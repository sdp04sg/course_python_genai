# Build & Learn

A standalone, step-by-step learning app for Python, FastAPI, TypeScript, generative AI, and MCP agents. The course tracker and optional AI tutor use a FastAPI backend; lesson completion is saved in a local SQLite database.

## What is included

- Five practical courses with 40 short lessons and a build-it-yourself exercise in each lesson.
- A persistent progress tracker, with course and overall completion percentages.
- A TypeScript/Vite web app that talks to the FastAPI service.
- An optional AI learning coach backed by an OpenAI-compatible chat-completions API. The provider key stays on the Python server.
- API documentation at `/docs` and focused tests for the course and progress APIs.

The coach needs your own provider API key and may incur provider charges. Without it, the learning tracker still works and the chat endpoint explains how to configure one. The coach does not currently have MCP tools; connecting a local course-search tool is a hands-on exercise in the Agents and MCP course.

## Requirements

- Python 3.10 or later
- Node.js 20.19 or later

## Run on Windows

Open this standalone project folder in VS Code, then open two PowerShell terminals with their working directory set to the project folder.

### Terminal 1: FastAPI backend

```powershell
cd api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

The API is at `http://localhost:8000`. Browse `http://localhost:8000/docs` to explore its endpoints. Progress is stored in `api/data/progress.sqlite3`.

To enable the AI learning coach, edit `api/.env` and set `OPENAI_API_KEY` to your own key. You can also set `OPENAI_MODEL` and `OPENAI_BASE_URL` for another OpenAI-compatible provider. Restart the backend after changing the settings. Keep `.env` private; never add a real key to source control.

### Terminal 2: TypeScript web app

```powershell
cd web
npm install
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`).

## Learn and track progress

1. Choose a course and start with its first lesson.
2. Try the practical exercise using the ideas in the lesson.
3. Use **Mark done** to update your progress. It is saved in SQLite and remains after a restart.
4. Choose **Continue learning** to jump to the next incomplete lesson.
5. Ask the learning coach for an explanation or hint after configuring an AI provider.
6. Follow the courses in order to finish with a Python MCP server and an AI study-assistant capstone.

## Verify the projects

```powershell
cd api
python -m pip install -r requirements-dev.txt
python -m pytest
```

In another terminal:

```powershell
cd web
npm run typecheck
npm run build
```

## Deploy to Render

The site is built for one learner: progress is shared, so protect it with a password. In production, one Docker service builds the web app and runs FastAPI, which serves the app and the API from the same URL.

1. Push this folder to a GitHub repository. `.env` and `api/data/` are ignored, so your key and local progress stay on your computer.
2. In the Render dashboard, choose **New > Blueprint** and select the repository. Render reads `render.yaml`.
3. When asked, set:
   - `APP_PASSWORD`: a long password. When the site opens, the browser asks for it; any username works.
   - `OPENAI_API_KEY`: your provider key, or leave it empty to keep the coach off.
4. Apply the Blueprint. When the deploy finishes, open the `onrender.com` URL Render shows.

Progress is saved on a 1 GB persistent disk at `/var/data`. Render only offers disks on paid instance types, so `render.yaml` uses the `starter` plan. To run on the free type, remove the `plan` and `disk` blocks and the `APP_DB_PATH` setting; progress then resets on every deploy and restart.

Every push to the repository's default branch redeploys the site. To use your own domain, add it under the service's **Settings > Custom Domains** and create the DNS record Render shows.

Settings used in production:

| Variable | Purpose |
| --- | --- |
| `APP_PASSWORD` | Password for the whole site, except `/api/health` (used by Render's health check). Empty means no password. |
| `APP_DB_PATH` | Where the SQLite progress database is stored. |
| `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL` | AI coach provider settings, as for local use. |

## API endpoints

- `GET /api/health` — service status
- `GET /api/courses` — course, module, lesson, and exercise content
- `GET /api/progress` — saved lesson-completion state
- `PUT /api/progress/{lesson_id}` — mark a lesson complete or incomplete
- `POST /api/chat` — send tutor messages to the configured LLM provider
