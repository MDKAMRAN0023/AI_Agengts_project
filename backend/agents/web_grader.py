import re
from typing import Literal
from pydantic import BaseModel


class WebGradeDecision(BaseModel):
    grade: Literal["good", "weak"]


def grade_web_evidence(question, context):

    question = re.sub(
        r"[^\w\s]",
        "",
        question.lower()
    )

    context = re.sub(
        r"[^\w\s]",
        "",
        context.lower()
    )

    question_words = set(question.split())
    context_words = set(context.split())

    # Common words
    common_words = question_words.intersection(context_words)

    # Remove generic words
    stop_words = {
        "what",
        "is",
        "the",
        "a",
        "an",
        "in",
        "of",
        "to",
        "can",
        "do",
        "does",
        "who",
        "how",
        "when",
        "where",
        "why",
        "which"
    }

    important_words = {
        word
        for word in question_words
        if word not in stop_words
    }

    common_important_words = (
        important_words.intersection(context_words)
    )

    # --------------------------------
    # Check numbers / years
    # --------------------------------

    question_numbers = set(
        re.findall(r"\b\d{2,4}\b", question)
    )

    context_numbers = set(
        re.findall(r"\b\d{2,4}\b", context)
    )

    # If question contains a specific year/number
    # and web evidence does not contain it,
    # evidence may not answer the exact question.
    if question_numbers:

        if not question_numbers.intersection(context_numbers):
            return "weak"

    # --------------------------------
    # Final relevance check
    # --------------------------------

    if len(common_important_words) >= 2:
        return "good"

    return "weak"