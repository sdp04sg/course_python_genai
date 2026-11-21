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
