from app.content._build import lesson, question, section

CONTENT = {
    "pg-setup": lesson(
        "PostgreSQL is a powerful open-source relational database. Install it, connect with the psql command-line client and create your first database.",
        [
            section(
                "Install and start PostgreSQL",
                "On Windows, use the installer from postgresql.org (it includes psql and pgAdmin), or run PostgreSQL in Docker, which you learned in the Docker course. The server listens on port 5432 by default, and clients such as psql, pgAdmin and your application connect to it.",
                r"""
                # Option A: Docker (no installer needed)
                docker run -d --name pg -e POSTGRES_PASSWORD=devpass -p 5432:5432 -v pgdata:/var/lib/postgresql/data postgres:16

                # Connect with psql inside the container
                docker exec -it pg psql -U postgres
                """,
                "shell",
            ),
            section(
                "Work in psql",
                "psql runs SQL statements, which end with `;`, and backslash meta-commands: `\\l` lists databases, `\\c name` connects to one, `\\dt` lists tables, `\\d table` describes a table and `\\q` quits. SQL keywords aren't case-sensitive, but writing them in capitals keeps queries readable.",
                r"""
                CREATE DATABASE learning;
                \c learning
                SELECT version();
                \dt
                \q
                """,
                "sql",
            ),
        ],
        [
            "PostgreSQL runs as a server; clients such as psql, pgAdmin and your app connect to it on port 5432.",
            "SQL statements end with `;`; psql meta-commands start with a backslash.",
            "Databases are isolated from each other; switch between them with `\\c`.",
        ],
        r"""
        -- In a terminal:  docker exec -it pg psql -U postgres
        CREATE DATABASE learning;
        \c learning
        SELECT current_database(), current_user, version();
        \dt
        -- "Did not find any relations." The database is empty, as expected.
        \q
        """,
        [
            question("What is PostgreSQL's default port?", ["3306", "5432", "8000", "1433"], 1,
                     "3306 is MySQL's default and 1433 is SQL Server's."),
            question("Which psql command lists the tables in the current database?", ["\\l", "\\dt", "SHOW TABLES;", "\\q"], 1,
                     "`\\l` lists databases; `SHOW TABLES` is MySQL syntax."),
            question("What ends a SQL statement in psql?", ["A new line", "A semicolon", "A full stop", "Nothing"], 1,
                     "psql keeps reading until it sees `;`, so a long query can span several lines."),
        ],
        "sql",
    ),
    "pg-tables": lesson(
        "Tables hold your data in typed columns. Good types and constraints stop bad data at the door, before it can cause bugs.",
        [
            section(
                "Data types",
                "Common types: `integer` and `bigint` for whole numbers, `numeric(10,2)` for money (exact, unlike floating point), `text` for strings, `boolean`, `date`, and `timestamptz` for points in time (stored as UTC and shown in your time zone). `GENERATED ALWAYS AS IDENTITY` creates auto-numbered primary keys.",
                r"""
                CREATE TABLE courses (
                    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    title      text NOT NULL,
                    price      numeric(10, 2) NOT NULL DEFAULT 0,
                    published  boolean NOT NULL DEFAULT false,
                    created_at timestamptz NOT NULL DEFAULT now()
                );
                """,
                "sql",
            ),
            section(
                "Constraints",
                "Constraints are rules the database enforces on every write: `NOT NULL`, `UNIQUE`, `CHECK (condition)`, `PRIMARY KEY` and `FOREIGN KEY`. They protect your data even when application code has a bug. Change existing tables with `ALTER TABLE`.",
                r"""
                ALTER TABLE courses ADD CONSTRAINT price_not_negative CHECK (price >= 0);

                INSERT INTO courses (title, price) VALUES ('SQL basics', -5);
                -- ERROR: new row for relation "courses" violates check constraint "price_not_negative"
                """,
                "sql",
            ),
        ],
        [
            "Use `numeric` for money and `timestamptz` for points in time.",
            "Identity columns generate primary keys for you.",
            "Constraints guard your data even when application code has bugs.",
        ],
        r"""
        CREATE TABLE students (
            id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            full_name  text NOT NULL,
            email      text NOT NULL UNIQUE,
            age        integer CHECK (age BETWEEN 13 AND 120),
            joined_at  timestamptz NOT NULL DEFAULT now()
        );

        INSERT INTO students (full_name, email, age) VALUES ('Ada Lovelace', 'ada@example.com', 36);

        INSERT INTO students (full_name, email, age) VALUES ('Copy Cat', 'ada@example.com', 30);
        -- ERROR: duplicate key value violates unique constraint "students_email_key"

        INSERT INTO students (full_name, email, age) VALUES ('Too Young', 'kid@example.com', 5);
        -- ERROR: new row for relation "students" violates check constraint "students_age_check"

        \d students
        """,
        [
            question("Which type should store prices?", ["real", "double precision", "numeric(10,2)", "text"], 2,
                     "numeric is exact; floating-point types store 0.1 + 0.2 as 0.30000000000000004."),
            question("What does `timestamptz` store?", ["A time without a date", "An absolute point in time, displayed in the session's time zone", "A string", "Only dates"], 1,
                     "It stores UTC internally and converts on display, which avoids time-zone bugs."),
            question("A CHECK constraint fails during an INSERT. What happens?", ["The row is saved with NULL", "The statement fails with an error and nothing is inserted", "A warning is logged", "The value is clamped"], 1,
                     "Constraints reject the whole statement, so invalid data never reaches the table."),
        ],
        "sql",
    ),
    "pg-select": lesson(
        "SELECT reads data. Filter rows with WHERE, sort them with ORDER BY and page through them with LIMIT and OFFSET.",
        [
            section(
                "Filter and sort",
                "Choose columns after SELECT, filter rows with WHERE (combine conditions with AND and OR) and sort with ORDER BY. `LIKE` matches patterns (`%` matches anything) and `ILIKE` does the same ignoring case; use `IN` for lists and `BETWEEN` for ranges. Test for missing values with `IS NULL`: `= NULL` never matches.",
                r"""
                SELECT full_name, email, joined_at
                FROM students
                WHERE email ILIKE '%@example.com'
                  AND age IS NOT NULL
                ORDER BY joined_at DESC
                LIMIT 5;
                """,
                "sql",
            ),
            section(
                "Expressions, aliases and paging",
                "Compute values in the SELECT list and name them with AS. `DISTINCT` removes duplicate rows. `LIMIT n OFFSET m` pages through results; on large tables, keyset paging (`WHERE id > last_seen_id ORDER BY id LIMIT n`) stays fast at any depth.",
                r"""
                SELECT full_name,
                       date_part('year', age(joined_at)) AS years_member,
                       upper(left(full_name, 1))         AS initial
                FROM students
                ORDER BY full_name
                LIMIT 10 OFFSET 20;          -- page 3, with 10 rows per page

                SELECT DISTINCT age FROM students ORDER BY age;
                """,
                "sql",
            ),
        ],
        [
            "WHERE filters rows, ORDER BY sorts them and LIMIT caps the result.",
            "Use `IS NULL`, never `= NULL`.",
            "Without ORDER BY, the order of rows isn't guaranteed.",
        ],
        r"""
        SELECT id, full_name, email, joined_at
        FROM students
        WHERE email LIKE '%@example.com'
        ORDER BY joined_at DESC, id DESC      -- id breaks ties between equal timestamps
        LIMIT 5;
        """,
        [
            question("What does `WHERE phone = NULL` return?", ["Rows with no phone", "No rows: a comparison with NULL is never true", "An error", "All rows"], 1,
                     "NULL means 'unknown', so `= NULL` is unknown too. Use `IS NULL`."),
            question("Which condition matches 'Ada', 'ada' and 'ADA'?", ["name = 'ada'", "name LIKE 'ada'", "name ILIKE 'ada'", "name IN ('ada')"], 2,
                     "ILIKE is PostgreSQL's case-insensitive LIKE."),
            question("Without ORDER BY, in which order are rows returned?", ["Insertion order", "Primary key order", "Any order; it isn't guaranteed", "Alphabetical order"], 2,
                     "The order can change between runs as the table and query plan change."),
        ],
        "sql",
    ),
    "pg-modify": lesson(
        "INSERT adds rows, UPDATE changes them and DELETE removes them. The WHERE clause decides which rows are touched, and RETURNING shows exactly what changed.",
        [
            section(
                "Insert and upsert",
                "Insert several rows in one statement. `ON CONFLICT` turns an insert into an 'upsert': update the existing row (or do nothing) when a unique key already exists. `RETURNING` gives back the affected rows, including generated values such as ids.",
                r"""
                INSERT INTO courses (title, price)
                VALUES ('Python Foundations', 0), ('Advanced SQL', 49.00)
                RETURNING id, title;

                -- An upsert needs a UNIQUE constraint on the conflict column(s)
                ALTER TABLE courses ADD CONSTRAINT courses_title_key UNIQUE (title);

                INSERT INTO courses (title, price) VALUES ('Advanced SQL', 39.00)
                ON CONFLICT (title) DO UPDATE SET price = EXCLUDED.price
                RETURNING id, title, price;
                """,
                "sql",
            ),
            section(
                "Update and delete",
                "An UPDATE or DELETE without WHERE changes every row in the table. Write the WHERE clause first, check it with a SELECT, and in psql consider wrapping risky changes in `BEGIN; ... ROLLBACK;` to preview them without keeping the result.",
                r"""
                UPDATE courses
                SET price = round(price * 1.10, 2)
                WHERE title = 'Advanced SQL'
                RETURNING id, title, price;

                DELETE FROM courses
                WHERE published = false AND created_at < now() - interval '1 year'
                RETURNING id, title;
                """,
                "sql",
            ),
        ],
        [
            "RETURNING shows the rows an INSERT, UPDATE or DELETE affected.",
            "`INSERT ... ON CONFLICT ... DO UPDATE` is an atomic upsert.",
            "Write the WHERE clause first: an UPDATE without one changes every row.",
        ],
        r"""
        INSERT INTO courses (title, price, published)
        VALUES ('SQL Basics', 19.00, true),
               ('Window Functions', 29.00, true),
               ('Old Draft', 9.00, false)
        RETURNING id, title, price;

        UPDATE courses
        SET price = round(price * 1.10, 2)
        WHERE title = 'Window Functions'
        RETURNING title, price;                 -- 31.90

        DELETE FROM courses
        WHERE title = 'Old Draft'
        RETURNING id, title;
        """,
        [
            question("What does `UPDATE courses SET price = 0;` do?", ["Updates the first row", "Sets the price of every row to 0", "Fails because there's no WHERE", "Nothing"], 1,
                     "Without WHERE, the update applies to the whole table."),
            question("What does RETURNING add to an INSERT?", ["A transaction", "The inserted rows' values, including generated ids", "A backup", "Validation"], 1,
                     "It saves a second query to find out what was just created."),
            question("In `ON CONFLICT (title) DO UPDATE SET price = EXCLUDED.price`, what is EXCLUDED?", ["The existing row", "The row you tried to insert", "Deleted rows", "A table you create"], 1,
                     "EXCLUDED holds the proposed row that conflicted, so you can copy its values."),
        ],
        "sql",
    ),
    "pg-aggregate": lesson(
        "Aggregate functions turn many rows into one value. GROUP BY computes them per group, and HAVING filters the groups.",
        [
            section(
                "Aggregates and GROUP BY",
                "`count`, `sum`, `avg`, `min` and `max` summarise rows. With GROUP BY you get one result row per group, and every selected column must be either grouped or aggregated. `count(*)` counts rows; `count(column)` skips NULLs.",
                r"""
                CREATE TABLE enrolments (
                    student_id  bigint NOT NULL,
                    course_id   bigint NOT NULL,
                    score       integer,
                    enrolled_on date NOT NULL DEFAULT current_date
                );

                SELECT course_id,
                       count(*)             AS students,
                       round(avg(score), 1) AS avg_score,
                       max(score)           AS best
                FROM enrolments
                GROUP BY course_id
                ORDER BY students DESC;
                """,
                "sql",
            ),
            section(
                "WHERE vs HAVING",
                "WHERE filters rows before grouping; HAVING filters groups after aggregation. `FILTER (WHERE ...)` computes an aggregate over only part of each group, so one query can return several metrics side by side.",
                r"""
                SELECT course_id,
                       count(*)                            AS students,
                       count(*) FILTER (WHERE score >= 50) AS passed
                FROM enrolments
                WHERE enrolled_on >= date '2026-01-01'
                GROUP BY course_id
                HAVING count(*) > 2;
                """,
                "sql",
            ),
        ],
        [
            "Every selected column is either in GROUP BY or inside an aggregate.",
            "WHERE filters rows; HAVING filters groups.",
            "`count(*)` counts rows; `count(column)` ignores NULLs.",
        ],
        r"""
        INSERT INTO enrolments (student_id, course_id, score) VALUES
            (1, 1, 80), (2, 1, 65), (3, 1, 90),
            (1, 2, 40), (2, 2, NULL);

        SELECT course_id,
               count(*)             AS students,
               count(score)         AS graded,
               round(avg(score), 2) AS avg_score
        FROM enrolments
        GROUP BY course_id
        HAVING count(*) > 2;
        -- course_id | students | graded | avg_score
        --         1 |        3 |      3 |     78.33
        """,
        [
            question("Which clause filters groups after aggregation?", ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 1,
                     "WHERE runs before grouping, so it can't use aggregates."),
            question("A column holds 5, NULL and 7. What are `count(*)` and `count(col)`?", ["3 and 3", "3 and 2", "2 and 2", "2 and 3"], 1,
                     "count(*) counts every row; count(col) skips the NULL."),
            question("What happens with `SELECT course_id, student_id, count(*) FROM enrolments GROUP BY course_id`?", ["It works", "An error: student_id must be grouped or aggregated", "student_id is NULL", "A random student is picked"], 1,
                     "Each group has many student_ids, so PostgreSQL can't choose one for you."),
        ],
        "sql",
    ),
    "pg-joins": lesson(
        "Joins combine rows from related tables. Choosing between INNER and LEFT joins decides whether rows without a match are kept.",
        [
            section(
                "INNER JOIN",
                "An INNER JOIN keeps only rows that match in both tables, according to the condition in ON. Short table aliases keep queries readable.",
                r"""
                SELECT s.full_name, c.title, e.score
                FROM enrolments AS e
                JOIN students   AS s ON s.id = e.student_id
                JOIN courses    AS c ON c.id = e.course_id
                ORDER BY s.full_name, c.title;
                """,
                "sql",
            ),
            section(
                "LEFT JOIN and finding missing rows",
                "A LEFT JOIN keeps every row from the left table and fills the right side with NULL when there's no match. Adding `WHERE right.id IS NULL` finds rows with no match at all (an 'anti-join'). Put conditions on the right-hand table in ON, not WHERE, or you silently turn the LEFT JOIN back into an INNER JOIN.",
                r"""
                -- Students with no enrolments
                SELECT s.full_name
                FROM students AS s
                LEFT JOIN enrolments AS e ON e.student_id = s.id
                WHERE e.student_id IS NULL;
                """,
                "sql",
            ),
        ],
        [
            "INNER JOIN keeps matches only; LEFT JOIN keeps every row from the left table.",
            "LEFT JOIN plus `IS NULL` finds rows without a match.",
            "Conditions on the right-hand table of a LEFT JOIN belong in ON.",
        ],
        r"""
        SELECT s.full_name,
               coalesce(string_agg(c.title, ', ' ORDER BY c.title), '(no courses)') AS courses
        FROM students AS s
        LEFT JOIN enrolments AS e ON e.student_id = s.id
        LEFT JOIN courses    AS c ON c.id = e.course_id
        GROUP BY s.id, s.full_name
        ORDER BY s.full_name;
        """,
        [
            question("A student has no enrolments. Does an INNER JOIN with enrolments return them?", ["Yes", "No; only a LEFT (or FULL) JOIN keeps rows without a match", "Yes, with NULLs", "Only with DISTINCT"], 1,
                     "INNER JOIN drops rows that have no partner on the other side."),
            question("What's wrong with `LEFT JOIN orders o ON o.customer_id = c.id WHERE o.status = 'paid'`?", ["A syntax error", "Customers without paid orders disappear, as if it were an INNER JOIN", "It's slow", "Nothing"], 1,
                     "For unmatched customers o.status is NULL, so WHERE removes them. Move the condition into ON."),
            question("How do you find customers who have never ordered?", ["INNER JOIN orders", "LEFT JOIN orders ... WHERE o.id IS NULL", "GROUP BY customer", "SELECT DISTINCT customers"], 1,
                     "NOT EXISTS (SELECT 1 FROM orders ...) is an equally good alternative."),
        ],
        "sql",
    ),
    "pg-schema-design": lesson(
        "A good schema stores each fact once and lets the database enforce relationships. Normalization, foreign keys and junction tables are the core tools.",
        [
            section(
                "Normalization",
                "Store each fact in one place. If a course title were copied into every enrolment row, renaming the course would mean updating many rows, and the copies could drift apart. Keep courses in their own table and refer to them by id. One-to-many relationships put a foreign key on the 'many' side; many-to-many relationships use a junction table.",
                r"""
                -- Repeated data (avoid):
                --   enrolments(student_name, student_email, course_title, course_price, score)
                -- Normalized:
                --   students(id, full_name, email)
                --   courses(id, title, price)
                --   enrolments(student_id -> students.id, course_id -> courses.id, score)
                """,
                "text",
            ),
            section(
                "Foreign keys and ON DELETE",
                "A foreign key guarantees that the referenced row exists. `ON DELETE CASCADE` deletes child rows along with their parent; the default (NO ACTION) and `RESTRICT` block the delete while children exist; `ON DELETE SET NULL` keeps the child but clears the link. PostgreSQL doesn't index foreign-key columns automatically, so add indexes yourself.",
                r"""
                CREATE TABLE lessons (
                    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    course_id bigint NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
                    title     text NOT NULL,
                    position  integer NOT NULL,
                    UNIQUE (course_id, position)
                );
                CREATE INDEX lessons_course_id_idx ON lessons (course_id);
                """,
                "sql",
            ),
        ],
        [
            "Store each fact once and refer to it by id.",
            "Many-to-many relationships need a junction table.",
            "Foreign keys enforce relationships; index their columns yourself.",
        ],
        r"""
        DROP TABLE IF EXISTS enrolments;

        CREATE TABLE enrolments (
            student_id  bigint NOT NULL REFERENCES students (id) ON DELETE CASCADE,
            course_id   bigint NOT NULL REFERENCES courses (id) ON DELETE RESTRICT,
            score       integer CHECK (score BETWEEN 0 AND 100),
            enrolled_on date NOT NULL DEFAULT current_date,
            PRIMARY KEY (student_id, course_id)
        );
        -- The primary key's index covers lookups by student_id; add one for course_id
        CREATE INDEX enrolments_course_id_idx ON enrolments (course_id);

        -- Deleting a student removes their enrolments.
        -- Deleting a course that still has students is blocked:
        DELETE FROM courses WHERE id = 1;
        -- ERROR: update or delete on table "courses" violates foreign key constraint ...
        """,
        [
            question("Students take many courses and courses have many students. How do you model that?", ["A course_ids array on students", "A junction table with two foreign keys", "One table for both", "A JSON column"], 1,
                     "The junction table (enrolments) can also hold facts about the relationship, such as the score."),
            question("What does `ON DELETE CASCADE` do?", ["Blocks the delete", "Deletes the child rows along with the parent", "Sets the children's foreign key to NULL", "Archives rows"], 1,
                     "Use it when children make no sense without their parent, such as a course's lessons."),
            question("Does PostgreSQL automatically index foreign-key columns?", ["Yes", "No; create the index yourself", "Only with CASCADE", "Only for primary keys"], 1,
                     "Primary keys and unique constraints get indexes; foreign-key columns don't."),
        ],
        "sql",
    ),
    "pg-ctes": lesson(
        "Subqueries and common table expressions (CTEs) break complex questions into readable steps. Recursive CTEs walk hierarchies such as category trees.",
        [
            section(
                "Subqueries and CTEs",
                "A subquery is a query inside another query. A CTE, written `WITH name AS (...)`, gives a step a name, so the query reads from top to bottom. Correlated subqueries refer to the outer row, and `EXISTS` checks whether any matching row exists.",
                r"""
                WITH course_avg AS (
                    SELECT course_id, avg(score) AS avg_score
                    FROM enrolments
                    GROUP BY course_id
                )
                SELECT s.full_name, e.course_id, e.score, round(ca.avg_score, 1) AS course_avg
                FROM enrolments AS e
                JOIN course_avg AS ca USING (course_id)
                JOIN students   AS s ON s.id = e.student_id
                WHERE e.score > ca.avg_score;
                """,
                "sql",
            ),
            section(
                "Recursive CTEs",
                "`WITH RECURSIVE` starts from anchor rows, then repeatedly joins to find the next level until no new rows appear. It's the standard way to query trees: categories, org charts and comment threads.",
                r"""
                CREATE TABLE categories (
                    id        integer PRIMARY KEY,
                    name      text NOT NULL,
                    parent_id integer REFERENCES categories (id)
                );
                INSERT INTO categories VALUES
                    (1, 'Programming', NULL), (2, 'Python', 1), (3, 'Web', 2), (4, 'FastAPI', 3);

                WITH RECURSIVE tree AS (
                    SELECT id, name, 1 AS depth FROM categories WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, t.depth + 1
                    FROM categories AS c
                    JOIN tree AS t ON c.parent_id = t.id
                )
                SELECT repeat('  ', depth - 1) || name AS outline FROM tree ORDER BY depth;
                """,
                "sql",
            ),
        ],
        [
            "CTEs name intermediate steps, so complex queries read from top to bottom.",
            "`EXISTS` asks 'is there at least one?' and stops at the first match.",
            "`WITH RECURSIVE` walks hierarchies of any depth.",
        ],
        r"""
        -- 1. Students who scored above their course's average
        WITH course_avg AS (
            SELECT course_id, avg(score) AS avg_score
            FROM enrolments
            WHERE score IS NOT NULL
            GROUP BY course_id
        )
        SELECT s.full_name, e.course_id, e.score
        FROM enrolments AS e
        JOIN course_avg AS ca USING (course_id)
        JOIN students   AS s ON s.id = e.student_id
        WHERE e.score > ca.avg_score
        ORDER BY e.course_id, e.score DESC;

        -- 2. Every category under 'Python', with its path
        WITH RECURSIVE tree AS (
            SELECT id, name, name::text AS path
            FROM categories WHERE name = 'Python'
            UNION ALL
            SELECT c.id, c.name, t.path || ' > ' || c.name
            FROM categories AS c
            JOIN tree AS t ON c.parent_id = t.id
        )
        SELECT path FROM tree;
        -- Python | Python > Web | Python > Web > FastAPI
        """,
        [
            question("What's the main benefit of a CTE?", ["It's always faster", "It names intermediate steps, making complex queries readable", "It creates a permanent table", "It locks rows"], 1,
                     "Since PostgreSQL 12, simple CTEs are usually inlined, so they perform like the equivalent subquery."),
            question("Which part of a recursive CTE runs first?", ["The recursive term", "The anchor query before UNION ALL", "Both at once", "The final SELECT"], 1,
                     "The anchor rows seed the recursion; the recursive term then runs until it adds no new rows."),
            question("What does `WHERE EXISTS (SELECT 1 FROM enrolments e WHERE e.student_id = s.id)` keep?", ["Students with at least one enrolment", "All students", "Students with no enrolments", "Only the first student"], 0,
                     "NOT EXISTS would keep the students with none."),
        ],
        "sql",
    ),
    "pg-window": lesson(
        "Window functions calculate across related rows without collapsing them: rankings, running totals and comparisons with the previous row.",
        [
            section(
                "Ranking within groups",
                "`OVER (PARTITION BY ... ORDER BY ...)` defines the window: which rows are related, and their order. `row_number()` numbers rows 1, 2, 3; `rank()` gives ties the same rank and skips the next one; `dense_rank()` doesn't skip. Unlike GROUP BY, every row stays in the result.",
                r"""
                SELECT course_id, student_id, score,
                       rank()       OVER (PARTITION BY course_id ORDER BY score DESC) AS rank,
                       dense_rank() OVER (PARTITION BY course_id ORDER BY score DESC) AS dense_rank
                FROM enrolments
                WHERE score IS NOT NULL;
                """,
                "sql",
            ),
            section(
                "Running totals and neighbours",
                "With ORDER BY in the window, `sum()` becomes a running total. `lag()` and `lead()` read the previous or next row, which is handy for day-over-day changes. Window functions can't appear in WHERE, so to keep the top N per group, rank in a CTE or subquery and filter outside it.",
                r"""
                WITH daily AS (
                    SELECT joined_at::date AS day, count(*) AS signups
                    FROM students
                    GROUP BY 1
                )
                SELECT day, signups,
                       sum(signups) OVER (ORDER BY day)           AS running_total,
                       signups - lag(signups) OVER (ORDER BY day) AS change
                FROM daily
                ORDER BY day;
                """,
                "sql",
            ),
        ],
        [
            "Window functions keep every row; GROUP BY collapses rows.",
            "PARTITION BY defines the groups; ORDER BY sets the order inside each one.",
            "Filter on a window function's result in an outer query, not in WHERE.",
        ],
        r"""
        -- Rank students within each course and keep the top three
        WITH ranked AS (
            SELECT s.full_name, e.course_id, e.score,
                   rank() OVER (PARTITION BY e.course_id ORDER BY e.score DESC) AS position
            FROM enrolments AS e
            JOIN students AS s ON s.id = e.student_id
            WHERE e.score IS NOT NULL
        )
        SELECT * FROM ranked WHERE position <= 3 ORDER BY course_id, position;

        -- Running total of daily signups
        SELECT joined_at::date AS day,
               count(*) AS signups,
               sum(count(*)) OVER (ORDER BY joined_at::date) AS running_total
        FROM students
        GROUP BY joined_at::date
        ORDER BY day;
        """,
        [
            question("Scores are 90, 90 and 80. What does `rank()` give?", ["1, 2, 3", "1, 1, 2", "1, 1, 3", "1, 2, 2"], 2,
                     "Ties share a rank and the next rank is skipped; dense_rank() would give 1, 1, 2."),
            question("How do you keep only the top three rows per course?", ["WHERE rank() <= 3", "Compute the rank in a CTE or subquery, then filter in the outer query", "LIMIT 3", "HAVING rank <= 3"], 1,
                     "Window functions are evaluated after WHERE, so you filter on them one level up."),
            question("What does `lag(signups) OVER (ORDER BY day)` return?", ["The next day's value", "The previous day's value", "The total", "The average"], 1,
                     "lead() returns the next row's value."),
        ],
        "sql",
    ),
    "pg-jsonb": lesson(
        "JSONB stores semi-structured data inside PostgreSQL, with operators to query it and GIN indexes to make those queries fast. Arrays store short lists of values.",
        [
            section(
                "Querying JSONB",
                "`->` returns a JSON value, `->>` returns it as text and `#>>` follows a path. `@>` tests containment: 'does this JSON include these keys and values?'. Use JSONB for data whose shape varies, and keep core, frequently filtered fields as regular columns.",
                r"""
                ALTER TABLE lessons ADD COLUMN meta jsonb NOT NULL DEFAULT '{}';

                UPDATE lessons
                SET meta = '{"level": "advanced", "tags": ["sql", "postgres"], "video": {"minutes": 12}}'
                WHERE id = 1;

                SELECT title,
                       meta ->> 'level'                  AS level,
                       (meta #>> '{video,minutes}')::int AS video_minutes
                FROM lessons
                WHERE meta @> '{"tags": ["sql"]}';
                """,
                "sql",
            ),
            section(
                "Indexes and arrays",
                "A GIN index makes `@>` and key-existence (`?`) queries fast. Update keys with `jsonb_set` or merge objects with `||`. Arrays such as `text[]` suit short lists like tags; search them with `= ANY (array)` or `@>`.",
                r"""
                CREATE INDEX lessons_meta_idx ON lessons USING gin (meta);

                UPDATE lessons SET meta = meta || '{"reviewed": true}' WHERE id = 1;

                ALTER TABLE courses ADD COLUMN tags text[] NOT NULL DEFAULT '{}';
                SELECT title FROM courses WHERE 'beginner' = ANY (tags);
                """,
                "sql",
            ),
        ],
        [
            "`->>` extracts text; `@>` tests containment.",
            "Index JSONB with GIN for containment and key-existence queries.",
            "Keep fields you filter, join or constrain on often as real columns.",
        ],
        r"""
        UPDATE lessons
        SET meta = jsonb_build_object(
            'level', 'beginner',
            'tags', jsonb_build_array('sql', 'select'),
            'video', jsonb_build_object('minutes', 9)
        )
        WHERE id = 2;

        SELECT title, meta #>> '{video,minutes}' AS video_minutes
        FROM lessons
        WHERE meta @> '{"level": "beginner"}';

        CREATE INDEX IF NOT EXISTS lessons_meta_idx ON lessons USING gin (meta);
        EXPLAIN SELECT title FROM lessons WHERE meta @> '{"level": "beginner"}';
        -- On a large table the plan shows a Bitmap Index Scan on lessons_meta_idx
        """,
        [
            question("What's the difference between `->` and `->>`?", ["None", "`->` returns JSON; `->>` returns text", "`->>` is only for arrays", "`->` is faster"], 1,
                     "Use `->>` when you want to compare or display the value as text."),
            question("Which index type speeds up `meta @> '{...}'` queries?", ["B-tree", "GIN", "Hash", "None can"], 1,
                     "GIN indexes every key and value inside the documents."),
            question("When should a field be a real column instead of a JSONB key?", ["Never", "When you filter, join or constrain on it often", "When it's text", "When it's optional"], 1,
                     "Columns get types, constraints, foreign keys and better planner statistics."),
        ],
        "sql",
    ),
    "pg-indexes": lesson(
        "Indexes let PostgreSQL find rows without reading the whole table. EXPLAIN ANALYZE shows how a query really runs, so you can prove an index helps.",
        [
            section(
                "Reading EXPLAIN ANALYZE",
                "`EXPLAIN` shows the plan; `EXPLAIN ANALYZE` also runs the query and reports real timings. A 'Seq Scan' reads every row; an 'Index Scan' or 'Bitmap Index Scan' uses an index. Compare the actual time and row counts before and after a change.",
                r"""
                CREATE TABLE events (
                    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    user_id    integer NOT NULL,
                    kind       text NOT NULL,
                    created_at timestamptz NOT NULL
                );

                INSERT INTO events (user_id, kind, created_at)
                SELECT (random() * 1000)::int,
                       (ARRAY['view', 'click', 'buy'])[1 + (random() * 2)::int],
                       now() - random() * interval '90 days'
                FROM generate_series(1, 100000);

                ANALYZE events;
                EXPLAIN ANALYZE SELECT * FROM events WHERE user_id = 42;   -- Seq Scan
                """,
                "sql",
            ),
            section(
                "Choosing indexes",
                "B-tree, the default, handles `=`, ranges and sorting. A multi-column index on `(user_id, created_at)` serves filters on user_id, or on user_id plus a time range, but not on created_at alone. Indexes speed up reads but slow down writes and use disk, so add them for real query patterns, not for every column.",
                r"""
                CREATE INDEX events_user_created_idx ON events (user_id, created_at);

                EXPLAIN ANALYZE
                SELECT * FROM events
                WHERE user_id = 42 AND created_at > now() - interval '7 days'
                ORDER BY created_at DESC;                                    -- Index Scan

                -- A partial index covers only the rows a frequent query needs
                CREATE INDEX events_buys_idx ON events (created_at) WHERE kind = 'buy';
                """,
                "sql",
            ),
        ],
        [
            "Use `EXPLAIN ANALYZE` to see the real plan and timings.",
            "Column order in a multi-column index matters: queries must filter on the leading columns.",
            "Every index costs write speed and storage, so index real query patterns.",
        ],
        r"""
        -- Uses the events table with 100,000 rows from the lesson
        EXPLAIN ANALYZE SELECT count(*) FROM events WHERE user_id = 42;
        -- Seq Scan on events ... Rows Removed by Filter: ~99,900 ... several milliseconds

        CREATE INDEX events_user_id_idx ON events (user_id);
        ANALYZE events;

        EXPLAIN ANALYZE SELECT count(*) FROM events WHERE user_id = 42;
        -- Index Only Scan or Bitmap Index Scan using events_user_id_idx ... well under a millisecond

        -- Why: without an index PostgreSQL must read all 100,000 rows. The B-tree index
        -- jumps straight to the roughly 100 rows for user 42.
        """,
        [
            question("What does 'Seq Scan' in a query plan mean?", ["It used an index", "It read every row of the table", "It sorted rows", "It ran in parallel"], 1,
                     "On small tables that's often the fastest plan; on large tables it's a sign an index may help."),
            question("An index on `(user_id, created_at)` helps which query most?", ["WHERE created_at > ...", "WHERE user_id = 42 AND created_at > ...", "WHERE kind = 'buy'", "ORDER BY kind"], 1,
                     "The index is sorted by user_id first, then created_at within each user."),
            question("What do many extra indexes cost?", ["Nothing", "Slower inserts and updates, and more disk space", "Slower SELECTs", "Data loss"], 1,
                     "Every write must also update every index on the table."),
        ],
        "sql",
    ),
    "pg-transactions": lesson(
        "A transaction makes several changes succeed or fail together. Isolation and locks stop concurrent users from corrupting each other's work.",
        [
            section(
                "BEGIN, COMMIT and ROLLBACK",
                "Statements between BEGIN and COMMIT are atomic: either all of them take effect or none do. If anything fails, the transaction is rolled back. PostgreSQL transactions are ACID: atomic, consistent, isolated and durable.",
                r"""
                CREATE TABLE accounts (
                    id      integer PRIMARY KEY,
                    owner   text NOT NULL,
                    credits integer NOT NULL CHECK (credits >= 0)
                );
                INSERT INTO accounts VALUES (1, 'Ada', 100), (2, 'Grace', 50);

                BEGIN;
                UPDATE accounts SET credits = credits - 30 WHERE id = 1;
                UPDATE accounts SET credits = credits + 30 WHERE id = 2;
                COMMIT;
                """,
                "sql",
            ),
            section(
                "Concurrency and locking",
                "Under the default isolation level, READ COMMITTED, each statement sees data committed before it started. To read a row and then update it safely, lock it with `SELECT ... FOR UPDATE`: a second transaction then waits instead of overwriting your change (a 'lost update'). Keep transactions short, because locks are held until COMMIT.",
                r"""
                BEGIN;
                SELECT credits FROM accounts WHERE id = 1 FOR UPDATE;   -- other writers to row 1 now wait
                UPDATE accounts SET credits = credits - 10 WHERE id = 1;
                COMMIT;                                                 -- the lock is released
                """,
                "sql",
            ),
        ],
        [
            "A transaction is all-or-nothing.",
            "Use `SELECT ... FOR UPDATE` to lock rows you're about to change.",
            "Keep transactions short to avoid blocking other users.",
        ],
        r"""
        -- Start from known balances
        TRUNCATE accounts;
        INSERT INTO accounts VALUES (1, 'Ada', 100), (2, 'Grace', 50);

        -- A successful transfer
        BEGIN;
        UPDATE accounts SET credits = credits - 30 WHERE id = 1;
        UPDATE accounts SET credits = credits + 30 WHERE id = 2;
        COMMIT;
        SELECT * FROM accounts ORDER BY id;     -- Ada 70, Grace 80

        -- A failing transfer: Ada doesn't have 500 credits
        BEGIN;
        UPDATE accounts SET credits = credits + 500 WHERE id = 2;   -- runs
        UPDATE accounts SET credits = credits - 500 WHERE id = 1;   -- ERROR: violates check constraint
        COMMIT;                                                       -- PostgreSQL replies ROLLBACK
        SELECT * FROM accounts ORDER BY id;     -- still Ada 70, Grace 80: nothing changed
        """,
        [
            question("The second UPDATE in a transaction fails. What happens to the first?", ["It stays", "It's undone when the transaction rolls back", "Half of it stays", "It's retried"], 1,
                     "Atomicity means the transaction succeeds or fails as a whole."),
            question("What does `SELECT ... FOR UPDATE` do?", ["Updates rows", "Locks the selected rows so other transactions wait to change them", "Speeds up the query", "Copies rows"], 1,
                     "It prevents lost updates in read-then-write logic."),
            question("What's PostgreSQL's default isolation level?", ["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"], 1,
                     "Each statement sees a fresh snapshot of committed data."),
        ],
        "sql",
    ),
    "pg-python": lesson(
        "Connect to PostgreSQL from Python with psycopg 3: pass values as parameters, let context managers handle transactions and reuse connections with a pool.",
        [
            section(
                "Connect and query safely",
                'Install the driver with `pip install "psycopg[binary]"`. Pass values as parameters (`%s` placeholders plus a tuple), never with f-strings, so they\'re sent separately from the SQL and can\'t inject anything. `with psycopg.connect(...) as conn` commits when the block succeeds, rolls back on an error and closes the connection.',
                r"""
                import os

                import psycopg
                from psycopg.rows import dict_row

                DSN = os.environ.get("DATABASE_URL", "postgresql://postgres:devpass@localhost:5432/learning")

                with psycopg.connect(DSN, row_factory=dict_row) as conn:
                    conn.execute(
                        "INSERT INTO courses (title, price) VALUES (%s, %s)",
                        ("PostgreSQL in Python", 25),
                    )
                    rows = conn.execute(
                        "SELECT id, title, price FROM courses WHERE price < %s ORDER BY id", (30,)
                    ).fetchall()
                    for row in rows:
                        print(row["id"], row["title"], row["price"])
                """,
            ),
            section(
                "Connection pools in FastAPI",
                "Opening a connection for every request is slow. `psycopg_pool.ConnectionPool` (install `psycopg-pool`) keeps a few connections open and lends them out. Open the pool in FastAPI's lifespan handler and borrow a connection in each endpoint.",
                r"""
                from contextlib import asynccontextmanager

                from fastapi import FastAPI
                from psycopg.rows import dict_row
                from psycopg_pool import ConnectionPool

                pool = ConnectionPool(DSN, min_size=1, max_size=5, open=False, kwargs={"row_factory": dict_row})


                @asynccontextmanager
                async def lifespan(app: FastAPI):
                    pool.open()
                    yield
                    pool.close()


                app = FastAPI(lifespan=lifespan)


                @app.get("/courses")
                def list_courses() -> list[dict]:
                    with pool.connection() as conn:
                        return conn.execute("SELECT id, title, price FROM courses ORDER BY id").fetchall()
                """,
            ),
        ],
        [
            "Use `%s` parameters; never format values into SQL strings.",
            "Connection context managers commit on success and roll back on errors.",
            "Use a connection pool in web applications.",
        ],
        r"""
        # tasks_pg.py - the tasks API from the FastAPI course, stored in PostgreSQL
        import os
        from contextlib import asynccontextmanager

        from fastapi import FastAPI, HTTPException
        from psycopg.rows import dict_row
        from psycopg_pool import ConnectionPool
        from pydantic import BaseModel

        DSN = os.environ.get("DATABASE_URL", "postgresql://postgres:devpass@localhost:5432/learning")
        pool = ConnectionPool(DSN, min_size=1, max_size=5, open=False, kwargs={"row_factory": dict_row})


        class TaskIn(BaseModel):
            title: str


        @asynccontextmanager
        async def lifespan(app: FastAPI):
            pool.open()
            with pool.connection() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS tasks ("
                    " id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,"
                    " title text NOT NULL,"
                    " done boolean NOT NULL DEFAULT false)"
                )
            yield
            pool.close()


        app = FastAPI(lifespan=lifespan)


        @app.post("/tasks", status_code=201)
        def create_task(data: TaskIn) -> dict:
            with pool.connection() as conn:
                return conn.execute(
                    "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done", (data.title,)
                ).fetchone()


        @app.get("/tasks/{task_id}")
        def read_task(task_id: int) -> dict:
            with pool.connection() as conn:
                task = conn.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)).fetchone()
            if task is None:
                raise HTTPException(404, "Task not found")
            return task
        """,
        [
            question("How do you pass a value into a query with psycopg?", ["An f-string", "A `%s` placeholder plus a tuple of parameters", "String concatenation", "`{}` with `.format()`"], 1,
                     "psycopg sends the parameters separately, so they can never change the SQL."),
            question("What happens at the end of `with psycopg.connect(dsn) as conn:` if no error occurred?", ["It rolls back", "It commits the transaction and closes the connection", "Nothing", "The connection stays open forever"], 1,
                     "On an exception it rolls back instead."),
            question("Why use a connection pool in a web API?", ["FastAPI requires it", "Opening a connection per request is slow; a pool reuses a few open ones", "For security", "To cache results"], 1,
                     "Each new PostgreSQL connection costs a server process and several milliseconds."),
        ],
    ),
    "pg-operations": lesson(
        "Running PostgreSQL for real means least-privilege roles, backups you have actually restored, and schema changes applied through migrations rather than by hand.",
        [
            section(
                "Roles and privileges",
                "Don't let your app connect as the `postgres` superuser. Create a role with a password and grant only what it needs: connecting, using the schema, and reading or writing specific tables. Then a bug or an injected query can't drop tables or read other databases.",
                r"""
                CREATE ROLE learning_app LOGIN PASSWORD 'change-me';
                GRANT CONNECT ON DATABASE learning TO learning_app;
                GRANT USAGE ON SCHEMA public TO learning_app;
                GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO learning_app;
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO learning_app;
                """,
                "sql",
            ),
            section(
                "Backups and migrations",
                "`pg_dump` writes a database to a file and `pg_restore` loads it back (use psql for plain-SQL dumps). A backup is only proven once you've restored it. Change schemas through migrations: numbered, versioned scripts applied in order by a tool such as Alembic or Flyway, so every environment ends up with the same schema.",
                r"""
                # Back up in the compressed custom format, then restore into a new database
                pg_dump -U postgres -Fc -f learning.dump learning
                createdb -U postgres learning_restore
                pg_restore -U postgres -d learning_restore learning.dump

                # With Docker: dump inside the container, then copy the file out
                docker exec pg pg_dump -U postgres -Fc -f /tmp/learning.dump learning
                docker cp pg:/tmp/learning.dump .
                """,
                "shell",
            ),
        ],
        [
            "Apps connect with a least-privilege role, never as a superuser.",
            "A backup you haven't restored isn't proven.",
            "Apply schema changes through versioned migrations.",
        ],
        r"""
        -- 1. A least-privilege role for the app
        CREATE ROLE learning_app LOGIN PASSWORD 'use-a-long-random-password';
        GRANT CONNECT ON DATABASE learning TO learning_app;
        GRANT USAGE ON SCHEMA public TO learning_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO learning_app;

        -- Check: connected as learning_app, this fails with "must be owner of table courses"
        -- DROP TABLE courses;

        -- 2. Backup and restore (run in a terminal):
        --   pg_dump -U postgres -Fc -f learning.dump learning
        --   createdb -U postgres learning_restore
        --   pg_restore -U postgres -d learning_restore learning.dump
        --   psql -U postgres -d learning_restore -c "SELECT count(*) FROM courses;"

        -- 3. A migration file, e.g. migrations/003_add_course_level.sql
        BEGIN;
        ALTER TABLE courses ADD COLUMN level text NOT NULL DEFAULT 'beginner'
            CHECK (level IN ('beginner', 'intermediate', 'advanced'));
        COMMIT;
        """,
        [
            question("Why shouldn't your app connect as the postgres superuser?", ["It's slower", "A bug or an injected query could do anything, including dropping databases", "Superusers can't insert rows", "Licensing"], 1,
                     "Least privilege limits the damage of any single mistake."),
            question("When is a backup proven to work?", ["When the file exists", "After you've successfully restored it", "When it's large", "After a week"], 1,
                     "Untested backups often turn out to be incomplete or unusable when you need them."),
            question("What is a migration?", ["Moving to a new server", "A versioned script that changes the schema, applied in order in every environment", "A backup", "An index"], 1,
                     "Migrations make schema changes repeatable, reviewable and reversible."),
        ],
        "sql",
    ),
}
