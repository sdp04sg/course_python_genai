"""Helpers that keep the lesson content files short and consistent.

Each lesson has a summary, tutorial sections (text plus an optional code
example), key points, a worked solution to the lesson's practice task, and a
multiple-choice quiz. Inline code in text is written with `backticks`;
paragraphs are separated by a blank line.
"""

import hashlib
import random
import re
from textwrap import dedent

# Options such as "None" or "All of them" read best where the author put them.
_FIXED_OPTION = re.compile(r"^(none( of (these|the above))?|neither|either, always|all of (them|these|the above))$", re.I)
_NUMBER = re.compile(r"^[~≈]?\$?(\d[\d,]*(\.\d+)?)\s*(%|ms|s|kb|mb|gb|tb|x)?$", re.I)


def _code(source: str) -> str:
    return dedent(source).strip("\n")


def _arrange(prompt: str, options: list[str]) -> list[str]:
    """Return the options in a stable, varied order so the right answer isn't always in the same place.

    Numeric options are sorted ascending; other options are shuffled with a seed taken from the
    question text, so the order is the same on every run. "None"-style options keep their place.
    """
    numbers = [_NUMBER.match(option.strip()) for option in options]
    if all(numbers):
        return sorted(options, key=lambda option: float(_NUMBER.match(option.strip()).group(1).replace(",", "")))
    movable = [i for i, option in enumerate(options) if not _FIXED_OPTION.match(option.strip())]
    shuffled = [options[i] for i in movable]
    random.Random(hashlib.sha256(prompt.encode()).digest()).shuffle(shuffled)
    arranged = list(options)
    for index, option in zip(movable, shuffled):
        arranged[index] = option
    return arranged


def section(heading: str, text: str, code: str | None = None, language: str = "python") -> dict:
    item = {"heading": heading, "text": text.strip()}
    if code is not None:
        item["code"] = _code(code)
        item["language"] = language
    return item


def question(prompt: str, options: list[str], answer: int, explanation: str) -> dict:
    arranged = _arrange(prompt, options)
    return {
        "question": prompt,
        "options": arranged,
        "answer": arranged.index(options[answer]),
        "explanation": explanation,
    }


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
