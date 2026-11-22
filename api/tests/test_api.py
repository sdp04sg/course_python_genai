import base64
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.content import INTERVIEW_QUESTIONS, LESSON_CONTENT
from app.main import create_app


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch):
    # Keep tests independent of the developer's .env (password, real provider keys).
    for name in ("APP_PASSWORD", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "ANTHROPIC_EFFORT", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)


class FakeClaude:
    """Stands in for anthropic.AsyncAnthropic, recording each request."""

    calls: list[dict] = []
    stop_reason = "end_turn"

    def __init__(self, api_key, timeout, max_retries):
        assert api_key == "test-claude-key"
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def _create(self, **kwargs):
        FakeClaude.calls.append(kwargs)
        return SimpleNamespace(
            stop_reason=FakeClaude.stop_reason,
            content=[
                SimpleNamespace(type="thinking", thinking=""),
                SimpleNamespace(type="text", text="Try binary search on a list of five numbers."),
            ],
        )


def test_chat_uses_claude_with_lesson_context(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-claude-key")
    monkeypatch.setenv("OPENAI_API_KEY", "should-not-be-used")
    monkeypatch.setattr(main.anthropic, "AsyncAnthropic", FakeClaude)
    FakeClaude.calls, FakeClaude.stop_reason = [], "end_turn"

    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.post(
            "/api/chat",
            json={
                "lesson_id": "dsa-binary-search",
                "messages": [
                    {"role": "assistant", "content": "Earlier reply"},
                    {"role": "user", "content": "How do I start?"},
                ],
            },
        )

    assert response.status_code == 200
    assert response.json() == {"reply": "Try binary search on a list of five numbers."}
    request = FakeClaude.calls[0]
    assert request["model"] == "claude-opus-5-5"
    assert request["fallbacks"] == "default"
    assert request["messages"] == [{"role": "user", "content": "How do I start?"}]
    assert "Search sorted data with binary search" in request["system"]


def test_chat_returns_a_friendly_message_when_claude_declines(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-claude-key")
    monkeypatch.setattr(main.anthropic, "AsyncAnthropic", FakeClaude)
    FakeClaude.calls, FakeClaude.stop_reason = [], "refusal"

    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})

    FakeClaude.stop_reason = "end_turn"
    assert response.status_code == 200
    assert response.json()["reply"] == main.REFUSAL_REPLY


def _basic_auth(password: str) -> dict[str, str]:
    token = base64.b64encode(f"me:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_site_password_protects_everything_except_health(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "correct horse")
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        assert client.get("/api/health").status_code == 200

        locked = client.get("/api/courses")
        assert locked.status_code == 401
        assert locked.headers["WWW-Authenticate"].startswith("Basic")
        assert client.get("/docs").status_code == 401
        assert client.get("/api/courses", headers=_basic_auth("wrong")).status_code == 401
        assert client.get("/api/courses", headers={"Authorization": "Basic !!"}).status_code == 401

        assert client.get("/api/courses", headers=_basic_auth("correct horse")).status_code == 200


def test_serves_the_built_web_app_alongside_the_api(tmp_path):
    web_dist = tmp_path / "dist"
    web_dist.mkdir()
    (web_dist / "index.html").write_text("<h1>Build & Learn</h1>", encoding="utf-8")
    with TestClient(create_app(tmp_path / "progress.sqlite3", web_dist)) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Build & Learn" in page.text
        assert client.get("/api/health").json() == {"status": "ok"}
        assert client.put("/api/progress/nope", json={"completed": True}).status_code == 404


def test_courses_and_progress_are_available_and_persisted(tmp_path):
    app = create_app(tmp_path / "progress.sqlite3")
    with TestClient(app) as client:
        courses = client.get("/api/courses")
        assert courses.status_code == 200
        assert [course["id"] for course in courses.json()] == [
            "python",
            "dsa",
            "python-advanced",
            "fastapi",
            "backend",
            "postgres",
            "mongodb",
            "typescript",
            "docker",
            "system-design",
            "genai",
            "agents-mcp",
        ]

        updated = client.put("/api/progress/python-setup", json={"completed": True})
        assert updated.status_code == 200
        assert client.get("/api/progress").json() == {"python-setup": True}

    reopened_app = create_app(tmp_path / "progress.sqlite3")
    with TestClient(reopened_app) as reopened_client:
        assert reopened_client.get("/api/progress").json() == {"python-setup": True}


def test_curriculum_lessons_are_complete_and_ids_are_unique():
    # Progress is stored by lesson id, so ids must never repeat across courses.
    lesson_ids = []
    for course in main.COURSES:
        assert course["title"] and course["subtitle"] and course["level"]
        assert course["modules"], f"{course['id']} has no modules"
        for module in course["modules"]:
            assert module["lessons"], f"{module['title']} has no lessons"
            for lesson in module["lessons"]:
                assert lesson["title"] and lesson["practice"]
                assert lesson["minutes"] > 0
                lesson_ids.append(lesson["id"])
    assert len(lesson_ids) == len(set(lesson_ids))
    assert len(lesson_ids) == 125


def test_every_lesson_has_a_tutorial_and_a_valid_quiz():
    lesson_ids = {
        lesson["id"]
        for course in main.COURSES
        for module in course["modules"]
        for lesson in module["lessons"]
    }
    assert set(LESSON_CONTENT) == lesson_ids

    for lesson_id, content in LESSON_CONTENT.items():
        assert content["summary"].strip(), lesson_id
        assert len(content["sections"]) >= 2, lesson_id
        assert len(content["key_points"]) >= 3, lesson_id
        assert content["solution"].strip(), lesson_id
        assert len(content["quiz"]) >= 3, lesson_id
        for section in content["sections"]:
            assert section["heading"] and section["text"], lesson_id
        for item in content["quiz"]:
            assert len(set(item["options"])) == len(item["options"]) >= 2, (lesson_id, item["question"])
            assert 0 <= item["answer"] < len(item["options"]), (lesson_id, item["question"])
            assert item["explanation"], (lesson_id, item["question"])
        assert len(content["interview"]) >= 2, lesson_id
        for item in content["interview"]:
            assert item["question"] and item["answer"] and item["application"], lesson_id


def test_interview_questions_only_reference_real_lessons():
    assert set(INTERVIEW_QUESTIONS) == set(LESSON_CONTENT)


def test_course_interview_endpoint_groups_questions_by_lesson(tmp_path):
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.get("/api/courses/postgres/interview")
        assert response.status_code == 200
        body = response.json()
        assert body["course_title"] == "PostgreSQL and SQL"
        assert len(body["lessons"]) == 14
        assert all(len(lesson["questions"]) >= 2 for lesson in body["lessons"])
        assert client.get("/api/courses/not-a-course/interview").status_code == 404

        for course_id, title, lessons in [
            ("backend", "Server-Side Fundamentals", 8),
            ("mongodb", "MongoDB and NoSQL", 9),
            ("system-design", "System Design", 13),
        ]:
            body = client.get(f"/api/courses/{course_id}/interview").json()
            assert body["course_title"] == title
            assert len(body["lessons"]) == lessons
            assert all(len(lesson["questions"]) == 3 for lesson in body["lessons"])


def test_python_examples_in_lessons_are_valid_python():
    for lesson_id, content in LESSON_CONTENT.items():
        snippets = [
            (section["code"], section["language"])
            for section in content["sections"]
            if "code" in section
        ]
        snippets.append((content["solution"], content["solution_language"]))
        for code, language in snippets:
            if language == "python":
                compile(code, f"<{lesson_id}>", "exec")


def test_lesson_endpoint_returns_tutorial_content(tmp_path):
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.get("/api/lessons/dsa-binary-search")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == "dsa-binary-search"
        assert body["sections"] and body["quiz"] and body["solution"]
        assert client.get("/api/lessons/not-a-lesson").status_code == 404


def test_progress_rejects_unknown_lessons(tmp_path):
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.put("/api/progress/not-a-lesson", json={"completed": True})
    assert response.status_code == 404


def test_chat_explains_when_provider_is_not_configured(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Help me learn Python"}]},
        )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_chat_uses_the_configured_openai_compatible_provider(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    class MockClient:
        def __init__(self, timeout):
            assert timeout == 30.0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def post(self, url, headers, json):
            assert url == "https://provider.example/v1/chat/completions"
            assert headers["Authorization"] == "Bearer test-key"
            assert json["model"] == "test-model"
            assert json["messages"][0]["role"] == "system"
            return main.httpx.Response(
                200,
                json={"choices": [{"message": {"content": "Try a small example."}}]},
                request=main.httpx.Request("POST", url),
            )

    monkeypatch.setattr(main.httpx, "AsyncClient", MockClient)
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Help me learn Python"}]},
        )
    assert response.status_code == 200
    assert response.json() == {"reply": "Try a small example."}
