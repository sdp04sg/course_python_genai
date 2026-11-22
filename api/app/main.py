import base64
import binascii
import logging
import os
import secrets
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import anthropic
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.content import LESSON_CONTENT
from app.curriculum import COURSES

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)
DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "progress.sqlite3"
DEFAULT_WEB_DIST_PATH = Path(__file__).resolve().parents[2] / "web" / "dist"
# Paths that stay reachable without the site password, so the host's health check works.
PUBLIC_PATHS = {"/api/health"}
SYSTEM_PROMPT = (
    "You are a patient programming tutor for a practical course in Python (beginner to "
    "advanced), data structures and algorithms, FastAPI, server-side fundamentals (HTTP, APIs, "
    "authentication, security), PostgreSQL and SQL, MongoDB, TypeScript, Docker, system design, "
    "generative AI, and MCP. You also help learners prepare for technical interviews. Explain concepts step by step, ask the learner "
    "to try small exercises, and give hints before complete solutions. Be honest about "
    "uncertainty. You cannot see or change the learner's progress, access external tools, "
    "or run code. Never ask for secrets or claim to have used an MCP tool."
)


class ProgressUpdate(BaseModel):
    completed: bool


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)
    lesson_id: str | None = Field(default=None, max_length=80)


DEFAULT_CLAUDE_MODEL = "claude-opus-5-5"
# Models that accept the server-side refusal fallback (beta server-side-fallback-2026-07-01).
CLAUDE_FALLBACK_MODELS = {
    "claude-fable-5-2",
    "claude-fable-5-1",
    "claude-opus-5-5",
    "claude-opus-5",
    "claude-sonnet-5-5",
}
CLAUDE_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
REFUSAL_REPLY = (
    "I can't help with that request. Try asking about a lesson, a programming concept, "
    "or an error message you're seeing."
)


async def _ask_claude(api_key: str, system: str, history: list[dict]) -> str:
    """Ask Claude through the official Anthropic SDK and return the text reply."""
    model = os.environ.get("ANTHROPIC_MODEL", "").strip() or DEFAULT_CLAUDE_MODEL
    effort = os.environ.get("ANTHROPIC_EFFORT", "medium").strip().lower()
    request: dict = {
        "model": model,
        "max_tokens": 16000,
        "system": system,
        "messages": history,
        "output_config": {"effort": effort if effort in CLAUDE_EFFORTS else "medium"},
    }
    if model in CLAUDE_FALLBACK_MODELS:
        # If a safety classifier declines, the API retries on a suitable model in the same call.
        request["betas"] = ["server-side-fallback-2026-07-01"]
        request["fallbacks"] = "default"

    try:
        async with anthropic.AsyncAnthropic(api_key=api_key, timeout=90.0, max_retries=2) as client:
            response = await client.beta.messages.create(**request)
    except anthropic.AuthenticationError as error:
        logger.warning("Claude rejected the API key")
        raise HTTPException(
            status_code=502, detail="Claude rejected the API key. Check ANTHROPIC_API_KEY."
        ) from error
    except anthropic.PermissionDeniedError as error:
        logger.warning("The Anthropic API key lacks permission for model %s", model)
        raise HTTPException(
            status_code=502, detail="This API key can't use the configured Claude model."
        ) from error
    except anthropic.RateLimitError as error:
        logger.warning("Claude rate limit reached")
        raise HTTPException(
            status_code=503, detail="The AI coach is busy right now. Please try again shortly."
        ) from error
    except anthropic.APIStatusError as error:
        if "credit balance" in str(getattr(error, "message", "")).lower():
            logger.warning("The Anthropic account has no API credits")
            raise HTTPException(
                status_code=503,
                detail=(
                    "The AI coach is set up, but the Anthropic account has no API credits. "
                    "Add credits under Plans & Billing in the Claude Console, then try again."
                ),
            ) from error
        logger.warning(
            "Claude returned HTTP %s (request %s)", error.status_code, getattr(error, "request_id", None)
        )
        raise HTTPException(
            status_code=502, detail="Claude couldn't answer right now. Please try again."
        ) from error
    except anthropic.APIConnectionError as error:
        logger.warning("Could not reach Claude: %s", error.__class__.__name__)
        raise HTTPException(
            status_code=502, detail="Could not reach Claude. Check your connection and try again."
        ) from error

    if response.stop_reason == "refusal":
        return REFUSAL_REPLY
    reply = "".join(block.text for block in response.content if block.type == "text").strip()
    if not reply:
        raise HTTPException(status_code=502, detail="Claude's response did not contain a reply.")
    return reply


async def _ask_openai_compatible(api_key: str, system: str, history: list[dict]) -> str:
    """Fallback provider: any OpenAI-compatible chat-completions API."""
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    messages = [{"role": "system", "content": system}, *history]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model, "messages": messages},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        logger.warning("AI provider returned HTTP %s", error.response.status_code)
        raise HTTPException(
            status_code=502,
            detail="The AI provider rejected the request. Check your model and provider settings.",
        ) from error
    except httpx.RequestError as error:
        logger.warning("Could not reach the configured AI provider: %s", error)
        raise HTTPException(
            status_code=502,
            detail="Could not reach the AI provider. Check the provider URL and try again.",
        ) from error

    try:
        payload = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502, detail="The AI provider returned an invalid response."
        ) from error

    choices = payload.get("choices") if isinstance(payload, dict) else None
    first_choice = choices[0] if isinstance(choices, list) and choices else None
    message = first_choice.get("message") if isinstance(first_choice, dict) else None
    reply = message.get("content") if isinstance(message, dict) else None
    if not isinstance(reply, str) or not reply.strip():
        raise HTTPException(
            status_code=502,
            detail="The AI provider response did not contain a tutor reply.",
        )
    return reply.strip()


def _initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS lesson_progress (
                lesson_id TEXT PRIMARY KEY,
                completed INTEGER NOT NULL CHECK (completed IN (0, 1))
            )
            """
        )


def _get_progress(database_path: Path) -> dict[str, bool]:
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT lesson_id, completed FROM lesson_progress"
        ).fetchall()
    return {lesson_id: bool(completed) for lesson_id, completed in rows}


def _password_matches(authorization: str, password: str) -> bool:
    """Check an HTTP Basic Authorization header; the username is ignored."""
    scheme, _, encoded = authorization.partition(" ")
    if scheme.lower() != "basic" or not encoded:
        return False
    try:
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return False
    _, _, supplied = decoded.partition(":")
    return secrets.compare_digest(supplied.encode("utf-8"), password.encode("utf-8"))


def create_app(
    database_path: Path | None = None, web_dist_path: Path | None = None
) -> FastAPI:
    progress_database = database_path or Path(
        os.environ.get("APP_DB_PATH", str(DEFAULT_DATABASE_PATH))
    )
    web_dist = web_dist_path or DEFAULT_WEB_DIST_PATH
    site_password = os.environ.get("APP_PASSWORD", "").strip()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        _initialize_database(progress_database)
        yield

    application = FastAPI(
        title="Python + TypeScript Learning Path",
        description="A practical course tracker and provider-ready AI tutor.",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "PUT", "POST"],
        allow_headers=["Content-Type"],
    )

    if site_password:

        @application.middleware("http")
        async def require_site_password(request: Request, call_next):
            authorization = request.headers.get("Authorization", "")
            if request.url.path in PUBLIC_PATHS or _password_matches(
                authorization, site_password
            ):
                return await call_next(request)
            return PlainTextResponse(
                "Password required.",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Build & Learn", charset="UTF-8"'},
            )

    lessons = {
        lesson["id"]
        for course in COURSES
        for module in course["modules"]
        for lesson in module["lessons"]
    }

    @application.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/api/courses")
    async def courses() -> list[dict]:
        return COURSES

    @application.get("/api/lessons/{lesson_id}")
    async def lesson_content(lesson_id: str) -> dict:
        content = LESSON_CONTENT.get(lesson_id)
        if lesson_id not in lessons or content is None:
            raise HTTPException(status_code=404, detail="Lesson not found.")
        return {"id": lesson_id, **content}

    @application.get("/api/courses/{course_id}/interview")
    async def course_interview(course_id: str) -> dict:
        course = next((item for item in COURSES if item["id"] == course_id), None)
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found.")
        return {
            "course_id": course["id"],
            "course_title": course["title"],
            "lessons": [
                {
                    "lesson_id": lesson["id"],
                    "lesson_title": lesson["title"],
                    "module_title": module["title"],
                    "questions": LESSON_CONTENT.get(lesson["id"], {}).get("interview", []),
                }
                for module in course["modules"]
                for lesson in module["lessons"]
            ],
        }

    @application.get("/api/progress")
    async def progress() -> dict[str, bool]:
        return _get_progress(progress_database)

    @application.put("/api/progress/{lesson_id}")
    async def update_progress(
        lesson_id: str, update: ProgressUpdate
    ) -> dict[str, bool]:
        if lesson_id not in lessons:
            raise HTTPException(status_code=404, detail="Lesson not found.")
        with sqlite3.connect(progress_database) as connection:
            connection.execute(
                """
                INSERT INTO lesson_progress (lesson_id, completed)
                VALUES (?, ?)
                ON CONFLICT(lesson_id) DO UPDATE SET completed = excluded.completed
                """,
                (lesson_id, int(update.completed)),
            )
        return {lesson_id: update.completed}

    lesson_index = {
        lesson["id"]: (course, module, lesson)
        for course in COURSES
        for module in course["modules"]
        for lesson in module["lessons"]
    }

    def coach_system_prompt(lesson_id: str | None) -> str:
        if not lesson_id or lesson_id not in lesson_index:
            return SYSTEM_PROMPT
        course, module, lesson = lesson_index[lesson_id]
        summary = LESSON_CONTENT.get(lesson_id, {}).get("summary", "")
        return (
            f"{SYSTEM_PROMPT}\n\nThe learner is reading the lesson \"{lesson['title']}\" "
            f"(course: {course['title']}; module: {module['title']}). Lesson summary: {summary} "
            f"Practice task: {lesson['practice']} Relate your help to this lesson when it's relevant."
        )

    @application.post("/api/chat")
    async def chat(request: ChatRequest) -> dict[str, str]:
        history = [message.model_dump() for message in request.messages]
        while history and history[0]["role"] != "user":
            history.pop(0)  # Claude requires the conversation to start with the learner
        if not history:
            raise HTTPException(status_code=422, detail="Send a question for the coach first.")
        system = coach_system_prompt(request.lesson_id)

        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if anthropic_key:
            return {"reply": await _ask_claude(anthropic_key, system, history)}
        openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if openai_key:
            return {"reply": await _ask_openai_compatible(openai_key, system, history)}
        raise HTTPException(
            status_code=503,
            detail=(
                "AI chat is not configured. Set ANTHROPIC_API_KEY in api/.env "
                "(or in your host's environment settings) and restart the API."
            ),
        )

    # Serve the built web app (npm run build) from the same origin as the API.
    # Mounted last so the /api routes and /docs take priority.
    if (web_dist / "index.html").is_file():
        application.mount("/", StaticFiles(directory=web_dist, html=True), name="web")

    return application


app = create_app()
