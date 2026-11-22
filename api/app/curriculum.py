COURSES = [
    {
        "id": "python",
        "title": "Python Foundations",
        "subtitle": "Learn the language by building useful programs.",
        "level": "Beginner",
        "modules": [
            {
                "title": "Getting started",
                "lessons": [
                    {
                        "id": "python-setup",
                        "title": "Install Python and run your first script",
                        "practice": "Create hello.py, run it from a terminal, and print your name.",
                        "minutes": 20,
                    },
                    {
                        "id": "python-variables",
                        "title": "Variables, values, and basic types",
                        "practice": "Store a book title, page count, and reading status; print a summary.",
                        "minutes": 25,
                    },
                ],
            },
            {
                "title": "Decisions and repetition",
                "lessons": [
                    {
                        "id": "python-conditionals",
                        "title": "Make decisions with if, elif, and else",
                        "practice": "Write a grade checker that handles invalid scores.",
                        "minutes": 30,
                    },
                    {
                        "id": "python-loops",
                        "title": "Repeat work with for and while loops",
                        "practice": "Build a number-guessing game with a limited number of turns.",
                        "minutes": 35,
                    },
                ],
            },
            {
                "title": "Functions and collections",
                "lessons": [
                    {
                        "id": "python-functions",
                        "title": "Write reusable functions",
                        "practice": "Refactor the grade checker into functions with clear inputs and outputs.",
                        "minutes": 35,
                    },
                    {
                        "id": "python-collections",
                        "title": "Work with lists, dictionaries, and sets",
                        "practice": "Build a small contact book with add, find, and list operations.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Real-world Python",
                "lessons": [
                    {
                        "id": "python-files-errors",
                        "title": "Read files and handle errors",
                        "practice": "Load a text file and report a helpful message when it is missing.",
                        "minutes": 40,
                    },
                    {
                        "id": "python-classes-tests",
                        "title": "Use classes, modules, and tests",
                        "practice": "Model a task list and write unit tests for adding and completing tasks.",
                        "minutes": 50,
                    },
                ],
            },
        ],
    },
    {
        "id": "dsa",
        "title": "Data Structures and Algorithms with Python",
        "subtitle": "Solve problems efficiently, from Big-O basics to dynamic programming.",
        "level": "Beginner to advanced",
        "modules": [
            {
                "title": "Thinking about efficiency",
                "lessons": [
                    {
                        "id": "dsa-big-o",
                        "title": "Measure and reason about Big-O complexity",
                        "practice": "Time three ways to find duplicates in a list with timeit, then explain the Big-O of each.",
                        "minutes": 35,
                    },
                    {
                        "id": "dsa-builtins",
                        "title": "Know the cost of lists, dicts, sets, and deques",
                        "practice": "Benchmark membership tests and front insertions on a list, a set, and a deque, and explain the results.",
                        "minutes": 35,
                    },
                ],
            },
            {
                "title": "Linear data structures",
                "lessons": [
                    {
                        "id": "dsa-arrays",
                        "title": "Solve array problems with two pointers and sliding windows",
                        "practice": "Find a pair with a target sum in a sorted list, then the longest substring without repeating characters.",
                        "minutes": 45,
                    },
                    {
                        "id": "dsa-stacks-queues",
                        "title": "Use stacks and queues",
                        "practice": "Check balanced brackets with a stack, and simulate a print queue with collections.deque.",
                        "minutes": 40,
                    },
                    {
                        "id": "dsa-linked-lists",
                        "title": "Build and manipulate linked lists",
                        "practice": "Implement a singly linked list with append, delete, and reverse, and write a test for each method.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "Recursion, searching, and sorting",
                "lessons": [
                    {
                        "id": "dsa-recursion",
                        "title": "Think recursively and backtrack",
                        "practice": "Generate every subset and permutation of a small list, then place 4 queens on a 4x4 board.",
                        "minutes": 50,
                    },
                    {
                        "id": "dsa-binary-search",
                        "title": "Search sorted data with binary search",
                        "practice": "Implement binary search, then find the first and last position of a value; test empty and one-item lists.",
                        "minutes": 40,
                    },
                    {
                        "id": "dsa-sorting",
                        "title": "Implement merge sort and quicksort",
                        "practice": "Write both sorts, compare their speed with sorted() on 10,000 random numbers, and note which are stable.",
                        "minutes": 55,
                    },
                ],
            },
            {
                "title": "Hashing, trees, and heaps",
                "lessons": [
                    {
                        "id": "dsa-hashing",
                        "title": "Solve problems with hash maps and sets",
                        "practice": "Solve two-sum, group anagrams, and find the first non-repeating character with dict and Counter.",
                        "minutes": 45,
                    },
                    {
                        "id": "dsa-trees",
                        "title": "Traverse binary trees and binary search trees",
                        "practice": "Build a binary search tree with insert and search, then write in-order and level-order traversals.",
                        "minutes": 55,
                    },
                    {
                        "id": "dsa-heaps",
                        "title": "Use heaps and priority queues",
                        "practice": "Keep the k largest numbers from a stream and merge k sorted lists with heapq.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Graphs",
                "lessons": [
                    {
                        "id": "dsa-graph-traversal",
                        "title": "Represent graphs and explore them with BFS and DFS",
                        "practice": "Count the islands in a grid with DFS, then find the shortest path through a maze with BFS.",
                        "minutes": 55,
                    },
                    {
                        "id": "dsa-shortest-paths",
                        "title": "Find weighted shortest paths with Dijkstra's algorithm",
                        "practice": "Compute the fastest travel time between cities from a weighted adjacency list using heapq.",
                        "minutes": 55,
                    },
                    {
                        "id": "dsa-topo-union-find",
                        "title": "Order tasks with topological sort and union-find",
                        "practice": "Decide whether a set of course prerequisites can be completed, and detect cycles with union-find.",
                        "minutes": 55,
                    },
                ],
            },
            {
                "title": "Advanced problem solving",
                "lessons": [
                    {
                        "id": "dsa-dynamic-programming",
                        "title": "Solve problems with dynamic programming",
                        "practice": "Solve coin change and longest common subsequence, first with memoization, then with a table.",
                        "minutes": 60,
                    },
                    {
                        "id": "dsa-greedy",
                        "title": "Apply greedy algorithms and interval patterns",
                        "practice": "Schedule the most non-overlapping meetings, merge overlapping intervals, and explain why greedy works.",
                        "minutes": 45,
                    },
                    {
                        "id": "dsa-tries-practice",
                        "title": "Build a trie and practice timed problem solving",
                        "practice": "Build a trie-based autocomplete, then solve three mixed problems in 60 minutes and review their complexity.",
                        "minutes": 75,
                    },
                ],
            },
        ],
    },
    {
        "id": "python-advanced",
        "title": "Advanced Python",
        "subtitle": "Write idiomatic, typed, concurrent, production-ready Python.",
        "level": "Advanced",
        "modules": [
            {
                "title": "Functions and iteration in depth",
                "lessons": [
                    {
                        "id": "pyadv-generators",
                        "title": "Build lazy pipelines with iterators and generators",
                        "practice": "Stream a large log file with generators, keep only error lines, and count them without loading the whole file.",
                        "minutes": 45,
                    },
                    {
                        "id": "pyadv-decorators",
                        "title": "Write decorators and closures",
                        "practice": "Write @timer and @retry(times=3) decorators that keep the wrapped function's name with functools.wraps.",
                        "minutes": 50,
                    },
                    {
                        "id": "pyadv-context-managers",
                        "title": "Manage resources with context managers",
                        "practice": "Write a timing context manager as a class and with contextlib, and check cleanup still runs after an exception.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Types and the data model",
                "lessons": [
                    {
                        "id": "pyadv-typing",
                        "title": "Use type hints, generics, and protocols with mypy",
                        "practice": "Type the task-list project, define a Protocol for its storage, and make mypy --strict pass.",
                        "minutes": 50,
                    },
                    {
                        "id": "pyadv-dataclasses",
                        "title": "Model data with dataclasses and enums",
                        "practice": "Rewrite the contact book with frozen dataclasses and an Enum for the contact type; compare equality and sorting.",
                        "minutes": 40,
                    },
                    {
                        "id": "pyadv-data-model",
                        "title": "Make classes feel built-in with special methods",
                        "practice": "Build a Vector class that supports +, ==, len(), iteration, and a helpful repr.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Concurrency and performance",
                "lessons": [
                    {
                        "id": "pyadv-asyncio",
                        "title": "Run concurrent I/O with asyncio",
                        "practice": "Fetch five URLs at once with httpx.AsyncClient and asyncio.gather, with a timeout on each request.",
                        "minutes": 55,
                    },
                    {
                        "id": "pyadv-threads-processes",
                        "title": "Choose threads or processes with concurrent.futures",
                        "practice": "Compare thread and process pools on a download task and a number-crunching task, and explain the GIL's role.",
                        "minutes": 50,
                    },
                    {
                        "id": "pyadv-performance",
                        "title": "Profile and optimize slow code",
                        "practice": "Profile a slow script with cProfile, speed up its slowest function, and cache a pure function with functools.cache.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Production-grade Python",
                "lessons": [
                    {
                        "id": "pyadv-packaging",
                        "title": "Package a project with pyproject.toml",
                        "practice": "Make the task list an installable package with a command-line entry point, and install it in a fresh virtual environment.",
                        "minutes": 50,
                    },
                    {
                        "id": "pyadv-testing",
                        "title": "Test in depth with fixtures, parametrize, and mocks",
                        "practice": "Test the task-list package with a temporary-file fixture, parametrized edge cases, and a mocked clock.",
                        "minutes": 55,
                    },
                    {
                        "id": "pyadv-logging-errors",
                        "title": "Design logging, configuration, and custom exceptions",
                        "practice": "Add logging, settings from environment variables, and a small custom exception hierarchy to the task-list CLI.",
                        "minutes": 45,
                    },
                ],
            },
        ],
    },
    {
        "id": "fastapi",
        "title": "FastAPI in Practice",
        "subtitle": "Turn Python skills into tested web APIs.",
        "level": "Beginner to intermediate",
        "modules": [
            {
                "title": "Your first API",
                "lessons": [
                    {
                        "id": "fastapi-first-app",
                        "title": "Create an app and explore interactive docs",
                        "practice": "Build a health endpoint and try it in Swagger UI at /docs.",
                        "minutes": 30,
                    },
                    {
                        "id": "fastapi-path-query",
                        "title": "Path parameters, query parameters, and responses",
                        "practice": "Add a searchable books endpoint with pagination parameters.",
                        "minutes": 35,
                    },
                ],
            },
            {
                "title": "Validate and structure data",
                "lessons": [
                    {
                        "id": "fastapi-pydantic",
                        "title": "Validate requests with Pydantic models",
                        "practice": "Create a request model that rejects empty task names.",
                        "minutes": 40,
                    },
                    {
                        "id": "fastapi-crud",
                        "title": "Build create, read, update, and delete routes",
                        "practice": "Implement an in-memory tasks API and verify each HTTP method.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "Persistence and dependencies",
                "lessons": [
                    {
                        "id": "fastapi-sqlite",
                        "title": "Persist data with SQLite",
                        "practice": "Move the tasks API to SQLite and confirm data survives a restart.",
                        "minutes": 55,
                    },
                    {
                        "id": "fastapi-dependencies",
                        "title": "Reuse logic with dependency injection",
                        "practice": "Provide a database session through a FastAPI dependency.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Reliable APIs",
                "lessons": [
                    {
                        "id": "fastapi-errors",
                        "title": "Handle errors, status codes, and configuration",
                        "practice": "Return useful 404 and 409 responses for task operations.",
                        "minutes": 35,
                    },
                    {
                        "id": "fastapi-testing",
                        "title": "Test endpoints and prepare a deployment",
                        "practice": "Write API tests with a temporary database and document startup steps.",
                        "minutes": 50,
                    },
                ],
            },
        ],
    },
    {
        "id": "backend",
        "title": "Server-Side Fundamentals",
        "subtitle": "How HTTP, APIs, authentication, security and production servers work.",
        "level": "Intermediate",
        "modules": [
            {
                "title": "HTTP and APIs",
                "lessons": [
                    {
                        "id": "be-http",
                        "title": "How HTTP works: requests, responses and status codes",
                        "practice": "Send requests to this app's API from Python, print the status codes and headers, and explain each status-code class.",
                        "minutes": 35,
                    },
                    {
                        "id": "be-rest",
                        "title": "Design clean REST APIs",
                        "practice": "Design versioned, paginated endpoints for a library API with one consistent error format.",
                        "minutes": 40,
                    },
                    {
                        "id": "be-browser-rules",
                        "title": "CORS, cookies and HTTP caching",
                        "practice": "Allow your frontend's origin with CORS and add an ETag so repeat requests get 304 Not Modified.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Authentication and security",
                "lessons": [
                    {
                        "id": "be-auth",
                        "title": "Authentication: passwords, sessions and tokens",
                        "practice": "Hash and verify passwords with scrypt, then issue and verify a signed token that expires.",
                        "minutes": 50,
                    },
                    {
                        "id": "be-authz",
                        "title": "Authorization, roles and OAuth 2.0",
                        "practice": "Let only admins delete orders, and let customers read only their own orders.",
                        "minutes": 45,
                    },
                    {
                        "id": "be-security",
                        "title": "Web security essentials: injection, XSS, CSRF and SSRF",
                        "practice": "Find and fix an SQL injection, an XSS bug and an SSRF bug in a small app.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "Servers in production",
                "lessons": [
                    {
                        "id": "be-concurrency",
                        "title": "Concurrency: processes, threads, async and the GIL",
                        "practice": "Time sequential and concurrent I/O with asyncio, then move a blocking call off the event loop.",
                        "minutes": 45,
                    },
                    {
                        "id": "be-observability",
                        "title": "Logging, metrics, tracing and health checks",
                        "practice": "Add middleware that logs each request as JSON with a request ID, status and duration.",
                        "minutes": 40,
                    },
                ],
            },
        ],
    },
    {
        "id": "postgres",
        "title": "PostgreSQL and SQL",
        "subtitle": "Store, query and protect data with the leading open-source database.",
        "level": "Beginner to advanced",
        "modules": [
            {
                "title": "Getting started",
                "lessons": [
                    {
                        "id": "pg-setup",
                        "title": "Install PostgreSQL and connect with psql",
                        "practice": "Start PostgreSQL (installer or Docker), connect with psql, create a database called learning and list its tables.",
                        "minutes": 30,
                    },
                    {
                        "id": "pg-tables",
                        "title": "Create tables with the right types and constraints",
                        "practice": "Create a students table with an identity primary key, a unique email and a CHECK on age, then try to insert invalid rows.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Querying data",
                "lessons": [
                    {
                        "id": "pg-select",
                        "title": "Query rows with SELECT, WHERE, ORDER BY and LIMIT",
                        "practice": "Find the five newest students whose email ends in @example.com, sorted by signup date.",
                        "minutes": 35,
                    },
                    {
                        "id": "pg-modify",
                        "title": "Insert, update and delete safely with RETURNING",
                        "practice": "Insert three courses, raise one course's price by 10%, delete another, and return the changed rows each time.",
                        "minutes": 35,
                    },
                    {
                        "id": "pg-aggregate",
                        "title": "Summarise data with GROUP BY and HAVING",
                        "practice": "Count enrolments and average scores per course, and keep only courses with more than two students.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Relationships",
                "lessons": [
                    {
                        "id": "pg-joins",
                        "title": "Combine tables with joins",
                        "practice": "List every student with their courses, including students who haven't enrolled in anything.",
                        "minutes": 45,
                    },
                    {
                        "id": "pg-schema-design",
                        "title": "Design a normalized schema with foreign keys",
                        "practice": "Model students, courses and enrolments (many-to-many) with foreign keys and sensible ON DELETE rules.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "Advanced SQL",
                "lessons": [
                    {
                        "id": "pg-ctes",
                        "title": "Break down queries with subqueries and CTEs",
                        "practice": "Find students who scored above their course's average with a CTE, then walk a category tree with WITH RECURSIVE.",
                        "minutes": 50,
                    },
                    {
                        "id": "pg-window",
                        "title": "Rank and compare rows with window functions",
                        "practice": "Rank students within each course by score, keep the top three, and compute a running total of daily signups.",
                        "minutes": 50,
                    },
                    {
                        "id": "pg-jsonb",
                        "title": "Store flexible data with JSONB and arrays",
                        "practice": "Store lesson metadata in a JSONB column, query a nested key and add a GIN index for containment queries.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Performance and reliability",
                "lessons": [
                    {
                        "id": "pg-indexes",
                        "title": "Speed up queries with indexes and EXPLAIN",
                        "practice": "Load 100,000 rows, compare EXPLAIN ANALYZE before and after adding an index, and explain the difference.",
                        "minutes": 55,
                    },
                    {
                        "id": "pg-transactions",
                        "title": "Keep data correct with transactions and locking",
                        "practice": "Transfer credits between two accounts in a transaction, then show that a failing statement leaves both balances unchanged.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "PostgreSQL in applications",
                "lessons": [
                    {
                        "id": "pg-python",
                        "title": "Use PostgreSQL from Python with psycopg",
                        "practice": "Connect with psycopg 3, run parameterized queries and move the FastAPI tasks API from SQLite to PostgreSQL.",
                        "minutes": 55,
                    },
                    {
                        "id": "pg-operations",
                        "title": "Run PostgreSQL in production: roles, backups and migrations",
                        "practice": "Create a least-privilege app role, back up with pg_dump, restore into a new database and write a migration.",
                        "minutes": 50,
                    },
                ],
            },
        ],
    },
    {
        "id": "mongodb",
        "title": "MongoDB and NoSQL",
        "subtitle": "Model, query and scale document data with MongoDB and Python.",
        "level": "Beginner to advanced",
        "modules": [
            {
                "title": "Getting started",
                "lessons": [
                    {
                        "id": "mongo-intro",
                        "title": "Documents, collections and running MongoDB",
                        "practice": "Start MongoDB in Docker, connect with mongosh and insert your first document.",
                        "minutes": 30,
                    },
                    {
                        "id": "mongo-crud",
                        "title": "Create, read, update and delete documents",
                        "practice": "Insert students, find them with filters, update them with $set and $inc, then delete one.",
                        "minutes": 40,
                    },
                    {
                        "id": "mongo-queries",
                        "title": "Query operators, arrays and embedded documents",
                        "practice": "Query courses by nested fields and array contents, with sorting and projection.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Modelling and performance",
                "lessons": [
                    {
                        "id": "mongo-modeling",
                        "title": "Model data: embed or reference",
                        "practice": "Design a blog schema (authors, posts, comments) and justify each embed-or-reference choice.",
                        "minutes": 45,
                    },
                    {
                        "id": "mongo-indexes",
                        "title": "Speed up queries with indexes and explain()",
                        "practice": "Index a slow query and compare the explain() output before and after.",
                        "minutes": 40,
                    },
                    {
                        "id": "mongo-aggregation",
                        "title": "Analyze data with the aggregation pipeline",
                        "practice": "Compute each course's average score and its top three students with one pipeline.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Applications and scale",
                "lessons": [
                    {
                        "id": "mongo-python",
                        "title": "Use MongoDB from Python with PyMongo",
                        "practice": "Write a StudentRepository class with create, get-by-id and search methods.",
                        "minutes": 45,
                    },
                    {
                        "id": "mongo-transactions",
                        "title": "Transactions, write concern and consistency",
                        "practice": "Move credits between two accounts atomically with a multi-document transaction.",
                        "minutes": 40,
                    },
                    {
                        "id": "mongo-scale",
                        "title": "Replica sets, sharding and production",
                        "practice": "Choose a shard key for an orders collection and explain the trade-offs.",
                        "minutes": 45,
                    },
                ],
            },
        ],
    },
    {
        "id": "typescript",
        "title": "TypeScript for Applications",
        "subtitle": "Build safer frontends that talk to your Python API.",
        "level": "Beginner",
        "modules": [
            {
                "title": "Language essentials",
                "lessons": [
                    {
                        "id": "ts-setup",
                        "title": "Set up TypeScript and compile your first file",
                        "practice": "Create a small script and run the TypeScript compiler in strict mode.",
                        "minutes": 25,
                    },
                    {
                        "id": "ts-types",
                        "title": "Understand primitives, arrays, and object types",
                        "practice": "Define typed course and lesson objects for a study planner.",
                        "minutes": 35,
                    },
                ],
            },
            {
                "title": "Model application data",
                "lessons": [
                    {
                        "id": "ts-unions",
                        "title": "Use unions, narrowing, and interfaces",
                        "practice": "Model loading, success, and error states without unsafe casts.",
                        "minutes": 40,
                    },
                    {
                        "id": "ts-functions",
                        "title": "Type functions, generics, and reusable helpers",
                        "practice": "Write a typed helper that groups lessons by module.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Web and API skills",
                "lessons": [
                    {
                        "id": "ts-dom",
                        "title": "Use the DOM safely from TypeScript",
                        "practice": "Render a list of lessons and respond to a button click.",
                        "minutes": 45,
                    },
                    {
                        "id": "ts-fetch",
                        "title": "Call an API with fetch and handle failures",
                        "practice": "Load tasks from your FastAPI service and display loading and error states.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Ship a frontend",
                "lessons": [
                    {
                        "id": "ts-async",
                        "title": "Work with promises and async/await",
                        "practice": "Submit a form and disable it while the API request is in progress.",
                        "minutes": 40,
                    },
                    {
                        "id": "ts-build",
                        "title": "Configure strict checks and build for production",
                        "practice": "Add a type-check command and fix all errors before creating a build.",
                        "minutes": 35,
                    },
                ],
            },
        ],
    },
    {
        "id": "docker",
        "title": "Docker for Developers",
        "subtitle": "Package, run, and ship your apps in containers.",
        "level": "Beginner to advanced",
        "modules": [
            {
                "title": "Container fundamentals",
                "lessons": [
                    {
                        "id": "docker-intro",
                        "title": "Understand containers and install Docker",
                        "practice": "Install Docker Desktop (with WSL 2 on Windows), run hello-world, and explain how a container differs from a VM.",
                        "minutes": 30,
                    },
                    {
                        "id": "docker-run",
                        "title": "Run and manage containers",
                        "practice": "Run nginx on port 8080, read its logs, open a shell in it with docker exec, then stop and remove it.",
                        "minutes": 35,
                    },
                    {
                        "id": "docker-images",
                        "title": "Work with images, tags, and registries",
                        "practice": "Pull two tags of the python image, compare their sizes, and inspect their layers with docker image history.",
                        "minutes": 30,
                    },
                ],
            },
            {
                "title": "Build your own images",
                "lessons": [
                    {
                        "id": "docker-dockerfile",
                        "title": "Write your first Dockerfile",
                        "practice": "Containerize the number-guessing game with FROM, WORKDIR, COPY, and CMD, and play it with docker run -it.",
                        "minutes": 40,
                    },
                    {
                        "id": "docker-layers",
                        "title": "Speed up builds with layers, caching, and .dockerignore",
                        "practice": "Reorder a Dockerfile so dependency installs are cached, add a .dockerignore, and measure the rebuild time.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Containerize a web app",
                "lessons": [
                    {
                        "id": "docker-fastapi",
                        "title": "Run a FastAPI app in a container",
                        "practice": "Containerize your FastAPI project, configure it with environment variables, publish its port, and add a HEALTHCHECK.",
                        "minutes": 50,
                    },
                    {
                        "id": "docker-volumes",
                        "title": "Persist data with volumes and bind mounts",
                        "practice": "Store the SQLite database in a named volume, recreate the container, and confirm the data survives.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Multi-container apps with Compose",
                "lessons": [
                    {
                        "id": "docker-compose",
                        "title": "Define multi-container apps with Docker Compose",
                        "practice": "Write a compose.yaml that runs your API with PostgreSQL, connecting them by service name.",
                        "minutes": 55,
                    },
                    {
                        "id": "docker-compose-dev",
                        "title": "Develop with Compose: health checks, networks, and live reload",
                        "practice": "Make the API wait for a healthy database, and reload code changes with a bind mount or compose watch.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "Production-ready containers",
                "lessons": [
                    {
                        "id": "docker-multistage",
                        "title": "Build small, secure images with multi-stage builds",
                        "practice": "Study this app's Dockerfile, then give your API a multi-stage build that runs as a non-root user; compare image sizes.",
                        "minutes": 50,
                    },
                    {
                        "id": "docker-security",
                        "title": "Handle secrets and scan images for vulnerabilities",
                        "practice": "Move secrets out of the image into runtime settings, then scan it with docker scout and fix one finding.",
                        "minutes": 45,
                    },
                    {
                        "id": "docker-ci-deploy",
                        "title": "Build in CI, push to a registry, and deploy",
                        "practice": "Build and push your image to GitHub Container Registry with GitHub Actions, then deploy it to a container host.",
                        "minutes": 60,
                    },
                ],
            },
        ],
    },
    {
        "id": "system-design",
        "title": "System Design",
        "subtitle": "Design scalable, reliable systems and explain the trade-offs.",
        "level": "Intermediate to advanced",
        "modules": [
            {
                "title": "Foundations",
                "lessons": [
                    {
                        "id": "sd-approach",
                        "title": "Approach a system design problem",
                        "practice": "Write the requirements and a one-page high-level design for a pastebin service.",
                        "minutes": 35,
                    },
                    {
                        "id": "sd-estimation",
                        "title": "Back-of-the-envelope estimates",
                        "practice": "Estimate requests per second, five-year storage and bandwidth for a photo-sharing app.",
                        "minutes": 35,
                    },
                ],
            },
            {
                "title": "Scaling the request path",
                "lessons": [
                    {
                        "id": "sd-load-balancing",
                        "title": "Scale out with load balancers",
                        "practice": "Simulate several balancing algorithms and compare their waiting times.",
                        "minutes": 40,
                    },
                    {
                        "id": "sd-caching",
                        "title": "Caching, eviction and CDNs",
                        "practice": "Implement an LRU cache with expiry and use it in a cache-aside lookup.",
                        "minutes": 45,
                    },
                    {
                        "id": "sd-rate-limiting",
                        "title": "Rate limiting and API gateways",
                        "practice": "Implement a token bucket and a sliding-window limiter and test them with a fake clock.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Data at scale",
                "lessons": [
                    {
                        "id": "sd-databases",
                        "title": "Replication, consistency and the CAP theorem",
                        "practice": "Route reads to replicas while keeping read-your-writes for users who just wrote.",
                        "minutes": 45,
                    },
                    {
                        "id": "sd-sharding",
                        "title": "Partitioning and consistent hashing",
                        "practice": "Build a hash ring with virtual nodes and measure how many keys move when a node is added.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Asynchronous and reliable systems",
                "lessons": [
                    {
                        "id": "sd-queues",
                        "title": "Message queues, events and idempotent consumers",
                        "practice": "Build a worker that applies each order once, even when messages are delivered twice.",
                        "minutes": 45,
                    },
                    {
                        "id": "sd-reliability",
                        "title": "Timeouts, retries, circuit breakers and SLOs",
                        "practice": "Wrap a flaky dependency with retries, exponential backoff with jitter and a circuit breaker.",
                        "minutes": 45,
                    },
                    {
                        "id": "sd-microservices",
                        "title": "Monoliths, microservices and sagas",
                        "practice": "Model an order saga (stock, payment, shipping) with compensating actions.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Case studies",
                "lessons": [
                    {
                        "id": "sd-url-shortener",
                        "title": "Design a URL shortener",
                        "practice": "Design a URL shortener and code its core: base62 codes, storage and a cache.",
                        "minutes": 50,
                    },
                    {
                        "id": "sd-news-feed",
                        "title": "Design a news feed",
                        "practice": "Build a hybrid feed: fan-out on write for most accounts, fan-out on read for celebrities.",
                        "minutes": 50,
                    },
                    {
                        "id": "sd-chat",
                        "title": "Design a chat system",
                        "practice": "Build an in-memory chat core with rooms, ordered message IDs and offline catch-up.",
                        "minutes": 50,
                    },
                ],
            },
        ],
    },
    {
        "id": "genai",
        "title": "Generative AI with Python",
        "subtitle": "Learn LLM fundamentals by building and evaluating features.",
        "level": "Intermediate",
        "modules": [
            {
                "title": "LLM foundations",
                "lessons": [
                    {
                        "id": "ai-llm-basics",
                        "title": "Understand tokens, context windows, and model APIs",
                        "practice": "Call a chat-completions API from a small Python script without exposing its key.",
                        "minutes": 40,
                    },
                    {
                        "id": "ai-prompts",
                        "title": "Write prompts with roles, constraints, and examples",
                        "practice": "Design a tutor prompt and compare its answers on three lesson questions.",
                        "minutes": 40,
                    },
                ],
            },
            {
                "title": "Useful AI features",
                "lessons": [
                    {
                        "id": "ai-structured",
                        "title": "Request structured output and validate it",
                        "practice": "Ask a model for a quiz question and validate the result with Pydantic.",
                        "minutes": 50,
                    },
                    {
                        "id": "ai-embeddings",
                        "title": "Explore embeddings and semantic search",
                        "practice": "Find the most relevant lesson for a learner's free-text question.",
                        "minutes": 55,
                    },
                ],
            },
            {
                "title": "Retrieval and quality",
                "lessons": [
                    {
                        "id": "ai-rag",
                        "title": "Build a small retrieval-augmented generation flow",
                        "practice": "Answer questions from your own lesson notes and cite the retrieved text.",
                        "minutes": 60,
                    },
                    {
                        "id": "ai-evaluations",
                        "title": "Evaluate answers, latency, and cost",
                        "practice": "Create a tiny evaluation set and compare two prompt versions.",
                        "minutes": 50,
                    },
                ],
            },
            {
                "title": "Responsible AI engineering",
                "lessons": [
                    {
                        "id": "ai-safety",
                        "title": "Add validation, privacy, and safety boundaries",
                        "practice": "Reject oversized inputs and ensure credentials never appear in responses.",
                        "minutes": 45,
                    },
                    {
                        "id": "ai-production",
                        "title": "Add retries, timeouts, and observability",
                        "practice": "Handle provider timeouts clearly and record latency without logging prompts.",
                        "minutes": 50,
                    },
                ],
            },
        ],
    },
    {
        "id": "agents-mcp",
        "title": "Agents and MCP",
        "subtitle": "Give AI assistants tools through clear, controlled interfaces.",
        "level": "Intermediate",
        "modules": [
            {
                "title": "Agent building blocks",
                "lessons": [
                    {
                        "id": "agent-tools",
                        "title": "Understand tools, schemas, and agent loops",
                        "practice": "Let a model choose between two read-only study-planner tools.",
                        "minutes": 45,
                    },
                    {
                        "id": "agent-control",
                        "title": "Limit tool access and validate every call",
                        "practice": "Add input validation and a tool allowlist to a toy agent.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Model Context Protocol",
                "lessons": [
                    {
                        "id": "mcp-concepts",
                        "title": "Learn MCP servers, clients, tools, and resources",
                        "practice": "Sketch which course actions belong in tools and which belong in resources.",
                        "minutes": 40,
                    },
                    {
                        "id": "mcp-server",
                        "title": "Create a local MCP server in Python",
                        "practice": "Expose a read-only course search tool and test it with an MCP client.",
                        "minutes": 60,
                    },
                ],
            },
            {
                "title": "Connect and verify tools",
                "lessons": [
                    {
                        "id": "mcp-client",
                        "title": "Connect an MCP client to the server",
                        "practice": "List available tools and call the course search tool locally.",
                        "minutes": 55,
                    },
                    {
                        "id": "mcp-security",
                        "title": "Apply least privilege and inspect tool inputs",
                        "practice": "Keep the server local and verify it cannot modify progress without approval.",
                        "minutes": 45,
                    },
                ],
            },
            {
                "title": "Capstone",
                "lessons": [
                    {
                        "id": "agent-capstone",
                        "title": "Build a study assistant with one approved tool",
                        "practice": "Combine a chat model, a course-search tool, and an evaluation checklist.",
                        "minutes": 75,
                    },
                    {
                        "id": "agent-reflection",
                        "title": "Review, test, and document your agent",
                        "practice": "Test normal and invalid tool calls and document what the agent cannot do.",
                        "minutes": 40,
                    },
                ],
            },
        ],
    },
]
