# 1. Introduction à Spring Data JPA

- **Spring Data JPA** simplifie l'accès aux données en réduisant le code boilerplate.
- Fournit des interfaces de repositories avec des méthodes CRUD prêtes à l'emploi.
- Génère automatiquement les requêtes SQL à partir des noms de méthodes.
- Basé sur **JPA** (Java Persistence API) et utilise **Hibernate** comme implémentation par défaut.
- Support des transactions, du lazy loading et de la gestion du cache.

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>
    <!-- Ou H2 pour tests -->
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

```plain text
# application.properties

# PostgreSQL
spring.datasource.url=jdbc:postgresql://localhost:5432/studentdb
spring.datasource.username=postgres
spring.datasource.password=password

# JPA/Hibernate
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

# 2. ORM & JPA

## ORM (Object-Relational Mapping)

- **ORM** est une technique pour mapper des objets Java vers des tables de base de données.
- Élimine l'impédance entre le monde objet et le monde relationnel.
- Permet de manipuler des objets Java au lieu d'écrire du SQL.
- Les frameworks ORM gèrent automatiquement les conversions et les relations.

## JPA (Java Persistence API)

- **JPA** est une **spécification** Java standard pour l'ORM.
- Définit les annotations et interfaces, pas l'implémentation.
- **Hibernate** est l'implémentation JPA la plus populaire.
- **Autres implémentations** : `EclipseLink`, `OpenJPA`.
- Spring Data JPA s'appuie sur JPA et ajoute une couche d'abstraction supplémentaire.
- **Transient** : objet créé avec `new`, inconnu de JPA, aucune persistance automatique.
- **Managed** : sous contrôle de la session ; toute modification est détectée et persistée au flush (dirty checking).
- **Detached** : sorti de la session après fin de transaction ; modifications non suivies, relations `LAZY` inaccessibles.

```plain text
┌─────────────────────────────────┐
│   Spring Data JPA               │ ← Couche Spring (repositories)
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   JPA (Specification)           │ ← API standard (@Entity, @Id...)
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Hibernate (Implementation)    │ ← Implémentation concrète
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   JDBC                          │ ← Accès bas niveau à la DB
└─────────────────────────────────┘
```

# 3. Entités et mapping JPA

## Entités JPA

- **`@Entity`** : marque une classe comme entité JPA (table en base).
- **`@Id`** : définit la clé primaire.
- **`@GeneratedValue`** : génère automatiquement la clé primaire.
- **`GenerationType.SEQUENCE`** recommandé en PostgreSQL plutôt que `IDENTITY` : permet les batch inserts (Hibernate alloue plusieurs IDs en une seule requête), contrairement à `IDENTITY` qui requiert un aller-retour DB par insert.
- `@Table` personnalise le nom de la table.
- `@Column` personnalise les propriétés des colonnes.
- Hibernate crée automatiquement la table au démarrage si `ddl-auto=update` ou `create`.
- **Danger en production** : `ddl-auto=update` modifie le schéma automatiquement et peut supprimer des colonnes. Utiliser `validate` en prod et gérer les migrations avec Flyway ou Liquibase.

```java
@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "student_name", nullable = false, length = 100)
    private String name;

    @Column(nullable = false)
    private int marks;

    public Student() {} // requis par JPA/Hibernate : instanciation par réflexion sans appel de constructeur paramétré

    public Student(String name, int marks) {
        this.name = name;
        this.marks = marks;
    }

    // getters, setters
}
```

## Repository

- Interface héritant de `JpaRepository<T, ID>`.
- **`T`** : type de l'entité, **`ID`** : type de la clé primaire.
- **`@Repository`** : optionnel sur l'interface, Spring détecte automatiquement les repositories via `@EnableJpaRepositories` (activé par `@SpringBootApplication`).

```java
@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {
    // Méthodes CRUD héritées automatiquement :
    // save(), findAll(), findById(), deleteById(), count(), etc.
}
```

## Insertion de données

```java
@Configuration
public class DataLoader {

    @Bean
    CommandLineRunner initDatabase(StudentRepository repository) {
        return args -> {
            repository.save(new Student("Alice", 85));
            repository.save(new Student("Bob", 90));
            repository.save(new Student("Charlie", 78));
        };
    }
}
```

# 4. JpaRepository et opérations CRUD

- **`JpaRepository<T, ID>`** : hérite de `ListCrudRepository`, `ListPagingAndSortingRepository` et `QueryByExampleExecutor` ; fournit toutes les opérations CRUD, pagination et Query by Example sans implémentation à écrire.
- **`save(entity)`** : appelle `persist()` si l'entité est nouvelle (id null ou version null), `merge()` sinon.
- **Objet retourné** : toujours utiliser l'objet retourné par `save()` ; en cas de `merge()`, Hibernate retourne une nouvelle instance synchronisée, l'objet passé en paramètre peut ne pas avoir l'`id` généré.
- **`saveAndFlush(entity)`** : force l'envoi immédiat du SQL à la DB sans attendre le flush automatique en fin de transaction ; utile dans les tests pour vérifier les contraintes DB immédiatement.
- **`findById(id)`** : retourne `Optional<T>` ; toujours utiliser `orElseThrow()`, jamais `get()` directement.
- **`deleteById(id)`** : charge l'entité avant suppression pour déclencher les listeners JPA. Si les listeners ne sont pas nécessaires, préférer `@Modifying @Query` pour un DELETE direct sans SELECT préalable.

```java
@Service
public class StudentService {

    private final StudentRepository repository;

    public StudentService(StudentRepository repository) {
        this.repository = repository;
    }

    public List<Student> getAll() {
        return repository.findAll();
    }

    public Student getById(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", id));
    }

    public Student create(Student student) {
        return repository.save(student);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}
```

# 5. Relations JPA

- **`@OneToMany(mappedBy = "...")`** + **`@ManyToOne`** : relation bidirectionnelle ; la FK est toujours du côté `@ManyToOne`, `mappedBy` indique le champ propriétaire côté `@OneToMany`.
- **Piège** : `mappedBy` absent sur `@OneToMany` → JPA crée une table de jointure intermédiaire au lieu d'une simple colonne FK.
- `cascade = CascadeType.PERSIST` ou `REMOVE` (standard JPA) ; `CascadeType.SAVE_UPDATE` et `DELETE` (Hibernate-specific) supprimés en Hibernate 7.
- `fetch = FetchType.LAZY` recommandé partout (`EAGER`, défaut de `@ManyToOne`, charge systématiquement même si inutile). Conséquence concrète : charger une liste de 100 commandes avec `@ManyToOne` EAGER vers `User` déclenche 100 jointures superflues même si seule la liste est affichée.
- **`LazyInitializationException`** : accéder à une collection `LAZY` après la fermeture de la session JPA (hors transaction) lève cette exception. Solutions : `JOIN FETCH`, `@EntityGraph`, ou DTO qui force le chargement dans la transaction.
- **Problème N+1** : 1 requête pour la liste + N requêtes individuelles pour chaque relation lazy chargée. Détecter avec `spring.jpa.show-sql=true`.
- **`JOIN FETCH`** dans `@Query` ou **`@EntityGraph(attributePaths = "...")`** : charge la relation en une seule requête SQL (solution au N+1).
- **`@SQLRestriction`** : filtre automatique appliqué sur toutes les requêtes de l'entité (remplace `@Where` supprimé Hibernate 7).

```java
@Entity
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "order", cascade = CascadeType.PERSIST, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>(); // initialiser ici évite NullPointerException si on ajoute des items avant le premier save()
}

@Entity
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
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

# 6. @Transactional

- **`@Transactional`** sur les méthodes de **service** : Spring génère un proxy AOP qui intercepte les appels et ouvre/ferme la transaction.
- Les méthodes de `JpaRepository` (`save()`, `findById()`...) sont déjà `@Transactional` individuellement. `@Transactional` sur le service crée une transaction englobante qui maintient la session JPA ouverte pour toute la durée de la méthode, indispensable pour accéder aux collections `LAZY` après un appel repository.
- Sans `@Transactional` sur le service : la session JPA se ferme après chaque appel repository ; accéder à une collection `LAZY` dans la même méthode de service lève `LazyInitializationException`.
- `propagation = Propagation.REQUIRED` (défaut) : rejoint la transaction existante ou en crée une nouvelle ; `REQUIRES_NEW` : démarre une transaction indépendante en suspendant l'existante.
- **`readOnly = true`** : Hibernate désactive le dirty checking, optimise les lectures ; certains drivers routent vers un read replica.
- **Dirty checking** : mécanisme par lequel Hibernate compare l'état actuel des entités managées à leur état initial pour détecter les modifications et générer automatiquement les `UPDATE` au flush.
- Rollback automatique sur `RuntimeException` et `Error` ; les checked exceptions ne rollbackent pas par défaut (utiliser `rollbackFor = MyCheckedException.class`).
- `isolation` : ne s'applique qu'aux nouvelles transactions ; ignoré si une transaction existante est réutilisée.

```java
@Service
public class AccountService {

    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accountRepository.findById(fromId).orElseThrow(...);
        Account to = accountRepository.findById(toId).orElseThrow(...);
        from.debit(amount);
        to.credit(amount);
        // Commit automatique à la fin ; rollback sur RuntimeException
    }

    @Transactional(readOnly = true)
    public List<Account> getAll() {
        return accountRepository.findAll();
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(String action) {
        // Transaction indépendante : commit même si la transaction parente rollback
        auditRepository.save(new AuditLog(action));
    }
}
```

> ⚠️ Appel interne : `this.auditLog(...)` depuis la même classe contourne le proxy ; `@Transactional` ignoré. Injecter le service ou déplacer dans une autre classe.

# 7. Requêtes personnalisées

## Query Methods (dérivées)

- Spring génère automatiquement les requêtes SQL à partir des noms de méthodes : convention `findBy`, `deleteBy`, `countBy`, `existsBy` + nom de propriété.
- Opérateurs : `And`, `Or`, `Between`, `LessThan`, `GreaterThan`, `Like`, `Containing`, `IgnoreCase`, `OrderBy`, `Top`.
- Limites : devient illisible pour des requêtes complexes ; préférer `@Query` au-delà de 2-3 critères.

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    List<Student> findByNameContainingIgnoreCase(String keyword);
    List<Student> findByMarksBetween(int min, int max);
    List<Student> findTop3ByOrderByMarksDesc();
    boolean existsByName(String name);
    long countByMarksGreaterThan(int marks);

    @Transactional
    void deleteByMarksLessThan(int marks);
}
```

## @Query (JPQL)

- **`@Query`** : requête JPQL ou SQL natif, opère sur les entités (pas les tables).
- Paramètres nommés (`:param` + `@Param`) ou positionnels (`?1`).
- Passer à `@NativeQuery` pour du SQL pur avec des fonctionnalités DB-spécifiques.
- **Trade-off JPQL/natif** : JPQL est portable entre bases de données ; `@NativeQuery` permet les fonctions spécifiques mais couple le code au dialecte (une migration MySQL → PostgreSQL peut casser les requêtes natives).

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    @Query("SELECT s FROM Student s WHERE s.marks > :minMarks")
    List<Student> findAboveMarks(@Param("minMarks") int minMarks);

    @Query("SELECT s FROM Student s WHERE s.marks BETWEEN :min AND :max")
    List<Student> findByMarksRange(@Param("min") int min, @Param("max") int max);

    @Query("SELECT AVG(s.marks) FROM Student s")
    Double getAverageMarks();
}
```

## @NativeQuery (Spring Data JPA 4.0)

- **`@NativeQuery`** : annotation dédiée pour les requêtes SQL natives (remplace `@Query(nativeQuery = true)`).
- Ajoute `sqlResultSetMapping`, `countQuery` pour la pagination, et support du retour `Map<String, Object>`.

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    @NativeQuery("SELECT * FROM students WHERE marks > ?1")
    List<Student> findTopStudents(int minMarks);

    @NativeQuery(
        value = "SELECT * FROM students WHERE name = ?1",
        countQuery = "SELECT count(*) FROM students WHERE name = ?1"
    )
    Page<Student> findByNameNative(String name, Pageable pageable);
}
```

# 8. Update & Delete

## Update

- **Pattern find-and-save** : `findById()` → modifier les champs → `save()` (merge Hibernate).
- **`@Modifying`** : requis pour les DML (`UPDATE`, `DELETE`) dans `@Query`, combiné avec `@Transactional` ; DELETE en masse sans charger les entités (plus performant que `deleteById()` en boucle).
- **`@Modifying(clearAutomatically = true)`** : recommandé pour les UPDATE/DELETE en masse ; sans ça, le cache L1 Hibernate reste incohérent (les entités chargées en mémoire ne reflètent pas les modifications SQL directes).

## Delete

- **`delete(entity)`** : supprime une instance managée ; **`deleteAll()`** : supprime toutes les entités.
- **Piège `deleteAll()`** : charge toutes les entités avant suppression (N SELECT + N DELETE) ; pour un DELETE en masse performant, préférer `@Modifying @Query("DELETE FROM Student s")`.

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    // Update avec JPQL
    @Modifying
    @Transactional
    @Query("UPDATE Student s SET s.marks = :marks WHERE s.id = :id")
    int updateMarks(@Param("id") Long id, @Param("marks") int marks);

    // Delete avec JPQL
    @Modifying
    @Transactional
    @Query("DELETE FROM Student s WHERE s.marks < :minMarks")
    int deleteByLowMarks(@Param("minMarks") int minMarks);
}
```

```java
@Service
public class StudentService {

    private final StudentRepository repository;

    public StudentService(StudentRepository repository) {
        this.repository = repository;
    }

    public Student updateStudent(Long id, Student updatedStudent) {
        Student student = repository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", id));

        student.setName(updatedStudent.getName());
        student.setMarks(updatedStudent.getMarks());

        return repository.save(student); // entité déjà managée : Hibernate générerait l'UPDATE automatiquement au flush ; appel explicite pour la clarté
    }

    // Delete
    public void deleteStudent(Long id) {
        repository.deleteById(id);
    }

    // Delete avec condition
    public int deleteFailingStudents() {
        return repository.deleteByLowMarks(50);
    }
}
```

# 9. Pagination, Tri & Scrolling

- **`Pageable`** : `PageRequest.of(page, size)` ou `PageRequest.of(page, size, Sort.by(...))`, passé en paramètre d'une query method ou `findAll()`.
- **`Page<T>`** : contient le contenu + métadonnées (`totalElements`, `totalPages`, `number`, `first`, `last`).
- `Sort.by("field").descending()` : tri combinable avec pagination via `PageRequest`.
- **`Window<T>`** (Spring Data JPA 4.0) : alternative à `Page<T>` pour les grands datasets ; scrolling keyset ou offset sans `COUNT(*)`.
- Keyset scrolling (`ScrollPosition.keyset()`) : reconstruit la position à partir du dernier élément via les index DB ; plus performant qu'offset sur de gros volumes.

## Pagination avec Page\<T\>

```java
public interface StudentRepository extends JpaRepository<Student, Long> {
    Page<Student> findByMarksGreaterThan(int marks, Pageable pageable);
}
```

```java
// page=0, size=10, tri par marks DESC
Pageable pageable = PageRequest.of(0, 10, Sort.by("marks").descending());
Page<Student> page = repository.findAll(pageable);
```

## Scrolling avec `Window<T>`

```java
public interface StudentRepository extends JpaRepository<Student, Long> {
    Window<Student> findFirst10ByOrderByMarksDesc(ScrollPosition position);
}
```

```java
// Keyset scrolling : efficace sur grands volumes
WindowIterator<Student> iterator = WindowIterator
    .of(pos -> repository.findFirst10ByOrderByMarksDesc(pos))
    .startingAt(ScrollPosition.keyset());

while (iterator.hasNext()) {
    Student student = iterator.next();
}
```