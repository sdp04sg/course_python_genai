from app.content._build import lesson, question, section

CONTENT = {
    "fastapi-first-app": lesson(
        "FastAPI turns type-hinted Python functions into a web API, with automatic validation and interactive documentation.",
        [
            section(
                "Your first app",
                'Install FastAPI with `pip install "fastapi[standard]"`, create `main.py`, and start the development server with `fastapi dev main.py` (or `uvicorn main:app --reload`). Each decorated function becomes an endpoint, and returning a dict sends JSON.',
                r"""
                from fastapi import FastAPI

                app = FastAPI(title="Study API")


                @app.get("/")
                def home() -> dict[str, str]:
                    return {"message": "Hello from FastAPI"}
                """,
            ),
            section(
                "Interactive docs",
                "FastAPI generates an OpenAPI description of your API. Open `http://127.0.0.1:8000/docs` for Swagger UI, where you can call every endpoint from the browser, or `/redoc` for reference-style docs. This learning app's own API docs are at `/docs` too.",
                r"""
                pip install "fastapi[standard]"
                fastapi dev main.py
                # In another terminal:
                curl http://127.0.0.1:8000/
                """,
                "powershell",
            ),
        ],
        [
            "A path operation is an HTTP-method decorator plus a function.",
            "Return dicts, lists or Pydantic models; FastAPI converts them to JSON.",
            "`/docs` lets you try every endpoint without writing a client.",
        ],
        r"""
        from datetime import datetime, timezone

        from fastapi import FastAPI

        app = FastAPI(title="Study API", version="0.1.0")


        @app.get("/health", tags=["system"])
        def health() -> dict[str, str]:
            return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

        # Run: fastapi dev main.py, open http://127.0.0.1:8000/docs,
        # expand GET /health, then click "Try it out" and "Execute".
        """,
        [
            question("Which URL shows FastAPI's interactive Swagger UI by default?", ["/swagger", "/docs", "/api", "/openapi"], 1,
                     "`/docs` serves Swagger UI and `/redoc` serves ReDoc; the raw schema is at `/openapi.json`."),
            question("What does FastAPI send when an endpoint returns a Python dict?", ["An HTML page", "A JSON response", "Plain text", "Nothing until you call json.dumps"], 1,
                     "FastAPI serializes the return value to JSON automatically."),
            question("What does `--reload` (or `fastapi dev`) do?", ["Restarts the server when code changes", "Clears the database", "Reloads the browser", "Enables HTTPS"], 0,
                     "It's for development only; don't use it in production."),
        ],
    ),
    "fastapi-path-query": lesson(
        "Path parameters identify a resource; query parameters filter, search and paginate. FastAPI validates both from your type hints.",
        [
            section(
                "Path parameters",
                "Put a parameter in the path with braces and declare it as a function argument. The type hint converts and validates it: for an `int` id, `/books/abc` gets an automatic 422 error.",
                r"""
                from fastapi import FastAPI, HTTPException

                app = FastAPI()
                BOOKS = {1: "Dune", 2: "Emma", 3: "Ulysses"}


                @app.get("/books/{book_id}")
                def get_book(book_id: int) -> dict:
                    if book_id not in BOOKS:
                        raise HTTPException(status_code=404, detail="Book not found")
                    return {"id": book_id, "title": BOOKS[book_id]}
                """,
            ),
            section(
                "Query parameters and limits",
                "Function arguments that aren't in the path become query parameters, as in `/books?search=du&limit=5`. Give them defaults to make them optional, and use `Query` to add rules such as minimum and maximum values.",
                r"""
                from typing import Annotated

                from fastapi import Query


                @app.get("/books")
                def list_books(
                    search: str | None = None,
                    skip: Annotated[int, Query(ge=0)] = 0,
                    limit: Annotated[int, Query(ge=1, le=50)] = 10,
                ) -> list[dict]:
                    items = [{"id": i, "title": t} for i, t in BOOKS.items()]
                    if search:
                        items = [b for b in items if search.lower() in b["title"].lower()]
                    return items[skip : skip + limit]
                """,
            ),
        ],
        [
            "Path parameters for identity (`/books/3`); query parameters for options (`?limit=10`).",
            "Type hints convert and validate; bad input gets a 422 response.",
            "Use `Query(ge=..., le=...)` to keep pagination within bounds.",
        ],
        r"""
        from typing import Annotated

        from fastapi import FastAPI, HTTPException, Query

        app = FastAPI()
        BOOKS = [
            {"id": 1, "title": "Dune", "year": 1965},
            {"id": 2, "title": "Emma", "year": 1815},
            {"id": 3, "title": "Dracula", "year": 1897},
        ]


        @app.get("/books")
        def search_books(
            q: str | None = None,
            page: Annotated[int, Query(ge=1)] = 1,
            size: Annotated[int, Query(ge=1, le=20)] = 2,
        ) -> dict:
            matches = [b for b in BOOKS if not q or q.lower() in b["title"].lower()]
            start = (page - 1) * size
            return {"total": len(matches), "page": page, "items": matches[start : start + size]}


        @app.get("/books/{book_id}")
        def get_book(book_id: int) -> dict:
            for book in BOOKS:
                if book["id"] == book_id:
                    return book
            raise HTTPException(status_code=404, detail="Book not found")

        # Try: /books?q=d&page=1&size=2   and   /books/99
        """,
        [
            question("In `GET /books/7?limit=5`, what is `limit`?", ["A path parameter", "A query parameter", "A header", "The request body"], 1,
                     "Everything after the `?` is the query string."),
            question("A route declares `book_id: int` and receives `/books/abc`. What happens?", ["book_id is 'abc'", "FastAPI returns a 422 validation error", "The server crashes", "book_id is 0"], 1,
                     "Validation happens before your function runs, so it never sees invalid input."),
            question("How do you make a query parameter optional?", ["Give it a default value", "Put it in the path", "Mark it with @optional", "You can't"], 0,
                     "Parameters without defaults are required; `None` is a common default."),
        ],
    ),
    "fastapi-pydantic": lesson(
        "Pydantic models describe the shape of the JSON your API accepts and returns. FastAPI validates every request against them before your code runs.",
        [
            section(
                "Request bodies",
                "Define a class that inherits from `BaseModel` and use it as a parameter type. FastAPI reads the JSON body, validates it and gives you a typed object, or responds with 422 and a precise error message.",
                r"""
                from fastapi import FastAPI
                from pydantic import BaseModel, Field

                app = FastAPI()


                class TaskCreate(BaseModel):
                    title: str = Field(min_length=1, max_length=100)
                    priority: int = Field(default=3, ge=1, le=5)


                @app.post("/tasks")
                def create_task(task: TaskCreate) -> dict:
                    return {"created": task.title, "priority": task.priority}
                """,
            ),
            section(
                "Response models and custom rules",
                "Use separate input and output models, so clients can't set server-owned fields such as `id`. Use `field_validator` for rules that `Field` can't express, such as rejecting titles that contain only spaces.",
                r"""
                from pydantic import BaseModel, field_validator


                class TaskIn(BaseModel):
                    title: str

                    @field_validator("title")
                    @classmethod
                    def not_blank(cls, value: str) -> str:
                        value = value.strip()
                        if not value:
                            raise ValueError("title must not be blank")
                        return value


                class TaskOut(BaseModel):
                    id: int
                    title: str
                    done: bool = False
                """,
            ),
        ],
        [
            "A BaseModel parameter means 'read and validate the JSON body'.",
            "Invalid input never reaches your function; the client gets a 422 with details.",
            "Use separate models for input and output.",
        ],
        r"""
        from fastapi import FastAPI
        from pydantic import BaseModel, Field, field_validator

        app = FastAPI()


        class TaskCreate(BaseModel):
            name: str = Field(max_length=80)

            @field_validator("name")
            @classmethod
            def reject_empty(cls, value: str) -> str:
                if not value.strip():
                    raise ValueError("Task name can't be empty")
                return value.strip()


        class Task(TaskCreate):
            id: int
            done: bool = False


        tasks: list[Task] = []


        @app.post("/tasks", status_code=201)
        def add_task(payload: TaskCreate) -> Task:
            task = Task(id=len(tasks) + 1, name=payload.name)
            tasks.append(task)
            return task

        # POST {"name": "   "}  ->  422 with "Task name can't be empty"
        """,
        [
            question("What status code does FastAPI return when a JSON body fails validation?", ["400", "404", "422", "500"], 2,
                     "422 Unprocessable Content, with details about every failing field."),
            question("Why use separate input and output models?", ["Pydantic requires it", "So clients can't set server-owned fields like id, and responses can add fields", "It's faster", "For HTTPS"], 1,
                     "Input models describe what clients may send; output models describe what you promise to return."),
            question("What does `Field(ge=1, le=5)` mean?", ["Between 1 and 5, inclusive", "A length of 1 to 5", "Exactly 1 or 5", "Greater than 5"], 0,
                     "`ge` is 'greater than or equal' and `le` is 'less than or equal'."),
        ],
    ),
    "fastapi-crud": lesson(
        "CRUD maps naturally onto HTTP: POST creates, GET reads, PUT or PATCH updates and DELETE removes. Choose the right method and status code for each.",
        [
            section(
                "Methods and status codes",
                "Use POST with 201 Created for new items, GET with 200 to read, PUT to replace an item or PATCH to change some of its fields, and DELETE with 204 No Content. Return 404 when the item doesn't exist.",
                r"""
                from fastapi import FastAPI, HTTPException, Response
                from pydantic import BaseModel

                app = FastAPI()


                class TaskIn(BaseModel):
                    title: str
                    done: bool = False


                class Task(TaskIn):
                    id: int


                tasks: dict[int, Task] = {}
                """,
            ),
            section(
                "The routes",
                "Keep each route small: validate, change the data, return the result. An in-memory dict is fine for learning; the next lesson swaps it for SQLite.",
                r"""
                @app.post("/tasks", status_code=201)
                def create(data: TaskIn) -> Task:
                    task = Task(id=max(tasks, default=0) + 1, **data.model_dump())
                    tasks[task.id] = task
                    return task


                @app.get("/tasks/{task_id}")
                def read(task_id: int) -> Task:
                    if task_id not in tasks:
                        raise HTTPException(404, "Task not found")
                    return tasks[task_id]


                @app.delete("/tasks/{task_id}", status_code=204)
                def delete(task_id: int) -> Response:
                    if tasks.pop(task_id, None) is None:
                        raise HTTPException(404, "Task not found")
                    return Response(status_code=204)
                """,
            ),
        ],
        [
            "POST → 201, GET → 200, PUT/PATCH → 200, DELETE → 204.",
            "Return 404 for missing items instead of returning None.",
            "`model_dump()` turns a Pydantic model into a dict.",
        ],
        r"""
        from fastapi import FastAPI, HTTPException, Response
        from pydantic import BaseModel

        app = FastAPI()


        class TaskIn(BaseModel):
            title: str
            done: bool = False


        class TaskPatch(BaseModel):
            title: str | None = None
            done: bool | None = None


        class Task(TaskIn):
            id: int


        tasks: dict[int, Task] = {}


        def get_or_404(task_id: int) -> Task:
            if task_id not in tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            return tasks[task_id]


        @app.post("/tasks", status_code=201)
        def create_task(data: TaskIn) -> Task:
            task = Task(id=max(tasks, default=0) + 1, **data.model_dump())
            tasks[task.id] = task
            return task


        @app.get("/tasks")
        def list_tasks() -> list[Task]:
            return list(tasks.values())


        @app.get("/tasks/{task_id}")
        def read_task(task_id: int) -> Task:
            return get_or_404(task_id)


        @app.put("/tasks/{task_id}")
        def replace_task(task_id: int, data: TaskIn) -> Task:
            get_or_404(task_id)
            tasks[task_id] = Task(id=task_id, **data.model_dump())
            return tasks[task_id]


        @app.patch("/tasks/{task_id}")
        def update_task(task_id: int, data: TaskPatch) -> Task:
            task = get_or_404(task_id)
            updated = task.model_copy(update=data.model_dump(exclude_unset=True))
            tasks[task_id] = updated
            return updated


        @app.delete("/tasks/{task_id}", status_code=204)
        def delete_task(task_id: int) -> Response:
            get_or_404(task_id)
            del tasks[task_id]
            return Response(status_code=204)

        # Verify each method in /docs: create, list, read, replace, patch, delete, then read -> 404.
        """,
        [
            question("Which status code fits a successful DELETE with no response body?", ["200", "201", "204", "404"], 2,
                     "204 No Content tells the client it worked and there's nothing to read."),
            question("What's the difference between PUT and PATCH?", ["None", "PUT replaces the whole resource; PATCH changes only the fields sent", "PATCH creates resources", "PUT deletes resources"], 1,
                     "A PUT without a field resets it to its default; a PATCH leaves unsent fields unchanged."),
            question("What does `model_dump(exclude_unset=True)` return?", ["All fields", "Only the fields the client actually sent", "Only required fields", "JSON text"], 1,
                     "That's exactly what a PATCH handler needs to merge into the existing item."),
        ],
    ),
    "fastapi-sqlite": lesson(
        "Store data in SQLite so it survives restarts. Python's built-in sqlite3 module needs no separate server, which makes it ideal for small apps. This learning app stores your progress in SQLite.",
        [
            section(
                "Connect, create and query",
                "Open a connection with `sqlite3.connect(path)`, create tables with `CREATE TABLE IF NOT EXISTS`, and always pass values through `?` placeholders, never f-strings, to prevent SQL injection. Using a connection in a `with` block commits on success and rolls back on error (it doesn't close the connection).",
                r"""
                import sqlite3

                DB = "tasks.db"


                def init_db() -> None:
                    with sqlite3.connect(DB) as conn:
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS tasks ("
                            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            " title TEXT NOT NULL,"
                            " done INTEGER NOT NULL DEFAULT 0)"
                        )


                def add_task(title: str) -> int:
                    with sqlite3.connect(DB) as conn:
                        cursor = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
                        return cursor.lastrowid
                """,
            ),
            section(
                "Use it from FastAPI",
                "Create the table when the app starts, using FastAPI's lifespan handler, and set `row_factory = sqlite3.Row` so rows behave like dicts.",
                r"""
                from contextlib import asynccontextmanager

                from fastapi import FastAPI


                @asynccontextmanager
                async def lifespan(app: FastAPI):
                    init_db()
                    yield


                app = FastAPI(lifespan=lifespan)


                @app.get("/tasks")
                def list_tasks() -> list[dict]:
                    with sqlite3.connect(DB) as conn:
                        conn.row_factory = sqlite3.Row
                        rows = conn.execute("SELECT id, title, done FROM tasks").fetchall()
                    return [{**dict(row), "done": bool(row["done"])} for row in rows]
                """,
            ),
        ],
        [
            "Always use `?` placeholders; never build SQL with f-strings.",
            "`with connection:` commits on success and rolls back on errors.",
            "Create tables at startup with `CREATE TABLE IF NOT EXISTS`.",
        ],
        r"""
        import sqlite3
        from contextlib import asynccontextmanager

        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel

        DB = "tasks.db"


        class TaskIn(BaseModel):
            title: str


        def connect() -> sqlite3.Connection:
            conn = sqlite3.connect(DB)
            conn.row_factory = sqlite3.Row
            return conn


        @asynccontextmanager
        async def lifespan(app: FastAPI):
            with connect() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS tasks "
                    "(id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER DEFAULT 0)"
                )
            yield


        app = FastAPI(lifespan=lifespan)


        @app.post("/tasks", status_code=201)
        def create_task(data: TaskIn) -> dict:
            with connect() as conn:
                cursor = conn.execute("INSERT INTO tasks (title) VALUES (?)", (data.title,))
            return {"id": cursor.lastrowid, "title": data.title, "done": False}


        @app.get("/tasks/{task_id}")
        def read_task(task_id: int) -> dict:
            with connect() as conn:
                row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Task not found")
            return {**dict(row), "done": bool(row["done"])}

        # Create a task, stop the server with Ctrl+C, start it again: GET /tasks/1 still works.
        """,
        [
            question("Why must you pass values with `?` placeholders instead of putting them into SQL with an f-string?", ["Placeholders are faster to type", "They prevent SQL injection by sending values separately from the SQL", "f-strings don't work with sqlite3", "SQLite requires them for numbers"], 1,
                     "With an f-string, a value like `'); DROP TABLE tasks; --` becomes part of the SQL."),
            question("What does `with sqlite3.connect(path) as conn:` do at the end of the block?", ["Closes the connection", "Commits on success, or rolls back on an error", "Deletes the database", "Nothing"], 1,
                     "The connection's context manager handles the transaction; call `close()` separately when you're done with it."),
            question("Where should a FastAPI app create its tables?", ["In every request", "At startup, for example in the lifespan handler", "In the browser", "Only by hand"], 1,
                     "Startup runs once, before the first request is served."),
        ],
    ),
    "fastapi-dependencies": lesson(
        "Dependencies give each endpoint what it needs (a database connection, the current user, settings) from one reusable, testable place.",
        [
            section(
                "Depends",
                "A dependency is a function. Declare it with `Depends()`, and FastAPI calls it for each request and passes the result to your endpoint. Dependencies can depend on other dependencies.",
                r"""
                from typing import Annotated

                from fastapi import Depends, FastAPI, Query

                app = FastAPI()


                def pagination(skip: int = Query(0, ge=0), limit: int = Query(10, le=50)) -> dict:
                    return {"skip": skip, "limit": limit}


                Page = Annotated[dict, Depends(pagination)]


                @app.get("/books")
                def books(page: Page) -> dict:
                    return page
                """,
            ),
            section(
                "Yield dependencies for resources",
                "A dependency that uses `yield` runs its setup before the request and its cleanup afterwards, which is ideal for database connections. FastAPI may run the setup and the endpoint in different worker threads, so SQLite needs `check_same_thread=False`. In tests, swap any dependency with `app.dependency_overrides`.",
                r"""
                import sqlite3
                from collections.abc import Iterator


                def get_db() -> Iterator[sqlite3.Connection]:
                    conn = sqlite3.connect("tasks.db", check_same_thread=False)
                    conn.row_factory = sqlite3.Row
                    try:
                        yield conn
                    finally:
                        conn.close()


                DB = Annotated[sqlite3.Connection, Depends(get_db)]


                @app.get("/tasks")
                def list_tasks(db: DB) -> list[dict]:
                    return [dict(row) for row in db.execute("SELECT * FROM tasks")]
                """,
            ),
        ],
        [
            "`Depends(func)` runs `func` for each request and injects the result.",
            "Use `yield` dependencies for setup plus guaranteed cleanup.",
            "Override dependencies in tests with `app.dependency_overrides`.",
        ],
        r"""
        import sqlite3
        from collections.abc import Iterator
        from typing import Annotated

        from fastapi import Depends, FastAPI

        DATABASE = "tasks.db"
        app = FastAPI()


        def get_db() -> Iterator[sqlite3.Connection]:
            conn = sqlite3.connect(DATABASE, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()


        DB = Annotated[sqlite3.Connection, Depends(get_db)]


        @app.post("/tasks", status_code=201)
        def create_task(title: str, db: DB) -> dict:
            cursor = db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
            db.commit()                           # commit before the response is sent
            return {"id": cursor.lastrowid, "title": title}


        @app.get("/tasks")
        def list_tasks(db: DB) -> list[dict]:
            return [dict(row) for row in db.execute("SELECT id, title FROM tasks")]

        # In tests: app.dependency_overrides[get_db] = a function that yields a temporary database
        """,
        [
            question("When does FastAPI call a dependency function?", ["Once, at startup", "For each request that uses it", "Only in tests", "When you import it"], 1,
                     "Within one request, a dependency used in several places is called once and its result reused."),
            question("In a `yield` dependency, where does the cleanup go?", ["Before the yield", "In a finally block after the yield", "In the endpoint", "Nowhere; it's automatic"], 1,
                     "finally makes sure the connection is closed even if the endpoint raised."),
            question("How do you replace a dependency in tests?", ["Edit the source code", "`app.dependency_overrides[original] = replacement`", "Monkeypatch FastAPI itself", "Set an environment variable"], 1,
                     "Overrides let tests use a temporary database or a fake user without touching the app code."),
        ],
    ),
    "fastapi-errors": lesson(
        "Good APIs fail clearly: the right status code, a helpful message, and settings that change per environment without editing code.",
        [
            section(
                "Status codes and HTTPException",
                "Raise `HTTPException` to stop and return an error: 400 for a malformed request, 404 when something doesn't exist, 409 when the request conflicts with the current state (such as a duplicate). FastAPI sends 422 automatically for validation errors. The `status` constants make codes readable.",
                r"""
                from fastapi import FastAPI, HTTPException, status

                app = FastAPI()
                tasks: dict[str, bool] = {}


                @app.post("/tasks/{title}", status_code=status.HTTP_201_CREATED)
                def add(title: str) -> dict:
                    if title in tasks:
                        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"'{title}' already exists")
                    tasks[title] = False
                    return {"title": title}
                """,
            ),
            section(
                "Custom exception handlers and settings",
                "Raise your own domain exceptions in business logic and convert them to HTTP responses in one handler. Read configuration from environment variables (or pydantic-settings), so the same code runs locally and in production. This app reads `APP_PASSWORD` and `APP_DB_PATH` this way.",
                r"""
                import os

                from fastapi import Request
                from fastapi.responses import JSONResponse


                class TaskNotFound(Exception):
                    def __init__(self, title: str):
                        self.title = title


                @app.exception_handler(TaskNotFound)
                async def task_not_found(request: Request, error: TaskNotFound) -> JSONResponse:
                    return JSONResponse(status_code=404, content={"detail": f"No task called {error.title!r}"})


                MAX_TASKS = int(os.environ.get("MAX_TASKS", "100"))
                """,
            ),
        ],
        [
            "404 = not found, 409 = conflict, 422 = invalid input, 500 = a bug on your side.",
            "Keep error messages helpful, but never leak secrets or stack traces.",
            "Configuration comes from the environment, not hard-coded values.",
        ],
        r"""
        from fastapi import FastAPI, HTTPException, status
        from pydantic import BaseModel

        app = FastAPI()


        class TaskIn(BaseModel):
            title: str


        tasks: dict[int, dict] = {}


        @app.post("/tasks", status_code=status.HTTP_201_CREATED)
        def create_task(data: TaskIn) -> dict:
            if any(t["title"].lower() == data.title.lower() for t in tasks.values()):
                raise HTTPException(status.HTTP_409_CONFLICT, detail="A task with this title already exists")
            task_id = max(tasks, default=0) + 1
            tasks[task_id] = {"id": task_id, "title": data.title, "done": False}
            return tasks[task_id]


        @app.post("/tasks/{task_id}/complete")
        def complete_task(task_id: int) -> dict:
            task = tasks.get(task_id)
            if task is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")
            if task["done"]:
                raise HTTPException(status.HTTP_409_CONFLICT, detail="Task is already complete")
            task["done"] = True
            return task
        """,
        [
            question("A client tries to create a task whose title already exists. Which status fits best?", ["200", "404", "409 Conflict", "500"], 2,
                     "The request is valid, but it conflicts with the current state of the data."),
            question("Which status does FastAPI send automatically when request data fails validation?", ["400", "401", "422", "503"], 2,
                     "422 includes a list of which fields failed and why."),
            question("Where should the API key for a third-party service live?", ["In the source code", "In an environment variable or secret store", "In the response", "In the URL"], 1,
                     "Code is shared and committed; secrets must be injected at runtime."),
        ],
    ),
    "fastapi-testing": lesson(
        "FastAPI's TestClient calls your API in-process, so tests are fast and need no running server. Combine it with a temporary database for isolated tests.",
        [
            section(
                "TestClient basics",
                "`TestClient(app)` sends requests straight to your app. Assert on the status code and the JSON. Using it in a `with` block also runs the app's startup and shutdown (lifespan) code.",
                r"""
                from fastapi.testclient import TestClient

                from main import app


                def test_health():
                    with TestClient(app) as client:
                        response = client.get("/health")
                    assert response.status_code == 200
                    assert response.json()["status"] == "ok"
                """,
            ),
            section(
                "Isolated data and a deployment checklist",
                'Give every test a fresh database: build the app from a factory function that takes the database path, or override the database dependency. This project does exactly that; see `create_app(tmp_path / "progress.sqlite3")` in `api/tests/test_api.py`.\n\n'
                "Before deploying, document how to install, configure and start the app. In production run `uvicorn main:app --host 0.0.0.0 --port 8000`, without `--reload`.",
                r"""
                import pytest
                from fastapi.testclient import TestClient

                from main import create_app


                @pytest.fixture
                def client(tmp_path):
                    app = create_app(database_path=tmp_path / "test.db")
                    with TestClient(app) as test_client:
                        yield test_client


                def test_created_task_can_be_read(client):
                    created = client.post("/tasks", json={"title": "Write tests"})
                    assert created.status_code == 201
                    task_id = created.json()["id"]
                    assert client.get(f"/tasks/{task_id}").json()["title"] == "Write tests"
                """,
            ),
        ],
        [
            "TestClient runs your app in-process; no server is needed.",
            "Give each test its own temporary database through `tmp_path`.",
            "Deploy without `--reload`, bind to 0.0.0.0 and read settings from the environment.",
        ],
        r"""
        # test_tasks_api.py
        import pytest
        from fastapi.testclient import TestClient

        from main import create_app


        @pytest.fixture
        def client(tmp_path):
            with TestClient(create_app(database_path=tmp_path / "tasks.db")) as test_client:
                yield test_client


        def test_create_and_read(client):
            task = client.post("/tasks", json={"title": "Ship v1"}).json()
            assert client.get(f"/tasks/{task['id']}").json() == task


        def test_missing_task_returns_404(client):
            assert client.get("/tasks/999").status_code == 404


        def test_blank_title_is_rejected(client):
            assert client.post("/tasks", json={"title": ""}).status_code == 422

        # README, "Run locally":
        #   python -m venv .venv  ->  .venv\Scripts\activate  ->  pip install -r requirements.txt
        #   uvicorn main:app --reload
        # "Production":
        #   uvicorn main:app --host 0.0.0.0 --port $PORT
        """,
        [
            question("Does TestClient need the server running under uvicorn?", ["Yes", "No, it calls the app in-process", "Only for POST requests", "Only in CI"], 1,
                     "TestClient talks to the ASGI app directly, so tests start instantly."),
            question("Why give each test its own temporary database?", ["It's faster to type", "Tests stay independent: one test's data can't break another", "SQLite requires it", "To test HTTPS"], 1,
                     "Shared state makes tests pass or fail depending on the order they run in."),
            question("Which uvicorn flag should you NOT use in production?", ["--host", "--port", "--reload", "--workers"], 2,
                     "`--reload` watches files and restarts the server; it's slow and meant for development."),
        ],
    ),
}
