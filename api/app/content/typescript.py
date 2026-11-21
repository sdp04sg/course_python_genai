from app.content._build import lesson, question, section

CONTENT = {
    "ts-setup": lesson(
        "TypeScript is JavaScript with types. The compiler checks your code before it runs, then outputs plain JavaScript.",
        [
            section(
                "Install TypeScript",
                "Install Node.js first. Then create a project folder and add TypeScript as a development dependency. `npx` runs the project's local copy of the compiler, `tsc`.",
                r"""
                mkdir ts-start
                cd ts-start
                npm init -y
                npm install --save-dev typescript
                npx tsc --version
                """,
                "powershell",
            ),
            section(
                "Configure strict mode",
                "Create a `tsconfig.json` that turns on `strict`. Strict mode enables the checks that catch the most bugs, such as using a value that might be undefined. Put your `.ts` files in `src/`; `npx tsc` compiles them into `dist/`, and `node dist/hello.js` runs the result.",
                r"""
                {
                  "compilerOptions": {
                    "target": "ES2022",
                    "module": "NodeNext",
                    "strict": true,
                    "outDir": "dist"
                  },
                  "include": ["src"]
                }
                """,
                "json",
            ),
            section(
                "Your first typed file",
                "Annotate parameters and return values. If you call the function with the wrong type, the compiler (and your editor) reports it before the code ever runs.",
                r"""
                // src/hello.ts
                function greet(name: string, times: number = 1): string {
                  return `Hello, ${name}! `.repeat(times)
                }

                console.log(greet('TypeScript', 2))
                // greet(42)  -> error: Argument of type 'number' is not assignable to parameter of type 'string'.
                """,
                "typescript",
            ),
        ],
        [
            "TypeScript checks types at compile time; the output is plain JavaScript.",
            "Turn on `strict` from the start.",
            "`npx tsc` compiles using tsconfig.json; `npx tsc --noEmit` only type-checks.",
        ],
        r"""
        // src/hello.ts   ->   npx tsc   ->   node dist/hello.js
        const learner: string = 'Ada'
        const lessonsDone: number = 3
        const total = 8

        function progressMessage(name: string, done: number, of: number): string {
          const percent = Math.round((done / of) * 100)
          return `${name} has finished ${done}/${of} lessons (${percent}%).`
        }

        console.log(progressMessage(learner, lessonsDone, total))
        """,
        [
            question("What does the TypeScript compiler produce?", ["Machine code", "Plain JavaScript", "Python", "Only WebAssembly"], 1,
                     "Types are erased; browsers and Node.js run the JavaScript output."),
            question("When are TypeScript type errors reported?", ["At compile time, and in your editor as you type", "Only when the code runs", "Never", "Only in production"], 0,
                     "That's the point: mistakes are caught before users ever see them."),
            question("Which command type-checks without writing any output files?", ["npx tsc --noEmit", "npx tsc --watch", "node --check", "npm test"], 0,
                     "`--noEmit` is ideal in CI and in build scripts that use another bundler."),
        ],
        "typescript",
    ),
    "ts-types": lesson(
        "Describe your data with primitive types, arrays and object types, and let type inference fill in the rest.",
        [
            section(
                "Primitives, arrays and inference",
                "The basic types are `string`, `number`, `boolean`, `null` and `undefined`. Arrays are written `string[]` (or `Array<string>`). TypeScript infers types from values, so annotate function parameters and shared shapes rather than every variable.",
                r"""
                let title = 'Python Foundations'          // inferred: string
                const minutes: number[] = [20, 25, 30]
                const tags: readonly string[] = ['beginner', 'python']

                // title = 42   // error: Type 'number' is not assignable to type 'string'
                const total = minutes.reduce((sum, m) => sum + m, 0)   // number
                """,
                "typescript",
            ),
            section(
                "Object types",
                "Describe objects with a `type` alias or an `interface`. Mark optional properties with `?` and fixed ones with `readonly`. When you create an object literal, extra or missing properties are errors.",
                r"""
                type Lesson = {
                  readonly id: string
                  title: string
                  minutes: number
                  completed?: boolean
                }

                interface Course {
                  id: string
                  title: string
                  lessons: Lesson[]
                }

                const course: Course = {
                  id: 'python',
                  title: 'Python Foundations',
                  lessons: [{ id: 'python-setup', title: 'Install Python', minutes: 20 }],
                }
                """,
                "typescript",
            ),
        ],
        [
            "Let inference work; annotate parameters, return types and shared shapes.",
            "Use `?` for optional properties and `readonly` for fixed ones.",
            "`type` and `interface` both describe objects; interfaces can also be extended and merged.",
        ],
        r"""
        interface Lesson {
          readonly id: string
          title: string
          minutes: number
          completed: boolean
        }

        interface Course {
          id: string
          title: string
          level: 'Beginner' | 'Intermediate' | 'Advanced'
          lessons: Lesson[]
        }

        const planner: Course[] = [
          {
            id: 'dsa',
            title: 'Data Structures and Algorithms',
            level: 'Intermediate',
            lessons: [
              { id: 'dsa-big-o', title: 'Big-O', minutes: 35, completed: true },
              { id: 'dsa-arrays', title: 'Two pointers', minutes: 45, completed: false },
            ],
          },
        ]

        const remainingMinutes = planner
          .flatMap((course) => course.lessons)
          .filter((lesson) => !lesson.completed)
          .reduce((sum, lesson) => sum + lesson.minutes, 0)

        console.log(`Minutes left: ${remainingMinutes}`)   // 45
        """,
        [
            question("What type does TypeScript infer for `const ids = ['a', 'b']`?", ["string", "string[]", "any[]", "['a', 'b']"], 1,
                     "Array literals of strings are inferred as `string[]` (use `as const` for a fixed tuple)."),
            question("What does `completed?: boolean` mean?", ["completed is always true", "completed may be missing, so its type is `boolean | undefined`", "completed is read-only", "completed is a string"], 1,
                     "Optional properties can be left out when creating the object."),
            question("Which of these is an error when creating an object of type `Lesson`?", ["Providing every required property", "Adding an extra property the type doesn't declare", "Using a number for minutes", "Using a variable for the title"], 1,
                     "Excess property checks catch typos such as `minuts: 20` in object literals."),
        ],
        "typescript",
    ),
    "ts-unions": lesson(
        "Union types say 'this OR that'. Narrowing tells TypeScript which one you have, so you can model app states safely.",
        [
            section(
                "Unions and narrowing",
                "A union like `string | number` accepts either type. Before using type-specific features, narrow it with `typeof`, `in`, `instanceof`, an equality check or a truthiness check. Literal unions such as `'asc' | 'desc'` restrict a value to a fixed set.",
                r"""
                function format(value: string | number): string {
                  if (typeof value === 'number') {
                    return value.toFixed(1)     // here value is a number
                  }
                  return value.toUpperCase()    // here value is a string
                }

                type SortOrder = 'asc' | 'desc'
                let order: SortOrder = 'asc'
                // order = 'up'   // error
                """,
                "typescript",
            ),
            section(
                "Discriminated unions for UI state",
                "Give each variant a shared literal field, such as `status`. Checking that field narrows the whole object, so you can only read `data` once loading has succeeded. Assigning to `never` in the default case makes the compiler warn you if a new state isn't handled.",
                r"""
                type LoadState<T> =
                  | { status: 'loading' }
                  | { status: 'success'; data: T }
                  | { status: 'error'; message: string }

                function describe(state: LoadState<string[]>): string {
                  switch (state.status) {
                    case 'loading':
                      return 'Loading…'
                    case 'success':
                      return `${state.data.length} lessons`
                    case 'error':
                      return `Failed: ${state.message}`
                    default: {
                      const unreachable: never = state
                      return unreachable
                    }
                  }
                }
                """,
                "typescript",
            ),
        ],
        [
            "Narrow a union before using type-specific members.",
            "Discriminated unions (a shared `status` field) model states without unsafe casts.",
            "Assigning to `never` in the default case turns a missed case into a compile error.",
        ],
        r"""
        interface Task {
          id: number
          title: string
        }

        type TasksState =
          | { status: 'idle' }
          | { status: 'loading' }
          | { status: 'success'; tasks: Task[] }
          | { status: 'error'; message: string }

        function render(state: TasksState): string {
          switch (state.status) {
            case 'idle':
              return 'Press "Load" to fetch tasks.'
            case 'loading':
              return 'Loading tasks…'
            case 'success':
              return state.tasks.length
                ? state.tasks.map((task) => `• ${task.title}`).join('\n')
                : 'No tasks yet.'
            case 'error':
              return `Could not load tasks: ${state.message}`
            default: {
              const unhandled: never = state
              return unhandled
            }
          }
        }

        console.log(render({ status: 'success', tasks: [{ id: 1, title: 'Learn unions' }] }))
        """,
        [
            question("Inside `if (typeof x === 'string')`, what is the type of x if it was declared as `string | number`?", ["string | number", "string", "number", "unknown"], 1,
                     "The typeof check narrows the union inside that branch."),
            question("What makes a union 'discriminated'?", ["It uses classes", "Each member has a common literal property, such as status", "It has exactly two members", "It uses any"], 1,
                     "Checking the shared literal property tells TypeScript exactly which member you have."),
            question("Why assign the value to a `never` variable in the default case?", ["To speed up the switch", "So adding a new state without handling it causes a compile error", "It's required syntax", "To log errors"], 1,
                     "If every case is handled, the value really is `never`; an unhandled state makes the assignment fail."),
        ],
        "typescript",
    ),
    "ts-functions": lesson(
        "Type function inputs and outputs, then use generics to write helpers that work with any type while staying type-safe.",
        [
            section(
                "Typing functions",
                "Annotate parameters and, for exported functions, the return type. Optional parameters use `?` and defaults use `=`. Function types describe callbacks, as in `(lesson: Lesson) => boolean`.",
                r"""
                type Predicate<T> = (item: T) => boolean

                function countWhere<T>(items: T[], test: Predicate<T>): number {
                  let count = 0
                  for (const item of items) if (test(item)) count++
                  return count
                }

                const long = countWhere([20, 45, 60], (minutes) => minutes > 30)   // 2
                """,
                "typescript",
            ),
            section(
                "Generics and constraints",
                "A generic type parameter `<T>` stands for 'whatever type the caller uses'. Constrain it with `extends` when you need certain properties, and use `keyof` to accept only real property names.",
                r"""
                function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
                  return items.map((item) => item[key])
                }

                const lessons = [
                  { id: 'a', minutes: 20 },
                  { id: 'b', minutes: 35 },
                ]
                const ids = pluck(lessons, 'id')            // string[]
                const minutes = pluck(lessons, 'minutes')   // number[]
                // pluck(lessons, 'title')   // error: 'title' is not a key
                """,
                "typescript",
            ),
        ],
        [
            "Annotate parameters; let small local functions infer their return types.",
            "Generics keep the link between input and output types.",
            "`K extends keyof T` limits a parameter to real property names.",
        ],
        r"""
        interface Lesson {
          id: string
          module: string
          title: string
        }

        function groupBy<T, K extends PropertyKey>(items: T[], keyOf: (item: T) => K): Record<K, T[]> {
          const groups = {} as Record<K, T[]>
          for (const item of items) {
            const key = keyOf(item)
            const group = groups[key] ?? []
            group.push(item)
            groups[key] = group
          }
          return groups
        }

        const lessons: Lesson[] = [
          { id: 'dsa-big-o', module: 'Efficiency', title: 'Big-O' },
          { id: 'dsa-builtins', module: 'Efficiency', title: 'Built-in costs' },
          { id: 'dsa-arrays', module: 'Linear structures', title: 'Two pointers' },
        ]

        const byModule = groupBy(lessons, (lesson) => lesson.module)
        console.log(Object.keys(byModule))           // ['Efficiency', 'Linear structures']
        console.log(byModule['Efficiency'].length)   // 2
        """,
        [
            question("In `function first<T>(items: T[]): T | undefined`, what is T when it's called with `['a', 'b']`?", ["any", "string", "unknown", "T"], 1,
                     "TypeScript infers T from the argument: an array of strings makes T `string`."),
            question("What does `K extends keyof T` guarantee?", ["K is a number", "K is one of T's property names", "K is optional", "T has no keys"], 1,
                     "`keyof T` is the union of T's property names, and `extends` limits K to that union."),
            question("How do you type a callback that takes a number and returns nothing?", ["(n: number) => void", "function(number)", "Callback<number>", "(number): void"], 0,
                     "Arrow-style function types list the parameters, then `=>` and the return type."),
        ],
        "typescript",
    ),
    "ts-dom": lesson(
        "Use TypeScript's DOM types to find elements, render content safely and respond to user events.",
        [
            section(
                "Query elements with types",
                "`document.querySelector` returns `Element | null`. Pass a type parameter (or use a tag selector) to get the specific element type, and handle `null` before using it. Strict mode makes you.",
                r"""
                const list = document.querySelector<HTMLUListElement>('#lessons')
                const button = document.querySelector<HTMLButtonElement>('#add')

                if (!list || !button) {
                  throw new Error('Expected #lessons and #add in the page')
                }

                button.addEventListener('click', (event: MouseEvent) => {
                  button.disabled = true
                  console.log('clicked at', event.clientX)
                })
                """,
                "typescript",
            ),
            section(
                "Render safely",
                "Never put user-provided text into `innerHTML`: it can run scripts (cross-site scripting, or XSS). Create elements and set `textContent`, or escape the text first. This app's `escapeHtml` helper does exactly that.",
                r"""
                function renderLessons(list: HTMLUListElement, titles: string[]): void {
                  list.replaceChildren(
                    ...titles.map((title) => {
                      const item = document.createElement('li')
                      item.textContent = title     // treated as text, never as HTML
                      return item
                    }),
                  )
                }
                """,
                "typescript",
            ),
        ],
        [
            "`querySelector` can return null, so check before using the element.",
            "Use `textContent`, not `innerHTML`, for user-provided text.",
            "Type event handlers (MouseEvent, KeyboardEvent, SubmitEvent) to get the right properties.",
        ],
        r"""
        // index.html: <ul id="lessons"></ul> <input id="title" /> <button id="add">Add</button>
        const list = document.querySelector<HTMLUListElement>('#lessons')
        const input = document.querySelector<HTMLInputElement>('#title')
        const addButton = document.querySelector<HTMLButtonElement>('#add')
        if (!list || !input || !addButton) throw new Error('Page is missing elements')

        const lessons: string[] = ['Install Python', 'Variables and types']

        const render = (): void => {
          list.replaceChildren(
            ...lessons.map((title, index) => {
              const item = document.createElement('li')
              item.textContent = `${index + 1}. ${title}`
              return item
            }),
          )
        }

        addButton.addEventListener('click', () => {
          const title = input.value.trim()
          if (!title) return
          lessons.push(title)
          input.value = ''
          render()
        })

        render()
        """,
        [
            question("What does `document.querySelector('#x')` return when nothing matches?", ["undefined", "null", "An empty element", "It throws"], 1,
                     "That's why the return type includes `| null`."),
            question("Why avoid `element.innerHTML = userText`?", ["It's slow", "The text could contain HTML or scripts that run (XSS)", "It doesn't work in TypeScript", "It removes styles"], 1,
                     "`textContent` treats the value as plain text, so nothing in it can execute."),
            question("Which approach lets you read `input.value` without a type error?", ["`document.querySelector('#title')`", "`document.querySelector<HTMLInputElement>('#title')` followed by a null check", "`document.getElementById('title').value`", "`window.title`"], 1,
                     "The type parameter gives the element type, and the null check removes `| null`."),
        ],
        "typescript",
    ),
    "ts-fetch": lesson(
        "Call your FastAPI backend with fetch, check the response, type the JSON and show loading and error states.",
        [
            section(
                "fetch and response.ok",
                "`fetch` only rejects on network failures. A 404 or 500 still resolves, so always check `response.ok`. `response.json()` returns `any`, so give it a type, and validate data you don't control.",
                r"""
                interface Task {
                  id: number
                  title: string
                  done: boolean
                }

                async function getTasks(): Promise<Task[]> {
                  const response = await fetch('/api/tasks')
                  if (!response.ok) {
                    throw new Error(`Request failed: ${response.status}`)
                  }
                  return (await response.json()) as Task[]
                }
                """,
                "typescript",
            ),
            section(
                "Show every state",
                "Users should see something while loading, a clear message on failure, and the data on success. During development, Vite's proxy forwards `/api` to FastAPI, so the browser sees a single origin and you need no CORS setup; this project's `vite.config.ts` does exactly that.",
                r"""
                const output = document.querySelector<HTMLDivElement>('#tasks')

                async function showTasks(): Promise<void> {
                  if (!output) return
                  output.textContent = 'Loading…'
                  try {
                    const tasks = await getTasks()
                    output.textContent = tasks.length
                      ? tasks.map((task) => `${task.done ? '✓' : '○'} ${task.title}`).join('\n')
                      : 'No tasks yet.'
                  } catch (error) {
                    output.textContent = error instanceof Error ? error.message : 'Something went wrong.'
                  }
                }
                """,
                "typescript",
            ),
        ],
        [
            "fetch doesn't throw on HTTP errors, so check `response.ok`.",
            "Type the JSON you expect, and validate anything that comes from outside.",
            "Always render loading, error and empty states.",
        ],
        r"""
        interface Task {
          id: number
          title: string
          done: boolean
        }

        type State =
          | { status: 'loading' }
          | { status: 'success'; tasks: Task[] }
          | { status: 'error'; message: string }

        const root = document.querySelector<HTMLDivElement>('#app')
        if (!root) throw new Error('Missing #app')

        const render = (state: State): void => {
          root.replaceChildren()
          const message = document.createElement('p')
          if (state.status === 'loading') message.textContent = 'Loading tasks…'
          if (state.status === 'error') message.textContent = `Could not load tasks: ${state.message}`
          if (state.status === 'success') {
            if (!state.tasks.length) message.textContent = 'No tasks yet. Add one with POST /tasks.'
            const list = document.createElement('ul')
            for (const task of state.tasks) {
              const item = document.createElement('li')
              item.textContent = `${task.done ? '✓' : '○'} ${task.title}`
              list.append(item)
            }
            root.append(list)
          }
          root.prepend(message)
        }

        const load = async (): Promise<void> => {
          render({ status: 'loading' })
          try {
            const response = await fetch('/api/tasks', { signal: AbortSignal.timeout(5000) })
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            render({ status: 'success', tasks: (await response.json()) as Task[] })
          } catch (error) {
            render({ status: 'error', message: error instanceof Error ? error.message : 'Unknown error' })
          }
        }

        void load()
        """,
        [
            question("`fetch('/api/missing')` gets a 404 response. What happens?", ["The promise rejects", "The promise resolves with `response.ok === false`", "It retries automatically", "It returns null"], 1,
                     "Only network failures (and aborts) reject; HTTP error statuses resolve normally."),
            question("What type does `response.json()` give you without an annotation?", ["unknown", "`Promise<any>`, so you should add a type", "object", "string"], 1,
                     "`any` switches type checking off, so describe the shape you expect."),
            question("Why use Vite's proxy for `/api` during development?", ["To compress responses", "The browser sees one origin, so no CORS setup is needed", "To cache API calls", "fetch requires it"], 1,
                     "Requests go to the Vite server, which forwards them to FastAPI behind the scenes."),
        ],
        "typescript",
    ),
    "ts-async": lesson(
        "Promises represent work that finishes later. async/await makes that code read from top to bottom while staying non-blocking.",
        [
            section(
                "Promises and async/await",
                "An `async` function always returns a Promise. `await` pauses that function, not the page, until the promise settles. Handle failures with try/catch, and run independent requests in parallel with `Promise.all`.",
                r"""
                const wait = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms))

                async function loadDashboard(): Promise<void> {
                  await wait(200)                                  // sequential: waits first
                  const [courses, progress] = await Promise.all([  // parallel: both at once
                    fetch('/api/courses').then((r) => r.json()),
                    fetch('/api/progress').then((r) => r.json()),
                  ])
                  console.log(courses, progress)
                }
                """,
                "typescript",
            ),
            section(
                "Forms: prevent double submits",
                "Disable the form's button while a request is in flight and re-enable it in `finally`, so the form recovers after both success and failure. `Promise.allSettled` is useful when some requests may fail and you still want the others' results.",
                r"""
                form.addEventListener('submit', async (event: SubmitEvent) => {
                  event.preventDefault()
                  submitButton.disabled = true
                  try {
                    await saveTask(String(new FormData(form).get('title')))
                    form.reset()
                  } catch (error) {
                    alert(error instanceof Error ? error.message : 'Save failed')
                  } finally {
                    submitButton.disabled = false
                  }
                })
                """,
                "typescript",
            ),
        ],
        [
            "`await` pauses only the async function, never the whole page.",
            "Use `Promise.all` for independent requests; it rejects if any of them fails.",
            "Re-enable buttons in `finally` so the UI recovers from errors.",
        ],
        r"""
        const form = document.querySelector<HTMLFormElement>('#task-form')
        const submit = form?.querySelector<HTMLButtonElement>('button[type="submit"]')
        const status = document.querySelector<HTMLParagraphElement>('#status')
        if (!form || !submit || !status) throw new Error('Missing form elements')

        const saveTask = async (title: string): Promise<void> => {
          const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title }),
          })
          if (!response.ok) throw new Error(`Save failed (${response.status})`)
        }

        form.addEventListener('submit', async (event) => {
          event.preventDefault()
          const title = String(new FormData(form).get('title') ?? '').trim()
          if (!title) {
            status.textContent = 'Please enter a title.'
            return
          }
          submit.disabled = true
          status.textContent = 'Saving…'
          try {
            await saveTask(title)
            form.reset()
            status.textContent = 'Saved!'
          } catch (error) {
            status.textContent = error instanceof Error ? error.message : 'Save failed'
          } finally {
            submit.disabled = false
          }
        })
        """,
        [
            question("What does an `async` function return?", ["Its value directly", "A Promise", "undefined", "A callback"], 1,
                     "Even `async function f() { return 1 }` returns `Promise<number>`."),
            question("What happens with `Promise.all([a, b])` if b rejects?", ["It resolves with a's value", "It rejects with b's error", "It waits forever", "It returns [a, undefined]"], 1,
                     "Use `Promise.allSettled` when you want every result regardless of failures."),
            question("Why re-enable the submit button in `finally`?", ["It runs faster", "It runs after both success and failure, so the form never stays stuck", "finally is required", "To reset the form"], 1,
                     "If you only re-enable it after success, one failed request leaves the form unusable."),
        ],
        "typescript",
    ),
    "ts-build": lesson(
        "Strict compiler settings catch whole classes of bugs. Make type-checking part of your build so broken code never ships.",
        [
            section(
                "Strict options worth enabling",
                "`strict` turns on null checks, no implicit `any` and more. `noUnusedLocals`, `noUnusedParameters` and `noFallthroughCasesInSwitch` catch dead code and missing `break`s. `noUncheckedIndexedAccess` makes `array[i]` possibly undefined: strict, but it finds real bugs. This is this project's own tsconfig.json:",
                r"""
                {
                  "compilerOptions": {
                    "target": "ES2022",
                    "module": "ESNext",
                    "moduleResolution": "bundler",
                    "strict": true,
                    "noUnusedLocals": true,
                    "noUnusedParameters": true,
                    "noFallthroughCasesInSwitch": true,
                    "noEmit": true
                  },
                  "include": ["src"]
                }
                """,
                "json",
            ),
            section(
                "Type-check, then build",
                "Vite strips types without checking them, so run `tsc --noEmit` before building. This project's `npm run build` does both (`tsc --noEmit && vite build`), so a type error stops the build. The resulting `dist/` folder is what you deploy.",
                r"""
                {
                  "scripts": {
                    "dev": "vite",
                    "typecheck": "tsc --noEmit",
                    "build": "tsc --noEmit && vite build",
                    "preview": "vite preview"
                  }
                }
                """,
                "json",
            ),
        ],
        [
            "Enable `strict` from day one; adding it later is much harder.",
            "Vite doesn't type-check, so run `tsc --noEmit` in your build and in CI.",
            "Fix errors rather than silencing them with `any` or `@ts-ignore`.",
        ],
        r"""
        // Before (fails under strict):
        //   function total(items) { return items.reduce((s, i) => s + i.minutes, 0) }
        //   const first = lessons.find(l => l.id === 'x'); console.log(first.title)

        interface Lesson {
          id: string
          title: string
          minutes: number
        }

        // After: parameters are typed and the possibly-undefined result is handled
        function total(items: Lesson[]): number {
          return items.reduce((sum, item) => sum + item.minutes, 0)
        }

        const lessons: Lesson[] = [{ id: 'ts-build', title: 'Build for production', minutes: 30 }]
        const first = lessons.find((lesson) => lesson.id === 'ts-build')
        console.log(first ? first.title : 'Not found', total(lessons))

        // Then: npm run typecheck && npm run build, and deploy the dist/ folder
        """,
        [
            question("Does Vite type-check your TypeScript during `vite build`?", ["Yes, always", "No; it strips types, so run `tsc --noEmit` separately", "Only in dev mode", "Only with React"], 1,
                     "Vite uses esbuild to remove types quickly, without checking them."),
            question("Under `strict`, what is the type of `lessons.find(...)`?", ["Lesson", "Lesson | undefined", "any", "Lesson[]"], 1,
                     "find returns undefined when nothing matches, so you must handle that case."),
            question("What does `noUnusedLocals` report?", ["Unused npm packages", "Variables that are declared but never used", "Unused CSS", "Slow code"], 1,
                     "Unused variables are often leftovers or signs of a bug."),
        ],
        "typescript",
    ),
}
