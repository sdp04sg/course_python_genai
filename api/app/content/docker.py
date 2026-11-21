from app.content._build import lesson, question, section

CONTENT = {
    "docker-intro": lesson(
        "A container packages an app with everything it needs to run (code, runtime, libraries), so it behaves the same on every machine.",
        [
            section(
                "Containers vs virtual machines",
                "A virtual machine runs a complete guest operating system on virtual hardware. A container shares the host's kernel and isolates only processes, files and networking, so it starts in about a second and uses far less memory.\n\n"
                "An **image** is a read-only template: an operating-system base plus your app and its dependencies. A **container** is a running (or stopped) instance of an image. You can start many containers from one image.",
            ),
            section(
                "Install Docker and say hello",
                "On Windows, install Docker Desktop and use the WSL 2 backend when asked. On macOS install Docker Desktop, and on Linux install Docker Engine. Then check that everything works:",
                r"""
                docker --version
                docker run hello-world
                docker run --rm python:3.12-slim python -c "print('Hello from a container')"
                """,
                "powershell",
            ),
        ],
        [
            "Image = template; container = a running instance of it.",
            "Containers share the host kernel, so they're much lighter than VMs.",
            "`docker run` downloads (pulls) the image first if you don't have it yet.",
        ],
        r"""
        docker --version
        docker run hello-world
        # It printed "Hello from Docker!": Docker pulled the image, created a
        # container, ran it, and the container exited.

        docker ps -a        # the stopped hello-world container is listed
        docker images       # the hello-world image is stored locally

        # Container vs VM in one sentence: a VM virtualises hardware and boots a
        # full operating system; a container isolates processes on the host's
        # kernel, so it starts in seconds and is much smaller.
        """,
        [
            question("What's the difference between an image and a container?", ["They're the same thing", "An image is a read-only template; a container is a running instance of it", "A container is a template", "Images run and containers are stored"], 1,
                     "Think of the image as a class and containers as its instances."),
            question("Why do containers start faster than virtual machines?", ["They use better CPUs", "They share the host kernel instead of booting a whole operating system", "They're compiled", "They skip networking"], 1,
                     "There's no guest OS to boot, only processes to start."),
            question("What does Docker Desktop on Windows use to run Linux containers?", ["Nothing; Windows runs them natively", "WSL 2 (or Hyper-V)", "VirtualBox", "A cloud server"], 1,
                     "WSL 2 provides a real Linux kernel for the containers."),
        ],
        "shell",
    ),
    "docker-run": lesson(
        "Run containers in the background, publish their ports, read their logs, step inside them and clean up afterwards.",
        [
            section(
                "Run, list, stop and remove",
                "`-d` runs a container in the background, `--name` gives it a memorable name, and `-p HOST:CONTAINER` publishes a port. `docker ps` lists running containers (add `-a` to include stopped ones). `--rm` deletes the container automatically when it stops.",
                r"""
                docker run -d --name web -p 8080:80 nginx
                docker ps
                docker stop web
                docker start web
                docker rm -f web          # stop and remove in one step
                """,
                "shell",
            ),
            section(
                "Logs and a shell inside",
                "`docker logs` shows what the container printed (`-f` follows new output). `docker exec -it NAME sh` opens a shell inside a running container, which is great for debugging, but any change you make there is lost when the container is removed.",
                r"""
                docker logs -f web        # Ctrl+C stops following
                docker exec -it web sh
                # inside the container:
                ls /usr/share/nginx/html
                exit
                docker stats --no-stream  # CPU and memory per container
                """,
                "shell",
            ),
        ],
        [
            "`-p 8080:80` maps port 8080 on your computer to port 80 in the container.",
            "`docker logs` and `docker exec` are your main debugging tools.",
            "Containers are disposable: remove and recreate them rather than patching by hand.",
        ],
        r"""
        docker run -d --name web -p 8080:80 nginx
        # Open http://localhost:8080 to see the nginx welcome page

        docker logs web                  # shows the GET / request you just made
        docker exec -it web sh
        echo "<h1>Hello from inside</h1>" > /usr/share/nginx/html/index.html
        exit
        # Refresh the browser: the page changed (only in this container)

        docker stop web
        docker rm web
        docker ps -a                     # web is gone
        """,
        [
            question("With `docker run -p 3000:8000 app`, which port do you open in your browser?", ["8000", "3000", "80", "Either"], 1,
                     "The format is HOST:CONTAINER, so the host side is 3000."),
            question("Which command opens a shell in a running container named api?", ["docker run api sh", "docker exec -it api sh", "docker attach --shell api", "docker logs api sh"], 1,
                     "`exec` runs an extra process in an existing container; `-it` connects your terminal."),
            question("What does `--rm` do?", ["Removes the image", "Deletes the container automatically when it stops", "Restarts it on failure", "Runs it as root"], 1,
                     "Handy for one-off commands and experiments, so stopped containers don't pile up."),
        ],
        "shell",
    ),
    "docker-images": lesson(
        "Images are built from layers, named with tags, and shared through registries such as Docker Hub and GitHub Container Registry.",
        [
            section(
                "Pull, tag and inspect",
                "A full image name is `registry/namespace/repository:tag`. Without a registry, Docker uses Docker Hub; without a tag, it uses `latest`, which is just a name, not a guarantee of the newest version. Pin exact tags such as `python:3.12-slim` for repeatable builds.",
                r"""
                docker pull python:3.12
                docker pull python:3.12-slim
                docker images python                 # compare the SIZE column
                docker image history python:3.12-slim
                docker tag python:3.12-slim myname/python-base:1.0
                """,
                "shell",
            ),
            section(
                "Layers and cleanup",
                "Each image is a stack of read-only layers, and images that share layers store them only once. A container adds a thin writable layer on top. Unused images and stopped containers pile up, so clean them up occasionally.",
                r"""
                docker system df          # disk used by images, containers and volumes
                docker image prune        # remove dangling (untagged) images
                docker system prune       # also remove stopped containers and unused networks
                """,
                "shell",
            ),
        ],
        [
            "Pin specific tags; `latest` is only a default name.",
            "Slim and alpine variants are much smaller but include fewer tools.",
            "Layers are shared and cached, which saves disk space and build time.",
        ],
        r"""
        docker pull python:3.12
        docker pull python:3.12-slim
        docker images python
        # REPOSITORY   TAG         SIZE
        # python       3.12        roughly 1 GB     (full Debian with build tools)
        # python       3.12-slim   roughly 150 MB   (minimal Debian)

        docker image history python:3.12-slim
        # Each line is a layer: the base OS, then Python, pip and environment settings.

        # Use slim for most apps. Use the full image only if you need compilers to
        # build packages that don't ship pre-built wheels.
        """,
        [
            question("Which tag does `docker pull nginx` download?", ["The newest version, guaranteed", "The tag named latest", "All tags", "None"], 1,
                     "`latest` is whatever the publisher last tagged that way, which may not be the newest release."),
            question("How can two images share disk space?", ["Compression", "They share identical read-only layers", "Docker deduplicates containers", "They can't"], 1,
                     "Two images built on the same base reuse its layers."),
            question("What's a good reason to choose `python:3.12-slim` over `python:3.12`?", ["It's a newer Python", "A much smaller image: faster to pull and less to patch", "It includes more tools", "It runs on Windows"], 1,
                     "Fewer packages also means fewer potential vulnerabilities."),
        ],
        "shell",
    ),
    "docker-dockerfile": lesson(
        "A Dockerfile is a recipe for building your own image: start from a base, copy your code, install dependencies and say how to start the app.",
        [
            section(
                "The core instructions",
                "`FROM` picks the base image, `WORKDIR` sets the working folder, `COPY` adds files, `RUN` executes a command while the image is built, and `CMD` sets the default command when a container starts. Build with `docker build -t name .`; the final `.` is the build context, the folder sent to Docker.",
                r"""
                FROM python:3.12-slim
                WORKDIR /app
                COPY hello.py .
                CMD ["python", "hello.py"]
                """,
                "dockerfile",
            ),
            section(
                "Build and run",
                "Tag images with a name and a version. Add `-it` for programs that read keyboard input, and `--rm` so test containers clean up after themselves.",
                r"""
                docker build -t hello-app:1.0 .
                docker run --rm hello-app:1.0
                docker run --rm -it hello-app:1.0     # for interactive programs that use input()
                """,
                "shell",
            ),
        ],
        [
            "`RUN` happens at build time; `CMD` runs when a container starts.",
            'Use the exec form, `CMD ["python", "app.py"]`, so signals such as Ctrl+C reach your app.',
            "`-it` connects your keyboard and terminal to the container.",
        ],
        r"""
        # Dockerfile, next to guess.py from Python Foundations
        FROM python:3.12-slim
        WORKDIR /app
        COPY guess.py .
        CMD ["python", "guess.py"]

        # Build and play:
        #   docker build -t guess-game:1.0 .
        #   docker run --rm -it guess-game:1.0
        # Without -it, input() has no keyboard to read from and raises EOFError.
        """,
        [
            question("Which instruction runs while the image is being built?", ["CMD", "RUN", "ENTRYPOINT", "EXPOSE"], 1,
                     "RUN's results are saved into the image; CMD only records what to run later."),
            question("What does the `.` mean in `docker build -t app .`?", ["The current user", "The build context: the folder sent to Docker", "The latest tag", "Hidden files"], 1,
                     "COPY instructions can only read files from the build context."),
            question("Your containerized game crashes with EOFError on `input()`. What's missing?", ["-d", "-it", "-p", "--rm"], 1,
                     "`-i` keeps standard input open and `-t` allocates a terminal."),
        ],
        "dockerfile",
    ),
    "docker-layers": lesson(
        "Each Dockerfile instruction creates a cached layer. Order instructions from least to most frequently changed, and rebuilds take seconds instead of minutes.",
        [
            section(
                "How the build cache works",
                "Docker reuses a layer if its instruction and inputs haven't changed. Once one layer changes, every layer after it is rebuilt. So copy the dependency list and install dependencies before copying your source code, which changes far more often.",
                r"""
                FROM python:3.12-slim
                WORKDIR /app

                # 1. Dependencies: rebuilt only when requirements.txt changes
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt

                # 2. Source code: changes often, so it comes last
                COPY . .
                CMD ["python", "main.py"]
                """,
                "dockerfile",
            ),
            section(
                ".dockerignore",
                "The build context is everything in the folder you build from. A `.dockerignore` file keeps out things that are large, secret or irrelevant (virtual environments, node_modules, .git, .env files), which makes builds faster and images safer. This project has one at its root.",
                r"""
                .venv/
                __pycache__/
                node_modules/
                .git/
                .env
                *.sqlite3
                """,
                "text",
            ),
        ],
        [
            "Put rarely changing steps (dependencies) before frequently changing ones (code).",
            "A changed layer invalidates every layer after it.",
            "Always add a .dockerignore, especially to keep .env files out.",
        ],
        r"""
        # Before: every code change reinstalls every dependency
        #   FROM python:3.12-slim
        #   WORKDIR /app
        #   COPY . .
        #   RUN pip install -r requirements.txt
        #   CMD ["python", "main.py"]

        # After:
        FROM python:3.12-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY . .
        CMD ["python", "main.py"]

        # Measure it in PowerShell:
        #   Measure-Command { docker build -t app . }   # first build: slow
        #   (edit main.py)
        #   Measure-Command { docker build -t app . }   # seconds: the pip layer is CACHED
        """,
        [
            question("You change one line in main.py. With the good ordering, which steps run again?", ["All of them", "Only `COPY . .` and the steps after it", "Only FROM", "None"], 1,
                     "The dependency layers are unchanged, so Docker reuses them from the cache."),
            question("Why add `.env` to .dockerignore?", ["It's large", "So secrets aren't copied into the image, where anyone with the image could read them", "Docker can't read it", "It speeds up Python"], 1,
                     "Anything in the build context can end up in a layer."),
            question("What does `pip install --no-cache-dir` save?", ["Build time", "Image size, by not keeping pip's download cache", "Network traffic", "Nothing"], 1,
                     "pip's cache is useless inside an image and can add many megabytes."),
        ],
        "dockerfile",
    ),
    "docker-fastapi": lesson(
        "Containerize a FastAPI app: listen on all interfaces, publish the port, pass configuration as environment variables and add a health check.",
        [
            section(
                "A Dockerfile for an API",
                "Inside a container the server must listen on `0.0.0.0`, not `127.0.0.1`, or nothing outside the container can reach it. Read settings from environment variables, so one image works everywhere. `HEALTHCHECK` tells Docker, and you, whether the app is actually responding. (Hosts such as Render pass the port in `$PORT`; this app's own Dockerfile shows how to use it.)",
                r"""
                FROM python:3.12-slim
                WORKDIR /app
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt
                COPY app ./app
                EXPOSE 8000
                HEALTHCHECK --interval=30s --timeout=3s \
                  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
                CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
                """,
                "dockerfile",
            ),
            section(
                "Run it with configuration",
                "Pass settings with `-e NAME=value`, or a whole file with `--env-file .env`; the file stays on your machine, outside the image. `docker ps` shows the health status once the first check has run.",
                r"""
                docker build -t tasks-api:1.0 .
                docker run -d --name api -p 8000:8000 --env-file .env tasks-api:1.0
                docker ps                      # STATUS shows (healthy) after about 30 seconds
                curl http://localhost:8000/health
                docker logs api
                """,
                "shell",
            ),
        ],
        [
            "Listen on 0.0.0.0 inside containers.",
            "Configuration goes in environment variables, never baked into the image.",
            "A HEALTHCHECK turns 'running' into 'actually working'.",
        ],
        r"""
        # Dockerfile
        FROM python:3.12-slim
        ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY app ./app
        EXPOSE 8000
        HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
          CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

        # app/main.py needs a GET /health route that returns {"status": "ok"}, and
        # settings read with os.environ.get("APP_NAME", "Tasks API").
        #
        #   docker build -t tasks-api:1.0 .
        #   docker run -d --name api -p 8000:8000 -e APP_NAME="My Tasks" tasks-api:1.0
        #   docker ps   ->   STATUS: Up 1 minute (healthy)
        """,
        [
            question("Uvicorn listens on 127.0.0.1 inside a container started with `-p 8000:8000`. What happens when you open localhost:8000?", ["It works", "The connection fails: the server only accepts connections from inside the container", "It redirects", "It's slower"], 1,
                     "127.0.0.1 inside the container is the container's own loopback, not your computer's."),
            question("What's the best way to give an API key to a container?", ["COPY .env into the image", "Set ENV API_KEY=... in the Dockerfile", "Pass it at run time with -e or --env-file", "Hard-code it"], 2,
                     "Run-time configuration keeps the secret out of every image layer."),
            question("What does HEALTHCHECK add?", ["Automatic HTTPS", "A periodic check that marks the container healthy or unhealthy", "Log rotation", "Auto-scaling"], 1,
                     "Orchestrators and `docker ps` use the status to spot apps that are running but broken."),
        ],
        "dockerfile",
    ),
    "docker-volumes": lesson(
        "A container's own filesystem is thrown away with the container. Volumes and bind mounts keep data and share files with your computer.",
        [
            section(
                "Named volumes",
                "A named volume is storage that Docker manages and that outlives any container. Mount it where your app writes data, such as the folder holding a SQLite database. It's the container equivalent of the persistent disk this app uses on Render.",
                r"""
                docker volume create tasks-data
                docker run -d --name api -p 8000:8000 -v tasks-data:/data -e DB_PATH=/data/tasks.db tasks-api:1.0
                docker volume ls
                docker volume inspect tasks-data
                """,
                "shell",
            ),
            section(
                "Bind mounts for development",
                "A bind mount maps a folder on your computer into the container, so your edits appear inside it immediately, which pairs well with `--reload` during development. In production, prefer named volumes, which don't depend on the host's folder layout.",
                r"""
                # PowerShell: ${PWD} is the current folder
                docker run --rm -p 8000:8000 -v "${PWD}/app:/app/app" tasks-api:1.0 uvicorn app.main:app --host 0.0.0.0 --reload
                """,
                "powershell",
            ),
        ],
        [
            "Data written inside a container's own filesystem disappears when the container is removed.",
            "Use named volumes for data and bind mounts for live code during development.",
            "Back up volumes like any other important data.",
        ],
        r"""
        docker volume create tasks-data
        docker run -d --name api -p 8000:8000 -v tasks-data:/data -e DB_PATH=/data/tasks.db tasks-api:1.0
        # Create a task at http://localhost:8000/docs (POST /tasks)

        docker rm -f api                 # the container is gone...
        docker run -d --name api -p 8000:8000 -v tasks-data:/data -e DB_PATH=/data/tasks.db tasks-api:1.0
        curl http://localhost:8000/tasks # ...but the task is still there

        # Without -v, the database lived in the container and the list would now be empty.
        """,
        [
            question("You remove a container that stored data in its own filesystem. What happens to the data?", ["It's kept in the image", "It's lost", "It moves to a volume", "It's uploaded"], 1,
                     "The writable layer is deleted with the container."),
            question("Which suits live code editing during development?", ["A named volume", "A bind mount", "COPY", "An image layer"], 1,
                     "A bind mount shows your local files inside the container as you edit them."),
            question("In `-v tasks-data:/data`, what is `/data`?", ["A folder on your computer", "The path inside the container where the volume appears", "The volume's name", "A URL"], 1,
                     "The format is VOLUME:CONTAINER_PATH."),
        ],
        "shell",
    ),
    "docker-compose": lesson(
        "Docker Compose describes a multi-container app (API, database, cache) in one YAML file and starts it with one command.",
        [
            section(
                "compose.yaml",
                "Each service becomes a container. Services in the same Compose project share a network and reach each other by service name: the API connects to the host `db`, not `localhost`. A named volume keeps the database's data.",
                r"""
                services:
                  api:
                    build: .
                    ports:
                      - "8000:8000"
                    environment:
                      DATABASE_URL: postgresql://app:${POSTGRES_PASSWORD}@db:5432/tasks
                    depends_on:
                      - db
                  db:
                    image: postgres:16
                    environment:
                      POSTGRES_USER: app
                      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
                      POSTGRES_DB: tasks
                    volumes:
                      - pgdata:/var/lib/postgresql/data

                volumes:
                  pgdata:
                """,
                "yaml",
            ),
            section(
                "Everyday commands",
                "`docker compose up` builds and starts everything, and `-d` runs it in the background. `logs`, `ps` and `exec` work per service. `down` stops and removes the containers and networks but keeps named volumes; add `-v` to delete those too.",
                r"""
                docker compose up -d --build
                docker compose ps
                docker compose logs -f api
                docker compose exec db psql -U app -d tasks
                docker compose down
                """,
                "shell",
            ),
        ],
        [
            "Services reach each other by service name on Compose's network.",
            "`depends_on` controls start order, not readiness.",
            "Never commit real passwords in compose.yaml; put them in an .env file or a secret store.",
        ],
        r"""
        # compose.yaml (as in the lesson), plus .env next to it, not committed:
        #   POSTGRES_PASSWORD=change-me

        # In the API, read the connection string from the environment, e.g. with psycopg:
        #   conn = psycopg.connect(os.environ["DATABASE_URL"])

        services:
          api:
            build: .
            ports:
              - "8000:8000"
            environment:
              DATABASE_URL: postgresql://app:${POSTGRES_PASSWORD}@db:5432/tasks
            depends_on:
              - db
          db:
            image: postgres:16
            environment:
              POSTGRES_USER: app
              POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
              POSTGRES_DB: tasks
            volumes:
              - pgdata:/var/lib/postgresql/data

        volumes:
          pgdata:

        # Run: docker compose up -d --build, then docker compose logs -f api
        """,
        [
            question("From the api container, which host name reaches the database service `db`?", ["localhost", "db", "127.0.0.1", "host.docker.internal"], 1,
                     "Compose's built-in DNS resolves each service name to its container."),
            question("Does `depends_on: [db]` wait until Postgres accepts connections?", ["Yes", "No; it only orders startup unless you add a health condition", "Only on Linux", "Only with -d"], 1,
                     "The next lesson adds a healthcheck and `condition: service_healthy`."),
            question("What does `docker compose down` keep by default?", ["Containers", "Named volumes", "Networks", "Nothing"], 1,
                     "Your database data survives `down`; `down -v` removes it too."),
        ],
        "yaml",
    ),
    "docker-compose-dev": lesson(
        "Make development with Compose smooth: wait for healthy dependencies, reload code instantly and understand Compose networking.",
        [
            section(
                "Health checks and depends_on conditions",
                "Give the database a healthcheck, then make the API wait for `condition: service_healthy`. Your app should still retry its first connection, because databases can restart at any time.",
                r"""
                services:
                  db:
                    image: postgres:16
                    environment:
                      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
                    healthcheck:
                      test: ["CMD-SHELL", "pg_isready -U postgres"]
                      interval: 5s
                      timeout: 3s
                      retries: 10
                  api:
                    build: .
                    depends_on:
                      db:
                        condition: service_healthy
                """,
                "yaml",
            ),
            section(
                "Live reload with compose watch",
                "`docker compose watch` syncs changed files into the running container, and rebuilds when dependencies change. Combined with uvicorn's `--reload`, saved code is live in about a second. A bind mount is the simpler alternative. Only services with `ports:` are reachable from your computer; the rest stay on Compose's private network.",
                r"""
                services:
                  api:
                    build: .
                    command: uvicorn app.main:app --host 0.0.0.0 --reload
                    develop:
                      watch:
                        - action: sync
                          path: ./app
                          target: /app/app
                        - action: rebuild
                          path: requirements.txt
                """,
                "yaml",
            ),
        ],
        [
            "Use `condition: service_healthy` with a real healthcheck to wait for readiness.",
            "Compose creates a private network; only published ports are reachable from your computer.",
            "`docker compose watch` (or a bind mount) gives a fast edit-and-reload loop.",
        ],
        r"""
        services:
          db:
            image: postgres:16
            environment:
              POSTGRES_USER: app
              POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
              POSTGRES_DB: tasks
            healthcheck:
              test: ["CMD-SHELL", "pg_isready -U app -d tasks"]
              interval: 5s
              timeout: 3s
              retries: 10
            volumes:
              - pgdata:/var/lib/postgresql/data

          api:
            build: .
            command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
            ports:
              - "8000:8000"
            environment:
              DATABASE_URL: postgresql://app:${POSTGRES_PASSWORD}@db:5432/tasks
            depends_on:
              db:
                condition: service_healthy
            develop:
              watch:
                - action: sync
                  path: ./app
                  target: /app/app
                - action: rebuild
                  path: requirements.txt

        volumes:
          pgdata:

        # docker compose watch   ->   edit app/main.py, save, and the API reloads
        """,
        [
            question("Which setup makes the API wait until Postgres is ready?", ["`depends_on: [db]`", "`depends_on` with `condition: service_healthy`, plus a healthcheck on db", "`restart: always`", "links"], 1,
                     "Without a healthcheck, Compose only knows the container has started, not that Postgres is accepting connections."),
            question("In compose watch, what does `action: rebuild` on requirements.txt do?", ["Syncs the file", "Rebuilds the image and recreates the container when the file changes", "Deletes the file", "Nothing"], 1,
                     "New dependencies need a new image, so syncing the file alone wouldn't install them."),
            question("Can your browser reach the db service if it has no `ports:` entry?", ["Yes", "No; it's only on Compose's internal network", "Only on port 5432", "Only with watch"], 1,
                     "Not publishing the database port is a good default."),
        ],
        "yaml",
    ),
    "docker-multistage": lesson(
        "Multi-stage builds use one stage to build and a clean, minimal stage to run: smaller images, fewer vulnerabilities and no build tools in production.",
        [
            section(
                "Stages",
                "Each `FROM` starts a new stage. Build or compile in an early stage, then `COPY --from=` only the results into the final stage. This app's own Dockerfile works this way: a Node stage builds the TypeScript frontend, and the final Python image copies in just the built `dist/` folder.",
                r"""
                # Stage 1: build the web app
                FROM node:22-slim AS web
                WORKDIR /web
                COPY web/package.json web/package-lock.json ./
                RUN npm ci
                COPY web/ ./
                RUN npm run build

                # Stage 2: the runtime image, without Node or node_modules
                FROM python:3.12-slim
                WORKDIR /app/api
                COPY api/requirements.txt ./
                RUN pip install --no-cache-dir -r requirements.txt
                COPY api/app ./app
                COPY --from=web /web/dist /app/web/dist
                """,
                "dockerfile",
            ),
            section(
                "Run as a non-root user",
                "By default, containers run as root. Create an unprivileged user and switch to it with `USER`, so a compromised app can do far less damage. Make sure that user can write to any data folder the app needs.",
                r"""
                FROM python:3.12-slim
                RUN useradd --create-home --uid 10001 appuser
                WORKDIR /app
                COPY --chown=appuser:appuser . .
                USER appuser
                CMD ["python", "main.py"]
                """,
                "dockerfile",
            ),
        ],
        [
            "Build tools stay in the builder stage; only the results reach the final image.",
            "Run as a non-root USER in production.",
            "Compare sizes with `docker images` after each change.",
        ],
        r"""
        # Stage 1: build wheels for every dependency
        FROM python:3.12-slim AS builder
        WORKDIR /build
        COPY requirements.txt .
        RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

        # Stage 2: a minimal runtime
        FROM python:3.12-slim
        ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
        RUN useradd --create-home --uid 10001 appuser
        WORKDIR /app
        # Mount the wheels for this one step, so they never become a layer of the image
        RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
            pip install --no-cache-dir /wheels/*
        COPY --chown=appuser:appuser app ./app
        USER appuser
        EXPOSE 8000
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

        #   docker build -t tasks-api:slim .
        #   docker images tasks-api               # compare with a single-stage python:3.12 build
        #   docker run --rm tasks-api:slim whoami # appuser
        """,
        [
            question("In a multi-stage build, what ends up in the final image?", ["Everything from every stage", "Only what the last stage contains, including files copied with COPY --from", "Only the first stage", "The build cache"], 1,
                     "Earlier stages are discarded unless you copy something out of them."),
            question("Why run as a non-root user?", ["It's faster", "If the app is compromised, the attacker has far fewer privileges", "Root can't run Python", "Docker requires it"], 1,
                     "Least privilege limits the damage of a security bug."),
            question("A Dockerfile runs `COPY big-folder` and later `RUN rm -rf big-folder`. Does the image shrink?", ["Yes", "No; the earlier layer still contains the files", "Yes, but only on Windows", "Only after docker system prune"], 1,
                     "Layers are additive: deleting files later only hides them. Use a separate stage or a build mount instead."),
        ],
        "dockerfile",
    ),
    "docker-security": lesson(
        "Keep secrets out of images, use minimal and up-to-date base images, and scan images for known vulnerabilities.",
        [
            section(
                "Secrets don't belong in images",
                "Anything in a layer can be read by anyone who has the image, including values set with `ENV` and files you deleted in a later step. Pass secrets at run time (environment variables, or files from your platform's secret store). If a build step itself needs a secret, use a BuildKit secret mount, which never lands in a layer.",
                r"""
                # Wrong: the token is stored in the image for everyone to read
                # ENV API_TOKEN=abc123

                # Right, for build-time secrets:
                #   docker build --secret id=pip_token,src=token.txt .
                RUN --mount=type=secret,id=pip_token \
                    PIP_INDEX_URL="https://user:$(cat /run/secrets/pip_token)@pypi.example.com/simple" \
                    pip install --no-cache-dir -r requirements.txt
                """,
                "dockerfile",
            ),
            section(
                "Scan and update",
                "`docker scout`, built into Docker Desktop, lists known vulnerabilities (CVEs) in an image's packages and suggests fixes, usually a newer base image. Rebuild regularly to pick up patched bases, keep images small and run as non-root.",
                r"""
                docker scout quickview tasks-api:1.0
                docker scout cves tasks-api:1.0 --only-severity critical,high
                docker scout recommendations tasks-api:1.0
                docker build --pull -t tasks-api:1.1 .    # --pull fetches the newest base image
                """,
                "shell",
            ),
        ],
        [
            "Never put secrets in ENV, COPY or the build context.",
            "Scan images, and rebuild on fresh base images regularly.",
            "Smaller images plus non-root users mean a smaller attack surface.",
        ],
        r"""
        # 1. Look for secrets baked into the image (before the fix):
        docker history --no-trunc tasks-api:1.0 | findstr /i "KEY TOKEN PASSWORD"
        #    (macOS/Linux: | grep -iE "key|token|password")

        # 2. Fix: remove ENV API_KEY=... from the Dockerfile, add .env to .dockerignore,
        #    and pass the secret when the container starts:
        docker build -t tasks-api:1.1 .
        docker run -d -p 8000:8000 --env-file .env tasks-api:1.1

        # 3. Scan, and fix one finding:
        docker scout cves tasks-api:1.1 --only-severity critical,high
        docker scout recommendations tasks-api:1.1
        #    e.g. "update the base image": rebuild with --pull
        docker build --pull -t tasks-api:1.2 .
        docker scout quickview tasks-api:1.2
        """,
        [
            question("You set `ENV API_KEY=...` in a Dockerfile and push the image. Who can read the key?", ["Nobody", "Anyone who can pull the image", "Only root", "Only Docker Hub staff"], 1,
                     "`docker history` or `docker inspect` reveals ENV values."),
            question("What does `docker build --pull` do?", ["Pushes the image", "Always checks for a newer version of the base image", "Skips the cache for every layer", "Deletes old images"], 1,
                     "Without it, Docker may keep using an old, unpatched base image from its cache."),
            question("What's the safest way to use a private token during `RUN pip install`?", ["ARG TOKEN", "ENV TOKEN", "A BuildKit secret mount (`--mount=type=secret`)", "COPY token.txt"], 2,
                     "Secret mounts exist only while that one RUN step executes."),
        ],
        "shell",
    ),
    "docker-ci-deploy": lesson(
        "Automate it: every push builds and tests your image in CI, pushes it to a registry, and a host pulls and runs it.",
        [
            section(
                "Build and push with GitHub Actions",
                "A workflow in `.github/workflows/` runs on every push. Log in to GitHub Container Registry (ghcr.io) with the built-in `GITHUB_TOKEN`, then build and push with Docker's official actions. Tag images with the commit SHA so every version is traceable. Image names must be lowercase.",
                r"""
                name: image
                on:
                  push:
                    branches: [main]

                permissions:
                  contents: read
                  packages: write

                jobs:
                  build:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: docker/login-action@v3
                        with:
                          registry: ghcr.io
                          username: ${{ github.actor }}
                          password: ${{ secrets.GITHUB_TOKEN }}
                      - uses: docker/build-push-action@v6
                        with:
                          push: true
                          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
                """,
                "yaml",
            ),
            section(
                "Deploy the image",
                "Any container host can run the image: pull a specific tag and start it with production settings. Platforms such as Render, Fly.io or a cloud VM can deploy from a registry or build your Dockerfile directly. This app deploys to Render from its Dockerfile on every push to main.",
                r"""
                docker pull ghcr.io/OWNER/REPO:COMMIT_SHA
                docker run -d --name api --restart unless-stopped -p 80:8000 --env-file /etc/tasks-api.env ghcr.io/OWNER/REPO:COMMIT_SHA
                """,
                "shell",
            ),
        ],
        [
            "CI builds the same image every time, from a clean checkout.",
            "Tag images with the commit SHA; avoid deploying a moving `latest` tag.",
            "Run tests in CI before pushing, so broken images never reach production.",
        ],
        r"""
        # .github/workflows/image.yml
        name: test-build-push
        on:
          push:
            branches: [main]

        permissions:
          contents: read
          packages: write

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
                with:
                  python-version: "3.12"
              - run: pip install -r api/requirements-dev.txt
              - run: pytest
                working-directory: api

          image:
            needs: test
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: docker/setup-buildx-action@v3
              - uses: docker/login-action@v3
                with:
                  registry: ghcr.io
                  username: ${{ github.actor }}
                  password: ${{ secrets.GITHUB_TOKEN }}
              - uses: docker/build-push-action@v6
                with:
                  push: true
                  tags: |
                    ghcr.io/${{ github.repository }}:${{ github.sha }}
                    ghcr.io/${{ github.repository }}:main
                  cache-from: type=gha
                  cache-to: type=gha,mode=max

        # Deploy: on the host, docker pull ghcr.io/<owner>/<repo>:<sha> and docker run it,
        # or point Render or Fly.io at the image.
        """,
        [
            question("Why tag images with the commit SHA?", ["It's shorter", "Each image maps to one exact commit, so deploys and rollbacks are precise", "Registries require it", "It makes images smaller"], 1,
                     "A moving tag like `latest` can't tell you exactly which code is running."),
            question("What does `needs: test` do in the workflow?", ["Runs both jobs at the same time", "The image job runs only after the test job succeeds", "Installs test tools", "Skips the tests"], 1,
                     "Failing tests stop the image from being built and pushed."),
            question("Which token lets a GitHub Actions workflow push to ghcr.io for its own repository?", ["Your personal password", "The built-in GITHUB_TOKEN, with `packages: write` permission", "An SSH key", "No token is needed"], 1,
                     "GITHUB_TOKEN is created for each run and expires afterwards, so there's no secret to manage."),
        ],
        "yaml",
    ),
}
