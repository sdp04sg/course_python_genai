# Deploying Build & Learn

This guide puts the app on the internet with [Render](https://render.com), protected by a password. It takes about 15 minutes, and you don't need to install anything extra.

The site is built for **one learner**. Lesson progress is stored in a single database that every visitor shares, so keep the password private.

## How it runs in production

```text
Browser ──HTTPS──▶ Render web service (one Docker container)
                     ├─ FastAPI: /api/* and /docs
                     ├─ The built TypeScript web app at /
                     └─ SQLite progress database on a persistent disk (/var/data)
```

- The [Dockerfile](Dockerfile) builds the web app with Node, then runs FastAPI with Python. FastAPI serves both the web pages and the API, so there is one URL and no CORS setup.
- [render.yaml](render.yaml) is a Render *Blueprint*. It describes the service, its disk and its settings, so Render can create everything for you.
- When `APP_PASSWORD` is set, the browser asks for it before showing any page. Only `/api/health` stays open, because Render uses it to check that the app is up.

## Before you start

You need:

- **The code on GitHub:** [sdp04sg/course_python_genai](https://github.com/sdp04sg/course_python_genai).
- **A Render account.** You can sign up with GitHub at [render.com](https://render.com).
- **A long password** for the site. Use 16+ characters, such as four random words. Nothing limits repeated guesses, so the length is what keeps it safe.
- **Optional:** an Anthropic API key from the [Claude Console](https://platform.claude.com) to turn on the AI coach, which uses Claude. The Console account needs API credits (a Claude.ai subscription doesn't include API usage), and each chat message is billed to it.

> **Cost:** the database needs a persistent disk, and Render only offers disks on **paid** instance types, so `render.yaml` uses the `starter` plan. Check [Render's pricing](https://render.com/pricing) before you continue. To try it for free, see [Run on the free plan](#run-on-the-free-plan); progress then resets on every deploy.

## Step 1: Create the service on Render

Choose **one** of these options.

### Option A: Deploy button

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sdp04sg/course_python_genai)

Click the button, sign in to Render, and go to [Step 2](#step-2-fill-in-the-settings).

### Option B: From the Render dashboard

1. Open the [Render dashboard](https://dashboard.render.com).
2. Choose **New** → **Blueprint**.
3. Connect your GitHub account if asked, then select the **course_python_genai** repository.
4. Render finds `render.yaml` and shows a web service named **build-and-learn** with a 1 GB disk.

## Step 2: Fill in the settings

Render asks for the settings that aren't stored in `render.yaml`:

| Setting | What to enter |
| --- | --- |
| `APP_PASSWORD` | Your long password. **Don't leave it empty**, or anyone with the link can use the site. |
| `ANTHROPIC_API_KEY` | Your Anthropic API key, or leave it empty to keep the AI coach off. |

These values are already filled in and usually don't need changing:

| Setting | Value | Purpose |
| --- | --- | --- |
| `APP_DB_PATH` | `/var/data/progress.sqlite3` | Keeps progress on the persistent disk. |
| `ANTHROPIC_MODEL` | `claude-opus-5-5` | The Claude model the coach uses. |

The coach can also use any OpenAI-compatible provider instead: leave `ANTHROPIC_API_KEY` empty and add `OPENAI_API_KEY` (plus `OPENAI_MODEL` and `OPENAI_BASE_URL` if needed) under **Environment**.

Click **Apply** (or **Deploy Blueprint**). Render now builds the Docker image and starts the service. The first build takes a few minutes; you can follow it in the **Logs** tab.

## Step 3: Check that it works

1. When the service shows **Live**, open its URL, for example `https://build-and-learn-xxxx.onrender.com`. Render provides HTTPS automatically.
2. The browser asks you to sign in. **Type any username** and your `APP_PASSWORD`.
3. The course page loads. Choose **Mark done** on a lesson and refresh; it should stay marked.
4. If you set an API key, ask the learning coach a question.
5. Optional: open `https://<your-url>/api/health`. It returns `{"status":"ok"}` without a password.

Your browser remembers the password until you close it. To sign out, close all browser windows.

## Updating the site

Render redeploys automatically whenever you push to the `main` branch:

```powershell
git add -A
git commit -m "Describe your change"
git push
```

Before pushing, it's worth running the checks locally (see [Verify the projects](README.md#verify-the-projects)). If a deploy fails, Render keeps the previous version running.

## Changing settings or secrets

In the Render dashboard, open the **build-and-learn** service → **Environment**. Edit a value, then save and deploy. For example, you can:

- Change the site password: edit `APP_PASSWORD`.
- Turn the AI coach on or off: set or clear `ANTHROPIC_API_KEY`.
- Use a different Claude model: edit `ANTHROPIC_MODEL`.

Never put real keys or passwords in the code or in a committed file. `api/.env` is ignored by git for this reason, and this repository is public.

## Using your own domain

1. In the service, open **Settings** → **Custom Domains** → **Add Custom Domain**, and enter the domain (for example `learn.example.com`).
2. Render shows a DNS record (usually a `CNAME`). Add it at your domain registrar.
3. When the record has taken effect, Render verifies the domain and issues an HTTPS certificate automatically.

## Run on the free plan

To test without paying, use the free instance type. **Progress is then lost on every deploy and restart.** In `render.yaml`:

1. Delete the line `plan: starter`.
2. Delete the whole `disk:` block (four lines).
3. Delete the `APP_DB_PATH` entry (two lines).

Commit and push, then create the service as in Step 1. Free services also sleep when nobody uses them, so the first visit afterwards can take up to a minute.

You can switch to a paid instance type and add a disk later. Set `APP_DB_PATH` to a path on the disk when you do.

## Try the production setup on your computer

To check the production behavior (one server, password prompt) before deploying:

```powershell
cd web
npm run build
cd ..\api
.\.venv\Scripts\Activate.ps1
$env:APP_PASSWORD = "try-it-locally"
python -m uvicorn app.main:app --port 8000
```

Open `http://localhost:8000` and sign in with any username and `try-it-locally`. Close the terminal afterwards so the password setting doesn't stay around.

If you have Docker installed, you can test the exact image Render builds:

```powershell
docker build -t build-and-learn .
docker run --rm -p 8000:8000 -e APP_PASSWORD=try-it-locally build-and-learn
```

## Troubleshooting

| Problem | What to check |
| --- | --- |
| The build fails | Open the deploy in the **Logs** tab and look for the first error. Run `npm run build` in `web` and `python -m pytest` in `api` locally to reproduce it. |
| The password prompt keeps coming back | Check the password for typos or extra spaces. After changing `APP_PASSWORD`, wait for the redeploy to finish, then close the browser and sign in again. |
| The site opens without a password | `APP_PASSWORD` is empty. Set it under **Environment** and redeploy. |
| Progress disappears after a deploy | The service has no disk, or `APP_DB_PATH` doesn't point to `/var/data`. Check the **Disks** and **Environment** pages. |
| The coach says "AI chat is not configured" | `ANTHROPIC_API_KEY` is empty. Set it under **Environment** and redeploy. |
| The coach says the account has no API credits | Add credits under **Plans & Billing** in the Claude Console. No redeploy is needed. |
| The coach says Claude rejected the API key | The key is wrong, was revoked or has expired. Create a new one in the Claude Console and update `ANTHROPIC_API_KEY`. |
| Deploys fail the health check | Check the logs for a startup error. The app must answer `/api/health` on the port Render provides; the Dockerfile already uses `$PORT`. |
