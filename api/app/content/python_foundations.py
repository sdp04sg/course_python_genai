from app.content._build import lesson, question, section

CONTENT = {
    "python-setup": lesson(
        "Install Python, check that it works, and run a script from the terminal. You'll use this edit-run loop for every program you write.",
        [
            section(
                "Install and check Python",
                "On Windows, install Python from python.org and tick **Add python.exe to PATH** in the installer, or install it from the Microsoft Store. "
                "Then open a new terminal and check the version. On Windows the `py` launcher also works; on macOS and Linux the command is usually `python3`.",
                r"""
                python --version
                py --version
                """,
                "powershell",
            ),
            section(
                "Write and run a script",
                "A script is a plain-text file ending in `.py`. Python runs it from top to bottom. `print()` writes text to the terminal, and `input()` waits for the user to type a line.\n\n"
                "Save the file, then run it with `python hello.py` from the folder that contains it.",
                r"""
                # hello.py
                print("Hello, world!")
                name = input("What is your name? ")
                print("Nice to meet you,", name)
                """,
            ),
            section(
                "Experiment in the interactive shell",
                "Type `python` with no file name to open the interactive shell (the REPL). It runs each line as soon as you press Enter, which is handy for trying ideas. Leave it with `exit()`.",
                r"""
                >>> 2 + 3
                5
                >>> "py" * 3
                'pypypy'
                >>> exit()
                """,
                "pycon",
            ),
        ],
        [
            "Check your installation with `python --version` (or `py --version` on Windows).",
            "Run a script with `python file.py` from the folder that contains it.",
            "Use the REPL to experiment, and `.py` files for programs you want to keep.",
        ],
        r"""
        # hello.py
        name = input("Your name: ")
        print(f"Hello, {name}! Welcome to Python.")

        # Run it from the same folder:
        #   python hello.py
        """,
        [
            question("Which command runs a script called `hello.py`?", ["run hello.py", "python hello.py", "python --version hello.py", "open hello.py"], 1,
                     "`python` followed by a file name runs that script. `--version` only prints the installed version."),
            question("What type of value does `input()` return?", ["A number", "The text the user typed, as a string", "Nothing", "A list of words"], 1,
                     "`input()` always returns a string. Convert it with `int()` or `float()` when you need a number."),
            question("How do you leave the interactive shell?", ["Type `exit()`", "Press Enter twice", "Type `stop`", "Close the file"], 0,
                     "`exit()` leaves the REPL. Ctrl+Z then Enter (Windows) or Ctrl+D (macOS/Linux) also work."),
        ],
    ),
    "python-variables": lesson(
        "Variables are names for values. Learn Python's core types (int, float, str and bool) and how to convert between them.",
        [
            section(
                "Create variables",
                "Assign a value with `=`. Python works out the type from the value, and a name can point to a different value later. Use lowercase names with underscores (snake_case) and choose names that explain the value.",
                r"""
                title = "Dune"          # str: text
                pages = 412             # int: whole number
                rating = 4.5            # float: decimal number
                finished = False        # bool: True or False
                print(type(pages))      # <class 'int'>
                """,
            ),
            section(
                "Convert and combine values",
                'Values of different types don\'t mix automatically: `"Pages: " + 412` raises a TypeError. Convert with `str()`, `int()` or `float()`, or use an f-string, which converts values for you. '
                "`//` divides and drops the fraction, and `%` gives the remainder.",
                r"""
                pages = int("412")                   # text -> int
                rating = float("4.5")                # text -> float
                print("Pages: " + str(pages))        # int -> text
                print(f"{pages} pages, rated {rating}")
                print(pages // 100, pages % 100)     # 4 12
                """,
            ),
        ],
        [
            "A variable is a name bound to a value; assigning again makes it point somewhere new.",
            "`type()` shows a value's type; `int()`, `float()`, `str()` and `bool()` convert between types.",
            'f-strings (`f"{name} has {pages} pages"`) are the clearest way to build text from values.',
        ],
        r"""
        title = "The Hobbit"
        pages = 310
        status = "reading"
        print(f"{title}: {pages} pages ({status})")
        # The Hobbit: 310 pages (reading)
        """,
        [
            question("What is the type of `3.0`?", ["int", "float", "str", "bool"], 1,
                     "Any number written with a decimal point is a float, even when the fraction is zero."),
            question('What does `"5" + "3"` produce?', ["8", "'53'", "A TypeError", "15"], 1,
                     "Adding two strings joins them, so the result is the string '53'."),
            question("What does `17 // 5` return?", ["3.4", "3", "2", "4"], 1,
                     "`//` is floor division: it keeps the whole-number part, 3. Use `%` for the remainder, 2."),
        ],
    ),
    "python-conditionals": lesson(
        "Use if, elif and else to decide which code runs, based on comparisons and logical operators.",
        [
            section(
                "Compare values",
                "Comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`) produce True or False. Combine them with `and`, `or` and `not`. Python also allows chained comparisons such as `0 <= score <= 100`.",
                r"""
                score = 72
                print(score >= 50)                  # True
                print(0 <= score <= 100)            # True: chained comparison
                print(score > 90 or score < 10)     # False
                """,
            ),
            section(
                "Branch with if, elif and else",
                "Python checks each condition in order and runs only the first block whose condition is true. Indentation (4 spaces) shows which lines belong to each block.\n\n"
                'Empty values are "falsy": `0`, `""`, `[]`, `{}` and `None` behave like False in an if statement.',
                r"""
                score = 72
                if not 0 <= score <= 100:
                    print("Invalid score")
                elif score >= 90:
                    print("A")
                elif score >= 70:
                    print("B")
                else:
                    print("Keep practising")
                """,
            ),
        ],
        [
            "Only the first true branch runs, so order conditions from most to least specific.",
            "Indentation defines blocks; keep it consistent at 4 spaces.",
            "Zero, empty strings, empty collections and None are falsy.",
        ],
        r"""
        raw = input("Score (0-100): ")
        if not raw.isdigit():
            print("Please enter a whole number.")
        else:
            score = int(raw)
            if score > 100:
                print("Scores can't be above 100.")
            elif score >= 90:
                print("Grade: A")
            elif score >= 75:
                print("Grade: B")
            elif score >= 50:
                print("Grade: C")
            else:
                print("Grade: F")
        """,
        [
            question("If `x = 15`, what does `if x > 10: print('big')` / `elif x > 5: print('medium')` print?", ["big", "medium", "big and medium", "Nothing"], 0,
                     "Only the first true branch runs, so the elif is skipped even though `x > 5` is also true."),
            question("Which value is falsy?", ['"0"', "[0]", "0", '" "'], 2,
                     'The integer 0 is falsy. The string "0", the list [0] and a space are all non-empty, so they are truthy.'),
            question("What does `not (3 > 2 and 2 > 5)` evaluate to?", ["True", "False", "An error", "None"], 0,
                     "`3 > 2` is True and `2 > 5` is False, so the `and` is False, and `not False` is True."),
        ],
    ),
    "python-loops": lesson(
        "Repeat work with for loops over collections and ranges, and with while loops that run until something changes.",
        [
            section(
                "for loops",
                "A for loop takes each item from a sequence in turn. `range(start, stop, step)` produces numbers up to, but not including, `stop`. `enumerate()` gives you a counter alongside each item.",
                r"""
                for n in range(1, 6):
                    print(n, n * n)

                for i, fruit in enumerate(["apple", "kiwi", "plum"], start=1):
                    print(i, fruit)
                """,
            ),
            section(
                "while loops, break and continue",
                "A while loop repeats as long as its condition is true, so something inside must eventually change it. `break` leaves the loop early; `continue` skips to the next iteration.",
                r"""
                total = 0
                while True:
                    entry = input("Number (blank to stop): ")
                    if entry == "":
                        break
                    if not entry.isdigit():
                        print("Skipping", entry)
                        continue
                    total += int(entry)
                print("Total:", total)
                """,
            ),
        ],
        [
            "Use `for` when you know what to loop over, and `while` when you loop until something happens.",
            "`range(5)` gives 0 to 4: the stop value is excluded.",
            "Every while loop needs a way out: a condition that changes, or a `break`.",
        ],
        r"""
        import random

        secret = random.randint(1, 20)
        for turn in range(1, 6):
            guess = int(input(f"Guess {turn}/5: "))
            if guess == secret:
                print("You got it!")
                break
            print("Too low" if guess < secret else "Too high")
        else:
            # A for loop's else block runs only if the loop didn't break
            print(f"Out of turns. It was {secret}.")
        """,
        [
            question("What does `list(range(2, 10, 3))` produce?", ["[2, 5, 8]", "[2, 5, 8, 11]", "[3, 6, 9]", "[2, 3, 4]"], 0,
                     "Start at 2 and add 3 each time while staying below 10: 2, 5, 8."),
            question("What does `continue` do inside a loop?", ["Exits the loop", "Skips the rest of this iteration and moves to the next", "Restarts the loop from the beginning", "Pauses the program"], 1,
                     "`continue` jumps to the next iteration. `break` is the one that exits the loop entirely."),
            question("Starting with `n = 10`, how many times does `while n > 0: n -= 3` run its body?", ["3", "4", "10", "Forever"], 1,
                     "n goes 10 → 7 → 4 → 1 → -2, so the body runs 4 times."),
        ],
    ),
    "python-functions": lesson(
        "Functions package logic behind a name, with inputs (parameters) and an output (the return value), so you can reuse and test it.",
        [
            section(
                "Define and call functions",
                "`def` creates a function. Parameters receive the arguments you pass in, and `return` sends a value back. A function without a `return` gives back `None`. You can pass arguments by position or by name.",
                r"""
                def area(width, height):
                    return width * height

                print(area(3, 4))                 # 12
                print(area(height=2, width=5))    # keyword arguments: 10
                """,
            ),
            section(
                "Defaults, scope and type hints",
                "Parameters can have default values. Variables created inside a function are local: they disappear when it returns. Type hints document what goes in and out; Python doesn't enforce them at runtime.\n\n"
                "Never use a mutable default such as `def add(item, items=[])`: the same list is shared between calls. Use `None` and create the list inside the function.",
                r"""
                def greet(name: str, greeting: str = "Hello") -> str:
                    message = f"{greeting}, {name}!"    # local variable
                    return message

                print(greet("Ada"))               # Hello, Ada!
                print(greet("Ada", "Welcome"))    # Welcome, Ada!
                """,
            ),
        ],
        [
            "A good function does one thing, takes its inputs as parameters and returns its result.",
            "Without a `return`, a function returns `None`.",
            "Avoid mutable default arguments; default to `None` instead.",
        ],
        r"""
        def parse_score(raw: str) -> int | None:
            if not raw.isdigit():
                return None
            score = int(raw)
            return score if score <= 100 else None


        def grade(score: int) -> str:
            if score >= 90:
                return "A"
            if score >= 75:
                return "B"
            if score >= 50:
                return "C"
            return "F"


        score = parse_score(input("Score: "))
        print("Invalid score" if score is None else f"Grade: {grade(score)}")
        """,
        [
            question("What does a function return if it has no `return` statement?", ["0", "An empty string", "None", "An error"], 2,
                     "Python functions return `None` when they finish without reaching a `return`."),
            question("Given `def f(a, b=2): return a * b`, what is `f(3)`?", ["3", "5", "6", "An error"], 2,
                     "`b` takes its default of 2, so the result is 3 × 2 = 6."),
            question("Why is `def add(item, items=[])` risky?", ["Lists can't be parameters", "The default list is created once and shared between calls", "It always returns None", "It's slower"], 1,
                     "Default values are evaluated once, when the function is defined, so every call that uses the default appends to the same list."),
        ],
    ),
    "python-collections": lesson(
        "Lists, dictionaries and sets are Python's workhorse collections. Choosing the right one makes code simpler and faster.",
        [
            section(
                "Lists: ordered and changeable",
                "A list keeps items in order and allows duplicates. Indexes start at 0, negative indexes count from the end, and slices take a range. A list comprehension builds a new list in one line.",
                r"""
                tasks = ["write", "test"]
                tasks.append("ship")
                tasks.insert(0, "plan")
                print(tasks[0], tasks[-1])     # plan ship
                print(tasks[1:3])              # ['write', 'test']
                squares = [n * n for n in range(5)]   # [0, 1, 4, 9, 16]
                """,
            ),
            section(
                "Dictionaries and sets",
                "A dict maps unique keys to values and finds a key instantly. Use `.get()` when a key might be missing, to avoid a KeyError. A set stores unique values, which makes it ideal for membership tests and removing duplicates.",
                r"""
                ages = {"ada": 36, "linus": 28}
                ages["grace"] = 45
                print(ages.get("bob", "unknown"))   # unknown
                for name, age in ages.items():
                    print(name, age)

                tags = {"python", "web", "python"}
                print(len(tags))          # 2: duplicates are dropped
                print("web" in tags)      # True
                """,
            ),
        ],
        [
            "List: ordered sequence. Dict: key → value lookup. Set: unique items and fast `in` checks.",
            "`dict.get(key, default)` avoids a KeyError for missing keys.",
            "Comprehensions build lists, dicts and sets in one readable line.",
        ],
        r"""
        contacts: dict[str, str] = {}


        def add(name: str, phone: str) -> None:
            contacts[name.lower()] = phone


        def find(name: str) -> str:
            return contacts.get(name.lower(), "Not found")


        def list_all() -> None:
            for name in sorted(contacts):
                print(f"{name.title()}: {contacts[name]}")


        add("Ada", "555-0101")
        add("Grace", "555-0199")
        print(find("ada"))      # 555-0101
        print(find("bob"))      # Not found
        list_all()
        """,
        [
            question("Which collection should you use to check quickly whether a username is already taken?", ["list", "set", "tuple", "str"], 1,
                     "Sets check membership in constant time on average, while a list has to scan every item."),
            question("What is `[10, 20, 30, 40][-2]`?", ["20", "30", "40", "An error"], 1,
                     "Negative indexes count from the end: -1 is 40, so -2 is 30."),
            question('What does `{"a": 1}.get("b", 0)` return?', ["None", "A KeyError", "0", "'b'"], 2,
                     "`.get()` returns the default you pass (0) when the key isn't present."),
        ],
    ),
    "python-files-errors": lesson(
        "Read and write files safely with `with`, and handle problems such as missing files with try/except, so your program fails with a helpful message.",
        [
            section(
                "Read and write files",
                'Opening a file in a `with` block closes it automatically, even if an error happens. Always pass `encoding="utf-8"` for text files. `pathlib.Path` builds paths that work on every operating system.',
                r"""
                from pathlib import Path

                path = Path("notes.txt")
                path.write_text("first line\nsecond line\n", encoding="utf-8")

                with path.open(encoding="utf-8") as file:
                    for line_number, line in enumerate(file, start=1):
                        print(line_number, line.rstrip())
                """,
            ),
            section(
                "Handle errors with try/except",
                "Put code that can fail in a `try` block and catch specific exceptions. Never use a bare `except:`, which also hides real bugs. An `else` block runs when nothing failed, and `finally` always runs.",
                r"""
                def read_number(path: str) -> int | None:
                    try:
                        with open(path, encoding="utf-8") as file:
                            return int(file.read().strip())
                    except FileNotFoundError:
                        print(f"{path} doesn't exist yet.")
                    except ValueError:
                        print(f"{path} doesn't contain a whole number.")
                    return None
                """,
            ),
        ],
        [
            "Use `with open(...)` so files are always closed.",
            "Catch specific exceptions and tell the user what went wrong and what to do.",
            'Signal your own errors with `raise`, for example `raise ValueError("score must be 0-100")`.',
        ],
        r"""
        from pathlib import Path


        def show_file(name: str) -> None:
            path = Path(name)
            try:
                text = path.read_text(encoding="utf-8")
            except FileNotFoundError:
                print(f"Couldn't find {path.resolve()}. Check the name and folder.")
                return
            except PermissionError:
                print(f"No permission to read {path}.")
                return
            print(f"{path.name}: {len(text.splitlines())} lines")
            print(text)


        show_file(input("File to open: "))
        """,
        [
            question("Why use `with open(...) as f:`?", ["It reads faster", "It closes the file automatically, even after an error", "It's required for writing", "It creates the file if it's missing"], 1,
                     "The `with` block guarantees the file is closed when the block ends, whether it succeeded or raised."),
            question("Which exception does opening a missing file for reading raise?", ["ValueError", "KeyError", "FileNotFoundError", "IndexError"], 2,
                     "Opening a path that doesn't exist raises FileNotFoundError, a subclass of OSError."),
            question("When does a `finally` block run?", ["Only if an exception happened", "Only if no exception happened", "Always", "Never if there's a return"], 2,
                     "`finally` always runs, even after a `return` or an exception, which makes it the place for cleanup."),
        ],
    ),
    "python-classes-tests": lesson(
        "Group data and behaviour into classes, split code into modules, and prove it works with pytest.",
        [
            section(
                "Classes and objects",
                "A class is a blueprint, and each object (instance) made from it has its own data. `__init__` sets up a new object, and `self` refers to the instance a method was called on. `__repr__` controls how the object is displayed.",
                r"""
                class Task:
                    def __init__(self, title: str):
                        self.title = title
                        self.done = False

                    def complete(self) -> None:
                        self.done = True

                    def __repr__(self) -> str:
                        return f"Task({self.title!r}, done={self.done})"


                task = Task("Write tests")
                task.complete()
                print(task)        # Task('Write tests', done=True)
                """,
            ),
            section(
                "Modules and tests",
                "Put related code in a module (a `.py` file) and import it, for example `from tasks import TaskList`. With pytest, a test is a function whose name starts with `test_` and uses plain `assert`. Install it with `pip install pytest`, then run `pytest` in the project folder.",
                r"""
                # test_tasks.py
                from tasks import TaskList


                def test_new_task_is_pending():
                    tasks = TaskList()
                    tasks.add("Read chapter 3")
                    assert tasks.pending() == ["Read chapter 3"]


                def test_complete_removes_task_from_pending():
                    tasks = TaskList()
                    tasks.add("Read chapter 3")
                    tasks.complete("Read chapter 3")
                    assert tasks.pending() == []
                """,
            ),
        ],
        [
            "A class bundles data (attributes) with behaviour (methods).",
            "`self` is the instance; `__init__` initialises it.",
            "Tests are small functions that use `assert`; run them with `pytest`.",
        ],
        r"""
        # tasks.py
        class TaskList:
            def __init__(self) -> None:
                self._tasks: dict[str, bool] = {}

            def add(self, title: str) -> None:
                if not title.strip():
                    raise ValueError("Task title can't be empty")
                self._tasks[title] = False

            def complete(self, title: str) -> None:
                if title not in self._tasks:
                    raise KeyError(f"No task called {title!r}")
                self._tasks[title] = True

            def pending(self) -> list[str]:
                return [title for title, done in self._tasks.items() if not done]


        # test_tasks.py (also add the two tests from the lesson)
        import pytest
        from tasks import TaskList


        def test_empty_title_is_rejected():
            with pytest.raises(ValueError):
                TaskList().add("   ")
        """,
        [
            question("What does `self` refer to inside a method?", ["The class itself", "The instance the method was called on", "The module", "The parent class"], 1,
                     "When you call `task.complete()`, Python passes `task` as `self`."),
            question("How does pytest find tests by default?", ["Functions decorated with @test", "Files and functions whose names start with `test_`", "Any function that uses assert", "Only functions listed in a config file"], 1,
                     "pytest collects `test_*.py` (and `*_test.py`) files and runs the functions in them named `test_*`."),
            question("When is `__init__` called?", ["When the class is defined", "Each time a new instance is created", "When the program ends", "Only when you call it directly"], 1,
                     "`Task('Write tests')` creates a new object and runs `__init__` on it."),
        ],
    ),
}
