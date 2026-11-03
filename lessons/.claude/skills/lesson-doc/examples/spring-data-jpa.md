# 1. Entités & mapping

- **Transient** : objet créé avec `new`, inconnu de JPA, aucune persistance automatique.
- **Managed** : sous contrôle de la session ; toute modification est détectée et persistée au flush (dirty checking).
- **Detached** : sorti de la session après fin de transaction ; modifications non suivies, relations `LAZY` inaccessibles.
- **`GenerationType.SEQUENCE`** recommandé plutôt que `IDENTITY` (PostgreSQL et H2 supportent les séquences) : avec `IDENTITY`, Hibernate ne peut pas batcher les `INSERT`.
- **Danger en production** : `ddl-auto=update` modifie le schéma automatiquement et peut supprimer des colonnes. Utiliser `validate` en prod et gérer les migrations avec Flyway ou Liquibase.

```plain text
# application.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/studentdb
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
```

```java
@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long id;

    @Column(name = "student_name", nullable = false, length = 100)
    private String name;

    @Column(nullable = false)
    private int marks;

    public Student() {} // requis par JPA/Hibernate : instanciation par réflexion sans appel de constructeur paramétré
}
```

# 2. JpaRepository, CRUD & suppression

- **`save(entity)`** : appelle `persist()` si l'entité est nouvelle (id null ou version null), `merge()` sinon.
- **Objet retourné** : toujours utiliser l'objet retourné par `save()` ; en cas de `merge()`, Hibernate retourne une nouvelle instance synchronisée, l'objet passé en paramètre peut ne pas avoir l'`id` généré.
- **`findById(id)`** : retourne `Optional<T>` ; toujours utiliser `orElseThrow()`, jamais `get()` directement.
- **`deleteById(id)`** : charge l'entité avant suppression pour déclencher les listeners JPA. Si les listeners ne sont pas nécessaires, préférer `@Modifying @Query` pour un DELETE direct sans SELECT préalable.
- **Piège `deleteAll()`** : charge toutes les entités avant suppression (N SELECT + N DELETE) ; pour un DELETE en masse performant, préférer `@Modifying @Query("DELETE FROM Student s")`.
- **`@Modifying`** : requis pour les `UPDATE` / `DELETE` dans `@Query`, avec `@Transactional`. Ajouter `clearAutomatically = true` : sans ça, le cache L1 Hibernate reste incohérent (les entités chargées en mémoire ne reflètent pas les modifications SQL directes).

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    @Modifying(clearAutomatically = true)
    @Transactional
    @Query("UPDATE Student s SET s.marks = :marks WHERE s.id = :id")
    int updateMarks(@Param("id") Long id, @Param("marks") int marks);

    @Modifying(clearAutomatically = true)
    @Transactional
    @Query("DELETE FROM Student s WHERE s.marks < :minMarks")
    int deleteByLowMarks(@Param("minMarks") int minMarks);
}
```

# 3. Relations JPA

- **`@OneToMany(mappedBy = "...")`** + **`@ManyToOne`** : relation bidirectionnelle ; la FK est toujours du côté `@ManyToOne`, `mappedBy` indique le champ propriétaire côté `@OneToMany`.
- **Piège** : `mappedBy` absent sur `@OneToMany` → JPA crée une table de jointure intermédiaire au lieu d'une simple colonne FK.
- `fetch = FetchType.LAZY` recommandé partout (`EAGER`, défaut de `@ManyToOne`, charge systématiquement même si inutile). Conséquence concrète : charger une liste de 100 commandes avec `@ManyToOne` EAGER vers `User` déclenche 100 jointures superflues même si seule la liste est affichée.
- **`LazyInitializationException`** : accéder à une collection `LAZY` après la fermeture de la session JPA (hors transaction) lève cette exception. Solutions : `JOIN FETCH`, `@EntityGraph`, ou DTO qui force le chargement dans la transaction.
- **Problème N+1** : 1 requête pour la liste + N requêtes individuelles pour chaque relation lazy chargée. Détecter avec `spring.jpa.show-sql=true` ; corriger avec `JOIN FETCH` dans `@Query` ou `@EntityGraph(attributePaths = "...")` (une seule requête SQL).
- **`@SQLRestriction`** : filtre automatique appliqué sur toutes les requêtes de l'entité.

```java
@Entity
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long id;

    @OneToMany(mappedBy = "order", cascade = CascadeType.PERSIST, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>(); // initialiser ici évite NullPointerException si on ajoute des items avant le premier save()
}

@Entity
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    private Order order;
}
```

```java
public interface OrderRepository extends JpaRepository<Order, Long> {

    // JOIN FETCH : une seule requête SQL avec jointure
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
    Optional<Order> findByIdWithItems(@Param("id") Long id);

    // Ou avec @EntityGraph
    @EntityGraph(attributePaths = "items")
    Optional<Order> findWithItemsById(Long id);
}
```

# 4. @Transactional

- **`@Transactional`** sur les méthodes de **service** : Spring génère un proxy AOP qui intercepte les appels et ouvre/ferme la transaction.
- Les méthodes de `JpaRepository` (`save()`, `findById()`...) sont déjà `@Transactional` individuellement. `@Transactional` sur le service crée une transaction englobante qui maintient la session JPA ouverte pour toute la durée de la méthode, indispensable pour accéder aux collections `LAZY` après un appel repository.
- Sans `@Transactional` sur le service : la session JPA se ferme après chaque appel repository ; accéder à une collection `LAZY` dans la même méthode de service lève `LazyInitializationException`.
- `propagation = Propagation.REQUIRED` (défaut) : rejoint la transaction existante ou en crée une nouvelle ; `REQUIRES_NEW` : démarre une transaction indépendante en suspendant l'existante.
- **`readOnly = true`** : Hibernate désactive le dirty checking, optimise les lectures ; certains drivers routent vers un read replica.
- Rollback automatique sur `RuntimeException` et `Error` ; les checked exceptions ne rollbackent pas par défaut (utiliser `rollbackFor = MyCheckedException.class`).
- `isolation` : ne s'applique qu'aux nouvelles transactions ; ignoré si une transaction existante est réutilisée.

```java
@Service
public class AccountService {

    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accountRepository.findById(fromId).orElseThrow();
        Account to = accountRepository.findById(toId).orElseThrow();
        from.debit(amount);
        to.credit(amount);
        // Commit automatique à la fin ; rollback sur RuntimeException
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(String action) {
        // Transaction indépendante : commit même si la transaction parente rollback
        auditRepository.save(new AuditLog(action));
    }
}
```

> ⚠️ Appel interne : `this.auditLog(...)` depuis la même classe contourne le proxy ; `@Transactional` ignoré. Injecter le service ou déplacer dans une autre classe.

# 5. Requêtes personnalisées

- **Query methods** : Spring dérive la requête du nom de la méthode (`findBy`, `countBy`, `existsBy`, `deleteBy` + propriétés, avec des mots-clés comme `Between`, `ContainingIgnoreCase`, `Top3`). Illisible au-delà de 2-3 critères : passer à `@Query`.
- **`@Query`** : JPQL, opère sur les entités (pas les tables). Paramètres nommés (`:param` + `@Param`) ou positionnels (`?1`).
- **Trade-off JPQL/natif** : JPQL est portable entre bases de données ; `@NativeQuery` (alternative dédiée à `@Query(nativeQuery = true)`) permet les fonctions spécifiques mais couple le code au dialecte (une migration MySQL → PostgreSQL peut casser les requêtes natives).

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    List<Student> findByNameContainingIgnoreCase(String keyword);
    List<Student> findTop3ByOrderByMarksDesc();

    @Query("SELECT s FROM Student s WHERE s.marks > :minMarks")
    List<Student> findAboveMarks(@Param("minMarks") int minMarks);

    @NativeQuery(
        value = "SELECT * FROM students WHERE student_name = ?1",
        countQuery = "SELECT count(*) FROM students WHERE student_name = ?1"
    )
    Page<Student> findByNameNative(String name, Pageable pageable);
}
```

# 6. Pagination & Scrolling

- **`Page<T>`** : déclenche une requête `COUNT(*)` supplémentaire pour fournir `totalElements`.
- **`Window<T>`** : alternative à `Page<T>` pour les grands datasets ; scrolling sans `COUNT(*)`.
- **Keyset scrolling** (`ScrollPosition.keyset()`) : reconstruit la position à partir du dernier élément via les index DB ; plus performant qu'offset sur de gros volumes.

```java
public interface StudentRepository extends JpaRepository<Student, Long> {
    Window<Student> findFirst10ByOrderByMarksDesc(ScrollPosition position);
}
```

```java
WindowIterator<Student> iterator = WindowIterator
    .of(pos -> repository.findFirst10ByOrderByMarksDesc(pos))
    .startingAt(ScrollPosition.keyset());
```