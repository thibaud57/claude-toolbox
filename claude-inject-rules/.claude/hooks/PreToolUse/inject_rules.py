#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
"""
Hook PreToolUse — injection des rules .claude/rules/**/*.md

Contourne le bug officiel #23478 : les rules avec frontmatter `paths:` / `globs:`
ne sont PAS injectees dans le contexte lors d'un Write/Edit/MultiEdit (elles
fonctionnent uniquement sur Read).

Racines multiples (monorepo) : les rules appartiennent a leur projet, pas au
dossier depuis lequel Claude est lance. Le hook remonte du fichier edite jusqu'au
cwd et collecte chaque dossier portant un .claude/rules/. Les patterns de chaque
racine sont matches contre le chemin du fichier relatif A CETTE racine, donc
`src/**/*.service.ts` dans packages/api/.claude/rules/ vise bien le src/ de
packages/api, quel que soit le cwd. Injection du plus general au plus specifique,
pour qu'une rule de package precise une rule de racine.

Dedupe globale par session : chaque rule est injectee au maximum 1 fois par
session, aligne sur le comportement du mecanisme natif de Claude Code sur Read.
La cle de cache est qualifiee par racine, sans quoi deux rules homonymes dans
deux packages (ex: fastapi/routing.md) se masqueraient mutuellement.
Cache dans ~/.claude/cache/.inject-rules-cache/<session_id>.json, TTL 24h.

Matching : les globs sont compiles en regex, ou `**/` vaut zero ou plusieurs
segments et `*` ne traverse jamais un `/`. Le prefixe du pattern est donc
respecte : `packages/web/src/**/*.ts` ne matche pas un fichier de packages/api.
Les accolades sont expansees (`src/**/*.{ts,tsx}`), pour s'aligner sur le
mecanisme natif. Casse ignoree sous Windows.

Debug : INJECT_RULES_DEBUG=1 trace le deroulement sur stderr (stdout reste
reserve au JSON attendu par Claude Code) et affiche la traceback en cas d'erreur.

Convention fail-open : toute erreur = exit 0 silencieux (ne jamais bloquer le tool).
"""

import functools
import json
import sys
import os
import re
import time
from pathlib import Path

# pyyaml est declare en dependance du script (PEP 723, en-tete ci-dessus) : uv le
# garantit a l'execution. Pas de garde ImportError, une absence doit echouer
# bruyamment plutot que de desactiver silencieusement toutes les rules.
import yaml

TOOLS_TO_INTERCEPT = {"Write", "Edit", "MultiEdit"}
CACHE_DIR = Path.home() / ".claude" / "cache" / ".inject-rules-cache"
CACHE_TTL_SECONDS = 24 * 3600  # 24h

DEBUG = os.environ.get("INJECT_RULES_DEBUG", "").strip().lower() not in ("", "0", "false", "no")
_REGEX_FLAGS = re.IGNORECASE if os.name == "nt" else 0


def dbg(message):
    # stderr : stdout est reserve au JSON de sortie.
    if DEBUG:
        print("[inject_rules] %s" % message, file=sys.stderr)


def norm_path(path):
    return os.path.normpath(path).replace("\\", "/").rstrip("/")


def is_under(child_norm, parent_norm):
    return child_norm.lower().startswith(parent_norm.lower() + "/")


def relative_to(child_norm, parent_norm):
    if is_under(child_norm, parent_norm):
        return child_norm[len(parent_norm) + 1:]
    return child_norm


def parse_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if not match:
        return None, content

    try:
        fm_dict = yaml.safe_load(match.group(1))
    except Exception:
        fm_dict = {}

    return (fm_dict if isinstance(fm_dict, dict) else {}), match.group(2)


def get_patterns(frontmatter):
    if not frontmatter:
        return []
    patterns = []
    for key in ("paths", "globs"):
        value = frontmatter.get(key)
        if isinstance(value, list):
            patterns.extend(str(p) for p in value if p)
        elif isinstance(value, str):
            patterns.append(value)
    return patterns


def expand_braces(pattern):
    """Expanse `a/{b,c}/d` en ['a/b/d', 'a/c/d']. Recursif, accolades imbriquees OK."""
    match = re.search(r"\{([^{}]*)\}", pattern)
    if not match:
        return [pattern]

    prefix = pattern[:match.start()]
    suffix = pattern[match.end():]
    expanded = []
    for option in match.group(1).split(","):
        expanded.extend(expand_braces(prefix + option.strip() + suffix))
    return expanded


@functools.lru_cache(maxsize=None)
def compile_glob(pattern):
    """
    Compile un glob en regex.

    `**/` vaut zero ou plusieurs segments, `**` seul traverse tout, `*` et `?`
    ne traversent jamais un `/`. Contrairement a fnmatch, le prefixe du pattern
    est donc pleinement respecte.
    """
    index, length = 0, len(pattern)
    parts = ["^"]
    while index < length:
        char = pattern[index]
        if char == "*":
            if pattern.startswith("**/", index):
                parts.append("(?:[^/]+/)*")
                index += 3
            elif pattern.startswith("**", index):
                parts.append(".*")
                index += 2
            else:
                parts.append("[^/]*")
                index += 1
        elif char == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(char))
            index += 1
    parts.append("$")
    return re.compile("".join(parts), _REGEX_FLAGS)


def glob_match(rel_path, pattern):
    """
    Match d'un chemin relatif contre un glob, accolades comprises.

    Semantique gitignore : un pattern sans `/` vise le nom de fichier a n'importe
    quelle profondeur (`*.model.ts` attrape src/a/b/user.model.ts), un pattern
    contenant un `/` est ancre a la racine de sa propre racine de rules.
    """
    pattern = pattern.replace("\\", "/")
    basename = rel_path.rsplit("/", 1)[-1]

    for variant in expand_braces(pattern):
        regex = compile_glob(variant)
        if regex.match(rel_path):
            return True

        # Pattern sans separateur : compare au nom de fichier seul
        if "/" not in variant and regex.match(basename):
            return True

        # `src/**` doit aussi designer le dossier `src` lui-meme
        if variant.endswith("/**") and rel_path.lower() == variant[:-3].lower():
            return True

    return False


def find_rules_roots(project_norm, file_norm):
    """
    Racines de rules applicables au fichier, du plus general au plus specifique.

    Retourne une liste de (root_norm, rules_dir, label), ou label est le chemin de
    la racine relatif au cwd ("." pour le cwd lui-meme), utilise comme prefixe de
    cle de cache et dans l'entete d'injection.

    On ne remonte jamais au-dessus du cwd : un fichier hors du projet ne recoit
    que les rules du cwd (comportement historique preserve).
    """
    if is_under(file_norm, project_norm):
        segments = relative_to(file_norm, project_norm).split("/")[:-1]
    else:
        segments = []

    roots = []
    for depth in range(len(segments) + 1):
        candidate = "/".join([project_norm, *segments[:depth]])
        rules_dir = os.path.join(candidate, ".claude", "rules")
        if os.path.isdir(rules_dir):
            label = "/".join(segments[:depth]) or "."
            roots.append((candidate, rules_dir, label))
            dbg("racine retenue : %s" % label)

    return roots


def session_cache_file(session_id):
    # session_id sert de nom de fichier : assaini par precaution.
    safe_id = re.sub(r"[^A-Za-z0-9_\-]", "_", session_id or "")[:128]
    return CACHE_DIR / ("%s.json" % safe_id) if safe_id else None


def load_session_cache(session_id):
    cache_file = session_cache_file(session_id)
    if not cache_file:
        return set()
    try:
        return set(json.loads(cache_file.read_text(encoding="utf-8")).get("injected_rules", []))
    except Exception:
        return set()


def save_session_cache(session_id, injected_rules):
    cache_file = session_cache_file(session_id)
    if not cache_file:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({"injected_rules": sorted(injected_rules)}), encoding="utf-8")
    except Exception:
        pass


def cleanup_old_sessions():
    now = time.time()
    for f in CACHE_DIR.glob("*.json"):
        try:
            if now - f.stat().st_mtime > CACHE_TTL_SECONDS:
                f.unlink()
        except OSError:
            pass


def collect_matches(roots, file_norm, already_injected):
    """Rules matchees et non encore injectees, du plus general au plus specifique."""
    matched = []
    for root_norm, rules_dir, label in roots:
        rel_path = relative_to(file_norm, root_norm)
        dbg("racine %s : chemin relatif = %s" % (label, rel_path))

        for rule_file in sorted(Path(rules_dir).rglob("*.md")):
            rel_rule = rule_file.relative_to(rules_dir).as_posix()
            cache_key = "%s::%s" % (label, rel_rule)
            if cache_key in already_injected:
                dbg("  deja injectee : %s" % cache_key)
                continue

            try:
                content = rule_file.read_text(encoding="utf-8")
            except Exception:
                dbg("  illisible : %s" % rule_file)
                continue

            frontmatter, body = parse_frontmatter(content)
            patterns = get_patterns(frontmatter)
            if not patterns:
                dbg("  sans paths, ignoree : %s" % rule_file.name)
                continue

            hit = next((p for p in patterns if glob_match(rel_path, p)), None)
            if hit:
                display = rel_rule if label == "." else "%s/.claude/rules/%s" % (label, rel_rule)
                matched.append((display, cache_key, body.strip()))
                dbg("  MATCH %s via %s" % (rel_rule, hit))
            else:
                dbg("  pas de match : %s" % rel_rule)

    return matched


def main():
    try:
        hook_data = json.load(sys.stdin)
        tool_name = hook_data.get("tool_name", "")
        dbg("tool = %s" % tool_name)

        if tool_name not in TOOLS_TO_INTERCEPT:
            dbg("tool non intercepte")
            return

        tool_input = hook_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        if not file_path:
            dbg("file_path absent")
            return

        project_dir = hook_data.get("cwd", "")
        if not project_dir:
            dbg("cwd absent")
            return

        session_id = hook_data.get("session_id", "")

        project_norm = norm_path(project_dir)
        file_norm = norm_path(file_path)
        dbg("cwd = %s" % project_norm)
        dbg("fichier = %s" % file_norm)

        roots = find_rules_roots(project_norm, file_norm)
        if not roots:
            dbg("aucune racine .claude/rules trouvee")
            return

        already_injected = load_session_cache(session_id)
        matched = collect_matches(roots, file_norm, already_injected)
        cleanup_old_sessions()

        if not matched:
            dbg("aucune rule a injecter")
            return

        display_path = relative_to(file_norm, project_norm)
        lines = [
            "# Rules applicables pour `%s`" % display_path,
            "",
            "_Injection via hook PreToolUse (bug Claude Code #23478). Dedupe globale par session._",
            "",
        ]
        for display, _cache_key, body in matched:
            lines.append("## Rule: `%s`" % display)
            lines.append("")
            lines.append(body)
            lines.append("")

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "\n".join(lines),
            }
        }
        print(json.dumps(output))
        dbg("%d rule(s) injectee(s)" % len(matched))

        already_injected.update(cache_key for _display, cache_key, _body in matched)
        save_session_cache(session_id, already_injected)

    except Exception:
        if DEBUG:
            import traceback
            traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
