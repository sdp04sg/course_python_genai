from app.content._build import lesson, question, section

CONTENT = {
    "pyadv-generators": lesson(
        "Generators produce values one at a time, on demand. They let you process huge or endless data using a small, constant amount of memory.",
        [
            section(
                "Iterators and yield",
                "Anything you can loop over is iterable. `iter()` gives you an iterator, and `next()` pulls values from it until StopIteration. A function that contains `yield` is a generator: each `next()` call resumes it until the next `yield`.",
                r"""
                def countdown(n: int):
                    while n > 0:
                        yield n
                        n -= 1


                gen = countdown(3)
                print(next(gen), next(gen), next(gen))   # 3 2 1
                print(list(countdown(3)))                # [3, 2, 1]
                """,
            ),
            section(
                "Lazy pipelines",
                "Chain generators so data flows through one item at a time. Generator expressions use parentheses: `(x * 2 for x in items)`. The `itertools` module adds building blocks such as `islice`, `chain` and `groupby`. A generator can only be consumed once.",
                r"""
                from itertools import islice


                def read_lines(path):
                    with open(path, encoding="utf-8") as file:
                        for line in file:
                            yield line.rstrip("\n")


                def matching(lines, word):
                    return (line for line in lines if word in line)


                first_three = islice(matching(read_lines("app.log"), "ERROR"), 3)
                for line in first_three:
                    print(line)
                """,
            ),
        ],
        [
            "`yield` pauses a function and resumes it on the next request.",
            "A generator pipeline uses constant memory, whatever the data size.",
            "A generator is exhausted after one pass; create a new one to loop again.",
        ],
        r"""
        from collections import Counter
        from pathlib import Path


        def read_lines(path: Path):
            with path.open(encoding="utf-8") as file:
                yield from file                       # one line at a time


        def errors(lines):
            return (line for line in lines if " ERROR " in line)


        def level_counts(path: Path) -> Counter:
            return Counter(line.split()[2] for line in read_lines(path) if len(line.split()) > 2)


        log = Path("app.log")
        log.write_text(
            "2026-01-01 10:00 INFO started\n"
            "2026-01-01 10:01 ERROR db timeout\n"
            "2026-01-01 10:02 ERROR db timeout\n",
            encoding="utf-8",
        )
        print(sum(1 for _ in errors(read_lines(log))))   # 2, without loading the whole file
        print(level_counts(log))                          # Counter({'ERROR': 2, 'INFO': 1})
        """,
        [
            question("What does calling a function that contains `yield` return?", ["The first yielded value", "A generator object", "None", "A list"], 1,
                     "The body doesn't run until you iterate over the generator or call `next()` on it."),
            question("`g = (x for x in range(3))`, then `list(g)` twice. What does the second call return?", ["[0, 1, 2]", "[]", "An error", "None"], 1,
                     "The first `list(g)` consumed the generator; it has nothing left to give."),
            question("What is the main benefit of generators for a 10 GB log file?", ["A faster CPU", "They process one line at a time, so memory use stays small", "They compress the file", "They run in parallel"], 1,
                     "Only the current line is in memory, instead of the whole file."),
        ],
    ),
    "pyadv-decorators": lesson(
        "A decorator wraps a function to add behaviour such as timing, retries, logging or access checks, without changing the function's code.",
        [
            section(
                "Closures and wrappers",
                "Functions are objects: you can pass them around and return them. An inner function that uses variables from its enclosing function is a closure. A decorator is a function that takes a function and returns a wrapped version; `@timer` above a function is shorthand for `func = timer(func)`.",
                r"""
                import functools
                import time


                def timer(func):
                    @functools.wraps(func)            # keep func's name and docstring
                    def wrapper(*args, **kwargs):
                        start = time.perf_counter()
                        try:
                            return func(*args, **kwargs)
                        finally:
                            print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
                    return wrapper


                @timer
                def slow_sum(n):
                    return sum(range(n))


                slow_sum(1_000_000)
                """,
            ),
            section(
                "Decorators with arguments",
                "To configure a decorator, as in `@retry(times=3)`, add one more level: an outer function that takes the settings and returns the actual decorator.",
                r"""
                import functools


                def repeat(times: int):
                    def decorator(func):
                        @functools.wraps(func)
                        def wrapper(*args, **kwargs):
                            return [func(*args, **kwargs) for _ in range(times)]
                        return wrapper
                    return decorator


                @repeat(times=2)
                def greet(name):
                    return f"Hi {name}"


                print(greet("Ada"))   # ['Hi Ada', 'Hi Ada']
                """,
            ),
        ],
        [
            "`@decorator` means `func = decorator(func)`.",
            "Accept `*args, **kwargs` so the wrapper works with any signature.",
            "Always apply `functools.wraps` to keep the original name and docstring.",
        ],
        r"""
        import functools
        import time


        def timer(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
            return wrapper


        def retry(times: int = 3, delay: float = 0.5, exceptions=(Exception,)):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    for attempt in range(1, times + 1):
                        try:
                            return func(*args, **kwargs)
                        except exceptions as error:
                            if attempt == times:
                                raise
                            print(f"Attempt {attempt} failed ({error}); retrying")
                            time.sleep(delay)
                return wrapper
            return decorator


        calls = {"count": 0}


        @timer
        @retry(times=3, delay=0.1, exceptions=(ConnectionError,))
        def flaky():
            calls["count"] += 1
            if calls["count"] < 3:
                raise ConnectionError("network down")
            return "ok"


        print(flaky(), flaky.__name__)   # ok flaky
        """,
        [
            question("`@deco` above `def f(): ...` is equivalent to…", ["deco()", "f = deco(f)", "f = deco", "deco = f(deco)"], 1,
                     "Python calls the decorator with the function and rebinds the name to the result."),
            question("What goes wrong without `functools.wraps`?", ["The function won't run", "The wrapper replaces the function's metadata, so `__name__` becomes 'wrapper'", "Arguments are lost", "It's slower"], 1,
                     "Tools, logs and debuggers then show 'wrapper' instead of the real function's name and docstring."),
            question("How many nested functions does a decorator that takes arguments, such as `@retry(times=3)`, usually need?", ["1", "2", "3", "4"], 2,
                     "`retry(times)` returns `decorator(func)`, which returns `wrapper(*args, **kwargs)`: three levels."),
        ],
    ),
    "pyadv-context-managers": lesson(
        "Context managers guarantee setup and cleanup (closing files, releasing locks, rolling back transactions) even when errors happen.",
        [
            section(
                "The with protocol",
                "A `with` block calls `__enter__` at the start and `__exit__` at the end, whether the block finishes normally or raises. `__exit__` receives the exception details; returning True from it would swallow the exception, which is rarely what you want.",
                r"""
                import time


                class Timer:
                    def __enter__(self):
                        self.start = time.perf_counter()
                        return self

                    def __exit__(self, exc_type, exc, tb):
                        self.elapsed = time.perf_counter() - self.start
                        print(f"Took {self.elapsed:.3f}s")
                        return False          # don't hide exceptions


                with Timer() as t:
                    sum(range(1_000_000))
                """,
            ),
            section(
                "contextlib shortcuts",
                "`contextlib.contextmanager` turns a generator into a context manager: code before `yield` is the setup and code after it is the cleanup. Put the cleanup in `finally` so it also runs after errors. `contextlib.suppress` ignores specific exceptions, and `ExitStack` manages a variable number of resources.",
                r"""
                import os
                from contextlib import contextmanager, suppress


                @contextmanager
                def working_directory(path):
                    previous = os.getcwd()
                    os.chdir(path)
                    try:
                        yield
                    finally:
                        os.chdir(previous)      # always restored


                with suppress(FileNotFoundError):
                    os.remove("missing.tmp")    # no error if it doesn't exist
                """,
            ),
        ],
        [
            "`with` guarantees cleanup through `__exit__`.",
            "With `@contextmanager`, wrap the `yield` in try/finally.",
            "Return False (or None) from `__exit__` so errors still propagate.",
        ],
        r"""
        import time
        from contextlib import contextmanager


        class Timer:
            def __enter__(self):
                self.start = time.perf_counter()
                return self

            def __exit__(self, exc_type, exc, tb):
                self.elapsed = time.perf_counter() - self.start
                error = exc_type.__name__ if exc_type else "none"
                print(f"[class] {self.elapsed:.4f}s (error: {error})")
                return False


        @contextmanager
        def timer(label: str):
            start = time.perf_counter()
            try:
                yield
            finally:
                print(f"[{label}] {time.perf_counter() - start:.4f}s")


        with Timer():
            sum(range(100_000))

        try:
            with timer("failing block"):
                raise ValueError("boom")
        except ValueError:
            print("The error still reached us, and the timer printed first.")
        """,
        [
            question("When does `__exit__` run?", ["Only on success", "Only on error", "Whenever the with block ends, after success or an error", "When the object is garbage-collected"], 2,
                     "That guarantee is the whole point of context managers."),
            question("In a `@contextmanager` function, where should cleanup go?", ["Before the yield", "In a finally block after the yield", "In `__init__`", "Anywhere"], 1,
                     "If the with block raises, the exception is thrown at the `yield`; only a finally block still runs then."),
            question("What happens if `__exit__` returns True?", ["The exception is re-raised", "The exception is suppressed", "The block runs again", "Nothing"], 1,
                     "A true return value tells Python the exception was handled, so it's swallowed."),
        ],
    ),
    "pyadv-typing": lesson(
        "Type hints document your code and let tools such as mypy catch bugs before you run it.",
        [
            section(
                "Annotations and generics",
                "Annotate parameters, return values and important variables. Use built-in generics (`list[int]`, `dict[str, float]`), `X | None` for values that may be missing, and type variables for functions that work with any type. Python ignores hints at runtime; a type checker reads them. (Python 3.12+ also lets you write `def first[T](items: list[T]) -> T | None`.)",
                r"""
                from typing import TypeVar

                T = TypeVar("T")


                def first(items: list[T]) -> T | None:
                    return items[0] if items else None


                def mean(values: list[float]) -> float:
                    return sum(values) / len(values)


                name: str = first(["ada", "grace"]) or "nobody"
                """,
            ),
            section(
                "Protocols: structural typing",
                "A Protocol describes what an object must be able to do, not which class it inherits from. Any class with matching methods satisfies it: duck typing that a type checker can verify. Install mypy with `pip install mypy` and run `mypy --strict app.py`.",
                r"""
                from typing import Protocol


                class Storage(Protocol):
                    def save(self, key: str, value: str) -> None: ...
                    def load(self, key: str) -> str | None: ...


                class MemoryStorage:
                    def __init__(self) -> None:
                        self.data: dict[str, str] = {}

                    def save(self, key: str, value: str) -> None:
                        self.data[key] = value

                    def load(self, key: str) -> str | None:
                        return self.data.get(key)


                def remember(store: Storage) -> None:   # MemoryStorage fits without inheriting
                    store.save("theme", "dark")
                """,
            ),
        ],
        [
            "Hints are checked by tools (mypy, pyright, your editor), not by Python at runtime.",
            "Use `X | None` and handle the None case explicitly.",
            "Protocols type-check duck typing without inheritance.",
        ],
        r"""
        # tasks.py - check with: mypy --strict tasks.py
        from typing import Protocol


        class TaskStore(Protocol):
            def save(self, tasks: dict[str, bool]) -> None: ...
            def load(self) -> dict[str, bool]: ...


        class MemoryStore:
            def __init__(self) -> None:
                self._tasks: dict[str, bool] = {}

            def save(self, tasks: dict[str, bool]) -> None:
                self._tasks = dict(tasks)

            def load(self) -> dict[str, bool]:
                return dict(self._tasks)


        class TaskList:
            def __init__(self, store: TaskStore) -> None:
                self._store = store
                self._tasks = store.load()

            def add(self, title: str) -> None:
                self._tasks[title] = False
                self._store.save(self._tasks)

            def pending(self) -> list[str]:
                return [title for title, done in self._tasks.items() if not done]


        tasks = TaskList(MemoryStore())
        tasks.add("Learn Protocols")
        print(tasks.pending())
        """,
        [
            question('Python doesn\'t enforce type hints at runtime. What catches a call like `mean("abc")` before the code runs?', ["The Python interpreter, when importing", "A type checker such as mypy", "pip", "Nothing can"], 1,
                     "mypy (or your editor's checker) reads the hints and reports that a str isn't a list[float]."),
            question("Which annotation means 'a string, or nothing'?", ["str?", "`str | None` (or `Optional[str]`)", "str or None, written as text", "Any"], 1,
                     "`str | None` is the modern spelling; `Optional[str]` means the same thing."),
            question("What makes a class satisfy a Protocol?", ["Inheriting from it", "Having the methods and attributes the Protocol describes", "Registering it", "Using @dataclass"], 1,
                     "Protocols are structural: matching the shape is enough."),
        ],
    ),
    "pyadv-dataclasses": lesson(
        "Dataclasses write the boring parts of a class for you (`__init__`, `__repr__`, `__eq__`), and enums give names to a fixed set of values.",
        [
            section(
                "@dataclass",
                "Declare fields with type hints and you get a constructor, a readable repr and equality for free. `frozen=True` makes instances immutable (and hashable), `order=True` adds comparisons, and `field(default_factory=list)` gives each instance its own mutable default.",
                r"""
                from dataclasses import dataclass, field


                @dataclass(frozen=True, order=True)
                class Version:
                    major: int
                    minor: int = 0


                @dataclass
                class Project:
                    name: str
                    tags: list[str] = field(default_factory=list)


                print(Version(1, 2) < Version(1, 10))   # True: compares fields in order
                print(Project("api"))                    # Project(name='api', tags=[])
                """,
            ),
            section(
                "Enums",
                'An Enum is a fixed set of named constants. It prevents typos like `"actve"` and makes comparisons explicit. Mixing in `str` (or using `StrEnum` in Python 3.11+) makes members behave like strings too.',
                r"""
                from enum import Enum, auto


                class Status(Enum):
                    TODO = auto()
                    DOING = auto()
                    DONE = auto()


                status = Status.DOING
                print(status.name, status is Status.DOING)   # DOING True
                print([s.name for s in Status])              # ['TODO', 'DOING', 'DONE']
                """,
            ),
        ],
        [
            "Dataclasses generate `__init__`, `__repr__` and `__eq__` from annotated fields.",
            "Use `field(default_factory=...)` for list or dict defaults.",
            "Enums replace magic strings with named, checkable values.",
        ],
        r"""
        from dataclasses import dataclass
        from enum import Enum


        class Kind(str, Enum):      # str mixin: members compare and sort like strings
            FRIEND = "friend"
            WORK = "work"
            FAMILY = "family"


        @dataclass(frozen=True, order=True)
        class Contact:
            name: str
            phone: str
            kind: Kind = Kind.FRIEND


        book = {
            Contact("Grace", "555-0199", Kind.WORK),
            Contact("Ada", "555-0101"),
            Contact("Ada", "555-0101"),     # duplicate: frozen dataclasses are hashable
        }
        print(len(book))                     # 2
        for contact in sorted(book):         # order=True sorts by name, then phone, then kind
            print(contact)
        print(Contact("Ada", "1") == Contact("Ada", "1"))   # True: compares fields
        """,
        [
            question("Which methods does `@dataclass` generate by default?", ["`__init__`, `__repr__` and `__eq__`", "`__hash__` only", "`__lt__` and `__gt__`", "None"], 0,
                     "Ordering methods need `order=True`; hashing depends on `frozen` and `eq`."),
            question("Why write `tags: list[str] = field(default_factory=list)` instead of `= []`?", ["It's shorter", "Each instance gets its own new list instead of sharing one", "Lists aren't allowed", "For speed"], 1,
                     "Dataclasses reject a plain `[]` default because it would be shared between instances; `default_factory` creates a new list each time."),
            question("What does `frozen=True` do?", ["Makes the class abstract", "Prevents changing fields after creation, and makes instances hashable", "Caches instances", "Makes fields private"], 1,
                     "Assigning to a field of a frozen instance raises FrozenInstanceError."),
        ],
    ),
    "pyadv-data-model": lesson(
        "Special ('dunder') methods let your objects work with Python's built-in syntax: `+`, `==`, `len()`, for loops, printing and more.",
        [
            section(
                "Representation and comparison",
                "`__repr__` gives developers an unambiguous description, shown in the REPL and debuggers; `__str__` is the friendly version that `print` uses. `__eq__` defines `==`. If you define `__eq__`, also define `__hash__`, or the object becomes unhashable.",
                r"""
                class Money:
                    def __init__(self, amount: int, currency: str):
                        self.amount, self.currency = amount, currency

                    def __repr__(self) -> str:
                        return f"Money({self.amount!r}, {self.currency!r})"

                    def __str__(self) -> str:
                        return f"{self.amount} {self.currency}"

                    def __eq__(self, other: object) -> bool:
                        if not isinstance(other, Money):
                            return NotImplemented
                        return (self.amount, self.currency) == (other.amount, other.currency)
                """,
            ),
            section(
                "Operators, length and iteration",
                "`__add__` powers `+`, `__len__` powers `len()`, `__iter__` makes an object loopable and `__getitem__` enables indexing. Return `NotImplemented` for operand types you don't support, so Python can try the other operand.",
                r"""
                class Playlist:
                    def __init__(self, songs: list[str]):
                        self.songs = songs

                    def __len__(self) -> int:
                        return len(self.songs)

                    def __iter__(self):
                        return iter(self.songs)

                    def __getitem__(self, index):
                        return self.songs[index]

                    def __add__(self, other: "Playlist") -> "Playlist":
                        return Playlist(self.songs + other.songs)


                mix = Playlist(["intro"]) + Playlist(["outro"])
                print(len(mix), list(mix), mix[0])   # 2 ['intro', 'outro'] intro
                """,
            ),
        ],
        [
            "Give every class you write a `__repr__`.",
            "Return `NotImplemented`, not False, for unsupported operand types.",
            "Small protocols (`__len__`, `__iter__`, `__getitem__`) make objects feel built-in.",
        ],
        r"""
        from __future__ import annotations

        import math


        class Vector:
            def __init__(self, *components: float) -> None:
                self.components = tuple(components)

            def __repr__(self) -> str:
                return f"Vector{self.components}"

            def __len__(self) -> int:
                return len(self.components)

            def __iter__(self):
                return iter(self.components)

            def __eq__(self, other: object) -> bool:
                return isinstance(other, Vector) and self.components == other.components

            def __hash__(self) -> int:
                return hash(self.components)

            def __add__(self, other: Vector) -> Vector:
                if not isinstance(other, Vector) or len(other) != len(self):
                    return NotImplemented
                return Vector(*(a + b for a, b in zip(self, other)))

            def __abs__(self) -> float:
                return math.hypot(*self.components)


        v = Vector(1, 2) + Vector(3, 4)
        print(v, len(v), list(v), abs(Vector(3, 4)))   # Vector(4, 6) 2 [4, 6] 5.0
        assert v == Vector(4, 6)
        """,
        [
            question("Which method does `print(obj)` use first?", ["`__repr__`", "`__str__`", "Only `__format__`", "`__print__`"], 1,
                     "print calls `str()`, which uses `__str__` and falls back to `__repr__` when `__str__` isn't defined."),
            question("Which method makes `for x in obj` work?", ["`__len__`", "`__iter__`", "`__contains__`", "`__call__`"], 1,
                     "`__iter__` returns an iterator. (Python can also fall back to `__getitem__` with 0, 1, 2…)"),
            question("What should `__add__` return for an unsupported operand type?", ["False", "None", "NotImplemented", "Always raise TypeError itself"], 2,
                     "NotImplemented lets Python try the other operand's `__radd__` and raise a proper TypeError if that fails too."),
        ],
    ),
    "pyadv-asyncio": lesson(
        "asyncio runs many waiting tasks (network calls, database queries) concurrently on one thread, so slow I/O overlaps instead of queuing up.",
        [
            section(
                "async, await and gather",
                "`async def` defines a coroutine. `await` pauses it until the awaited work finishes, and other tasks run in the meantime. `asyncio.gather` runs several coroutines concurrently, and `asyncio.run` starts the event loop.",
                r"""
                import asyncio
                import time


                async def fetch(name: str, seconds: float) -> str:
                    await asyncio.sleep(seconds)          # stands in for a network call
                    return f"{name} done"


                async def main() -> None:
                    start = time.perf_counter()
                    results = await asyncio.gather(fetch("a", 1), fetch("b", 1), fetch("c", 1))
                    print(results, f"{time.perf_counter() - start:.1f}s")   # about 1.0s, not 3s


                asyncio.run(main())
                """,
            ),
            section(
                "Timeouts and blocking pitfalls",
                "Wrap slow work in `asyncio.wait_for()` (or `asyncio.timeout()` in Python 3.11+). Never call blocking functions such as `time.sleep` or `requests.get` inside a coroutine: they freeze every task. Use async libraries such as httpx, or move blocking code to a thread with `asyncio.to_thread`.",
                r"""
                import asyncio


                async def slow() -> str:
                    await asyncio.sleep(5)
                    return "finished"


                async def main() -> None:
                    try:
                        result = await asyncio.wait_for(slow(), timeout=1)
                    except asyncio.TimeoutError:
                        result = "gave up after 1s"
                    print(result)


                asyncio.run(main())
                """,
            ),
        ],
        [
            "Async helps with I/O-bound work, not CPU-bound work.",
            "`gather` runs coroutines concurrently; awaiting them one by one runs them in sequence.",
            "Never block the event loop; use async libraries or `asyncio.to_thread`.",
        ],
        r"""
        import asyncio

        import httpx

        URLS = [
            "https://example.com",
            "https://www.python.org",
            "https://httpbin.org/delay/3",      # deliberately slower than the timeout
            "https://docs.python.org/3/",
            "https://pypi.org",
        ]


        async def fetch(client: httpx.AsyncClient, url: str) -> str:
            try:
                response = await client.get(url, timeout=2.0)
                return f"{response.status_code} {url}"
            except httpx.TimeoutException:
                return f"timeout {url}"
            except httpx.HTTPError as error:
                return f"error {url}: {error.__class__.__name__}"


        async def main() -> None:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                results = await asyncio.gather(*(fetch(client, url) for url in URLS))
            for line in results:
                print(line)


        asyncio.run(main())
        """,
        [
            question("Three coroutines each `await asyncio.sleep(1)` and run under `gather`. Roughly how long does it take?", ["1 second", "3 seconds", "0 seconds", "It depends on the number of CPU cores"], 0,
                     "The waits overlap on the event loop, so the total is about the longest single wait."),
            question("What's wrong with calling `time.sleep(2)` inside an async function?", ["Nothing", "It blocks the whole event loop, freezing every other task", "It raises SyntaxError", "It sleeps for 4 seconds"], 1,
                     "Use `await asyncio.sleep(2)`, which yields control to other tasks."),
            question("asyncio is best suited to…", ["CPU-heavy number crunching", "Many I/O waits, such as HTTP requests", "GPU work", "Replacing multiprocessing for every task"], 1,
                     "A single thread can juggle thousands of waiting connections, but only computes one thing at a time."),
        ],
    ),
    "pyadv-threads-processes": lesson(
        "Threads share memory and suit tasks that wait; processes run on separate CPU cores and suit heavy computation. `concurrent.futures` gives both the same simple API.",
        [
            section(
                "The GIL in one paragraph",
                "In standard CPython, the Global Interpreter Lock (GIL) lets only one thread execute Python bytecode at a time. Threads still speed up I/O, because the GIL is released while waiting, but CPU-heavy Python code needs separate processes to use several cores. (Python 3.13 introduced an optional free-threaded build without the GIL; it isn't the default.)",
                r"""
                import time
                from concurrent.futures import ThreadPoolExecutor


                def download(n: int) -> str:
                    time.sleep(1)                 # waiting on I/O releases the GIL
                    return f"file {n}"


                start = time.perf_counter()
                with ThreadPoolExecutor(max_workers=5) as pool:
                    results = list(pool.map(download, range(5)))
                print(results, f"{time.perf_counter() - start:.1f}s")   # about 1s, not 5s
                """,
            ),
            section(
                "Processes for CPU work",
                'ProcessPoolExecutor runs functions in separate processes, each with its own interpreter and GIL. Arguments and results are pickled between processes, so keep them small. On Windows and macOS, guard the entry point with `if __name__ == "__main__":`.',
                r"""
                from concurrent.futures import ProcessPoolExecutor


                def count_primes(limit: int) -> int:
                    return sum(all(n % d for d in range(2, int(n ** 0.5) + 1)) for n in range(2, limit))


                if __name__ == "__main__":
                    with ProcessPoolExecutor() as pool:
                        print(list(pool.map(count_primes, [50_000] * 4)))
                """,
            ),
        ],
        [
            "I/O-bound work → threads or asyncio. CPU-bound work → processes.",
            "Use `executor.map`, or `submit` with `as_completed`, for a simple, uniform API.",
            'Protect process-pool code with `if __name__ == "__main__":`.',
        ],
        r"""
        import time
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


        def io_task(_: int) -> None:
            time.sleep(0.5)                          # a simulated download


        def cpu_task(_: int) -> int:
            return sum(i * i for i in range(3_000_000))


        def timed(executor_class, task, label: str) -> None:
            start = time.perf_counter()
            with executor_class(max_workers=4) as pool:
                list(pool.map(task, range(4)))
            print(f"{label:<16} {time.perf_counter() - start:.2f}s")


        if __name__ == "__main__":
            timed(ThreadPoolExecutor, io_task, "threads, I/O")      # ~0.5s: the waits overlap
            timed(ProcessPoolExecutor, io_task, "processes, I/O")   # ~0.5s plus start-up cost
            timed(ThreadPoolExecutor, cpu_task, "threads, CPU")     # about serial: the GIL
            timed(ProcessPoolExecutor, cpu_task, "processes, CPU")  # faster on a multi-core machine
        """,
        [
            question("Why don't threads speed up pure-Python CPU work in standard CPython?", ["Threads are disabled", "The GIL lets only one thread execute Python bytecode at a time", "The OS runs threads on one core", "They do"], 1,
                     "Threads take turns holding the GIL, so CPU-bound Python code runs about as fast as a single thread."),
            question("What's the best tool for running pure-Python image calculations on 1,000 files on an 8-core machine?", ["ThreadPoolExecutor", "ProcessPoolExecutor", "A single loop", "asyncio.gather"], 1,
                     "Processes each have their own GIL, so they can use all 8 cores."),
            question('Why do process pools need `if __name__ == "__main__":` on Windows?', ["For speed", "Child processes import the main module, and without the guard they'd start pools recursively", "It's only style", "To enable the GIL"], 1,
                     "On Windows and macOS, new processes start by importing your script; the guard stops that import from running the pool code again."),
        ],
    ),
    "pyadv-performance": lesson(
        "Measure before you optimize. Profilers show where the time really goes, and a handful of techniques fix most hot spots.",
        [
            section(
                "Profile first",
                "`cProfile` records how long every function takes. Sort by cumulative time to find the slowest call path, and fix only what the profile shows. From the terminal, `python -m cProfile -s cumulative script.py` profiles a whole script. `timeit` compares small alternatives precisely.",
                r"""
                import cProfile
                import pstats


                def slow_unique(items):
                    result = []
                    for item in items:
                        if item not in result:     # O(n) check inside a loop: O(n^2) overall
                            result.append(item)
                    return result


                cProfile.run("slow_unique(list(range(5_000)) * 2)", "profile.out")
                pstats.Stats("profile.out").sort_stats("cumulative").print_stats(5)
                """,
            ),
            section(
                "Common fixes",
                "Use a better data structure (such as a set for membership), move work out of loops, prefer built-ins (`sum`, `sorted`, `str.join`) that run in C, and cache pure functions with `functools.cache` or `lru_cache(maxsize=...)`.",
                r"""
                from functools import lru_cache


                def fast_unique(items):
                    return list(dict.fromkeys(items))     # O(n), keeps first-seen order


                @lru_cache(maxsize=1024)
                def shipping_cost(country: str, weight_kg: int) -> float:
                    return len(country) * 1.5 + weight_kg * 0.8   # stands in for slow, pure work
                """,
            ),
        ],
        [
            "Profile before optimizing; guesses about hot spots are usually wrong.",
            "Changing the algorithm or data structure beats micro-optimizations.",
            "Only cache pure functions: same input, same output, no side effects.",
        ],
        r"""
        import cProfile
        import pstats
        from functools import cache


        def slow_report(n: int) -> str:
            lines = ""
            for i in range(n):
                if i not in list(range(0, n, 3)):   # rebuilds a list on every iteration
                    lines += f"{i},"                 # repeated string concatenation
            return lines


        def fast_report(n: int) -> str:
            multiples = set(range(0, n, 3))          # built once, with O(1) lookups
            return "".join(f"{i}," for i in range(n) if i not in multiples)


        @cache
        def fib(n: int) -> int:
            return n if n < 2 else fib(n - 1) + fib(n - 2)


        assert slow_report(300) == fast_report(300)
        cProfile.run("slow_report(3_000)", "slow.out")
        pstats.Stats("slow.out").sort_stats("cumulative").print_stats(3)
        cProfile.run("fast_report(3_000)", "fast.out")
        pstats.Stats("fast.out").sort_stats("cumulative").print_stats(3)
        print(fib(200))                              # instant, thanks to the cache
        """,
        [
            question("What's the first step when code is too slow?", ["Rewrite it in C", "Profile it to find where the time goes", "Add caching everywhere", "Use threads"], 1,
                     "Optimizing code that isn't the bottleneck wastes effort and adds complexity."),
            question("Which function is safe to cache?", ["One that reads the current time", "One whose result depends only on its arguments", "One that writes to a database", "One that returns random numbers"], 1,
                     "Caching returns a stored result, which is only correct when the same inputs always give the same output."),
            question('Why prefer `"".join(parts)` over `s += part` in a big loop?', ["It's shorter", "Repeated `+=` can copy the growing string each time; join builds it once", "join sorts the parts", "`+=` is deprecated"], 1,
                     "Strings are immutable, so building one piece by piece can be O(n²)."),
        ],
    ),
    "pyadv-packaging": lesson(
        "Package your code with pyproject.toml so it installs with pip, declares its dependencies and provides a command-line command.",
        [
            section(
                "Project layout and pyproject.toml",
                "Use a `src/` layout so tests run against the installed package rather than loose files. `pyproject.toml` names the build backend and holds the project's metadata, dependencies and console scripts.",
                r"""
                # Layout:
                #   tasks-cli/
                #     pyproject.toml
                #     src/tasks_cli/__init__.py
                #     src/tasks_cli/cli.py
                #     tests/test_cli.py

                [build-system]
                requires = ["hatchling"]
                build-backend = "hatchling.build"

                [project]
                name = "tasks-cli"
                version = "0.1.0"
                requires-python = ">=3.10"
                dependencies = []

                [project.scripts]
                tasks = "tasks_cli.cli:main"
                """,
                "toml",
            ),
            section(
                "Install, run and build",
                "`pip install -e .` installs the project in editable mode, so your edits take effect immediately. The `[project.scripts]` entry creates a `tasks` command. `python -m build` produces a wheel you can share or upload to PyPI.",
                r"""
                py -m venv .venv
                .\.venv\Scripts\Activate.ps1
                pip install -e .
                tasks add "Read about packaging"
                pip install build
                python -m build          # creates dist/tasks_cli-0.1.0-py3-none-any.whl
                """,
                "powershell",
            ),
        ],
        [
            "pyproject.toml is the single place for metadata, dependencies and tool settings.",
            "Use a `src/` layout and install with `pip install -e .` while developing.",
            "`[project.scripts]` turns a function into a terminal command.",
        ],
        r"""
        # src/tasks_cli/cli.py
        import argparse
        import json
        from pathlib import Path

        STORE = Path.home() / ".tasks.json"


        def load() -> dict[str, bool]:
            return json.loads(STORE.read_text(encoding="utf-8")) if STORE.exists() else {}


        def save(tasks: dict[str, bool]) -> None:
            STORE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


        def main() -> None:
            parser = argparse.ArgumentParser(prog="tasks", description="A tiny task list.")
            commands = parser.add_subparsers(dest="command", required=True)
            commands.add_parser("list")
            add = commands.add_parser("add")
            add.add_argument("title")
            done = commands.add_parser("done")
            done.add_argument("title")
            args = parser.parse_args()

            tasks = load()
            if args.command == "add":
                tasks[args.title] = False
            elif args.command == "done":
                tasks[args.title] = True
            else:
                for title, finished in tasks.items():
                    print(f"[{'x' if finished else ' '}] {title}")
            save(tasks)

        # In a fresh virtual environment: pip install -e .   then   tasks add "Ship it"
        """,
        [
            question("What does `pip install -e .` do?", ["Installs from PyPI", "Installs the current project in editable mode, so code changes apply without reinstalling", "Exports a requirements file", "Encrypts the package"], 1,
                     "Editable installs point at your source folder instead of copying it."),
            question("Which pyproject.toml table creates a terminal command?", ["[tool.commands]", "[project.scripts]", "[build-system]", "[project.urls]"], 1,
                     "Each entry maps a command name to a `module:function` to call."),
            question("Why use a `src/` layout?", ["pip requires it", "Tests run against the installed package, which catches packaging mistakes", "It makes imports faster", "It hides the code from users"], 1,
                     "Without `src/`, tests can accidentally import the local folder and miss files left out of the package."),
        ],
    ),
    "pyadv-testing": lesson(
        "Go beyond simple asserts: fixtures share setup, parametrize covers many cases with one test, and mocks replace slow or unpredictable dependencies.",
        [
            section(
                "Fixtures and parametrize",
                "A fixture is a function that provides test setup; a test requests it by naming it as a parameter. Built-in fixtures include `tmp_path` (a fresh temporary folder) and `monkeypatch`. `@pytest.mark.parametrize` runs one test with many inputs.",
                r"""
                import pytest


                @pytest.fixture
                def notes_file(tmp_path):
                    path = tmp_path / "notes.txt"
                    path.write_text("a\nb\n", encoding="utf-8")
                    return path


                def test_counts_lines(notes_file):
                    assert len(notes_file.read_text(encoding="utf-8").splitlines()) == 2


                @pytest.mark.parametrize("raw, expected", [("42", 42), (" 7 ", 7), ("0", 0)])
                def test_parse(raw, expected):
                    assert int(raw.strip()) == expected
                """,
            ),
            section(
                "Mocks and exceptions",
                "Replace things you don't control (time, the network, randomness) with fakes. `monkeypatch.setattr` swaps an attribute for one test, and `unittest.mock.Mock` records how it was called. Use `pytest.raises` to check that errors are raised.",
                r"""
                from unittest.mock import Mock

                import pytest


                def notify(sender, user):
                    if not user:
                        raise ValueError("user required")
                    sender.send(f"Hello {user}")


                def test_notify_sends_message():
                    sender = Mock()
                    notify(sender, "ada")
                    sender.send.assert_called_once_with("Hello ada")


                def test_notify_requires_user():
                    with pytest.raises(ValueError, match="required"):
                        notify(Mock(), "")
                """,
            ),
        ],
        [
            "Fixtures keep setup in one place; `tmp_path` gives every test a clean folder.",
            "Parametrize instead of copy-pasting tests.",
            "Mock only the boundaries (time, network, external services), not your own logic.",
        ],
        r"""
        # tasks.py
        from datetime import datetime
        from pathlib import Path


        def add_task(path: Path, title: str, now=datetime.now) -> str:
            if not title.strip():
                raise ValueError("title must not be empty")
            line = f"{now():%Y-%m-%d} {title.strip()}"
            with path.open("a", encoding="utf-8") as file:
                file.write(line + "\n")
            return line


        # test_tasks.py
        from datetime import datetime

        import pytest
        from tasks import add_task


        @pytest.fixture
        def task_file(tmp_path):
            return tmp_path / "tasks.txt"


        def fixed_clock():
            return datetime(2026, 1, 15)


        @pytest.mark.parametrize("title, expected", [
            ("Write tests", "2026-01-15 Write tests"),
            ("  padded  ", "2026-01-15 padded"),
        ])
        def test_add_task_formats_line(task_file, title, expected):
            assert add_task(task_file, title, now=fixed_clock) == expected
            assert task_file.read_text(encoding="utf-8") == expected + "\n"


        @pytest.mark.parametrize("title", ["", "   "])
        def test_add_task_rejects_blank_titles(task_file, title):
            with pytest.raises(ValueError):
                add_task(task_file, title, now=fixed_clock)
        """,
        [
            question("How does a test use a fixture?", ["By importing it", "By naming it as a parameter of the test function", "With a @use_fixture decorator", "By calling it directly"], 1,
                     "pytest sees the parameter name, runs the matching fixture and passes in its result."),
            question("What does the `tmp_path` fixture provide?", ["A folder shared by all tests", "A fresh temporary directory for each test", "The project root", "A mock file"], 1,
                     "Each test gets its own empty directory, so tests can't interfere with each other's files."),
            question("Which check verifies that a Mock was called exactly once with certain arguments?", ["mock.called_once()", "mock.assert_called_once_with(...)", "assert mock == 1", "mock.verify()"], 1,
                     "`assert_called_once_with` fails if the call count isn't 1 or the arguments differ."),
        ],
    ),
    "pyadv-logging-errors": lesson(
        "Production code needs logs you can search, configuration that changes without code edits, and errors that say exactly what went wrong.",
        [
            section(
                "Logging instead of print",
                "Create one logger per module with `logging.getLogger(__name__)` and configure logging once, when the program starts. Levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) control how much detail you see without changing code. `logger.exception()` also records the traceback.",
                r"""
                import logging

                logger = logging.getLogger(__name__)


                def main() -> None:
                    logging.basicConfig(
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                    )
                    logger.info("Starting with %d tasks", 3)      # formatted only if INFO is enabled
                    try:
                        1 / 0
                    except ZeroDivisionError:
                        logger.exception("Calculation failed")    # includes the traceback


                main()
                """,
            ),
            section(
                "Configuration and custom exceptions",
                "Read settings from environment variables with safe defaults, so the same code runs locally and in production. Define a small exception hierarchy with one base class, so callers can catch all of your errors at once or one kind specifically.",
                r"""
                import os


                class TasksError(Exception):
                    pass                      # base class for every error from this app


                class TaskNotFound(TasksError):
                    pass


                class StorageError(TasksError):
                    pass


                LOG_LEVEL = os.environ.get("TASKS_LOG_LEVEL", "INFO").upper()
                DATA_FILE = os.environ.get("TASKS_FILE", "tasks.json")
                """,
            ),
        ],
        [
            "Use `logging.getLogger(__name__)` in modules, and configure logging once in `main`.",
            "Pass values as logging arguments (`%s`) instead of building the message yourself.",
            "A custom exception hierarchy makes failures specific and easy to handle.",
        ],
        r"""
        import json
        import logging
        import os
        import sys
        from pathlib import Path

        logger = logging.getLogger("tasks")


        class TasksError(Exception):
            pass


        class TaskNotFound(TasksError):
            pass


        class StorageError(TasksError):
            pass


        def load(path: Path) -> dict[str, bool]:
            try:
                return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            except (OSError, json.JSONDecodeError) as error:
                raise StorageError(f"Can't read {path}") from error


        def complete(tasks: dict[str, bool], title: str) -> None:
            if title not in tasks:
                raise TaskNotFound(title)
            tasks[title] = True
            logger.info("Completed %r", title)


        def main() -> int:
            logging.basicConfig(level=os.environ.get("TASKS_LOG_LEVEL", "INFO").upper())
            path = Path(os.environ.get("TASKS_FILE", "tasks.json"))
            try:
                tasks = load(path)
                complete(tasks, sys.argv[1] if len(sys.argv) > 1 else "")
            except TaskNotFound as error:
                logger.error("No task called %r", error.args[0])
                return 1
            except TasksError:
                logger.exception("Task storage problem")
                return 2
            return 0


        if __name__ == "__main__":
            sys.exit(main())
        """,
        [
            question('Why prefer `logger.info("Loaded %d rows", n)` over an f-string?', ["It's required", "The message is only built if that level is enabled, and tools can group identical messages", "f-strings don't work in logs", "It's faster to type"], 1,
                     "Lazy formatting skips work for disabled levels, and the constant template makes log searches easier."),
            question("What does `raise StorageError(...) from error` do?", ["Hides the original error", "Keeps the original exception as the cause, shown in the traceback", "Retries the operation", "Logs the error"], 1,
                     "Exception chaining preserves the root cause while giving callers a meaningful error type."),
            question("Where should logging be configured (for example with `basicConfig`)?", ["In every module", "Once, at the application's entry point", "Inside each function", "Only in tests"], 1,
                     "Libraries and modules just get loggers; the application decides where logs go and at what level."),
        ],
    ),
}
