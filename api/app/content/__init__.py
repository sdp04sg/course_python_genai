"""Tutorial content and interview questions for every lesson in app.curriculum."""

from app.content import (
    agents_mcp,
    docker,
    dsa,
    fastapi_course,
    genai,
    interview_ai,
    interview_backend,
    interview_dsa,
    interview_frontend_devops,
    interview_python,
    postgres,
    python_advanced,
    python_foundations,
    typescript,
)

LESSON_CONTENT: dict[str, dict] = {}
for _course in (
    python_foundations,
    dsa,
    python_advanced,
    fastapi_course,
    postgres,
    typescript,
    docker,
    genai,
    agents_mcp,
):
    LESSON_CONTENT.update(_course.CONTENT)

INTERVIEW_QUESTIONS: dict[str, list[dict]] = {}
for _group in (interview_python, interview_dsa, interview_backend, interview_frontend_devops, interview_ai):
    INTERVIEW_QUESTIONS.update(_group.INTERVIEW)

for _lesson_id, _content in LESSON_CONTENT.items():
    _content["interview"] = INTERVIEW_QUESTIONS.get(_lesson_id, [])
