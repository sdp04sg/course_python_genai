"""Helpers that keep the lesson content files short and consistent.

Each lesson has a summary, tutorial sections (text plus an optional code
example), key points, a worked solution to the lesson's practice task, and a
multiple-choice quiz. Inline code in text is written with `backticks`;
paragraphs are separated by a blank line.
"""

from textwrap import dedent


def _code(source: str) -> str:
    return dedent(source).strip("\n")


def section(heading: str, text: str, code: str | None = None, language: str = "python") -> dict:
    item = {"heading": heading, "text": text.strip()}
    if code is not None:
        item["code"] = _code(code)
        item["language"] = language
    return item


def question(prompt: str, options: list[str], answer: int, explanation: str) -> dict:
    return {"question": prompt, "options": options, "answer": answer, "explanation": explanation}


def qa(question: str, answer: str, application: str) -> dict:
    """An interview question with a model answer and where it applies in practice."""
    return {"question": question, "answer": answer, "application": application}


def lesson(
    summary: str,
    sections: list[dict],
    key_points: list[str],
    solution: str,
    quiz: list[dict],
    solution_language: str = "python",
) -> dict:
    return {
        "summary": summary,
        "sections": sections,
        "key_points": key_points,
        "solution": _code(solution),
        "solution_language": solution_language,
        "quiz": quiz,
    }
