from typing import Literal
from pydantic import BaseModel


class GradeDecision(BaseModel):
    grade: Literal["good", "weak"]


def grade_evidence(question, context):

    question_words = set(question.lower().split())
    context_words = set(context.lower().split())

    common_words = question_words.intersection(context_words)

    # Remove very common words
    common_words = {
        word for word in common_words
        if word not in {
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
            "does"
        }
    }

    if len(common_words) >= 2:
        return "good"

    return "weak"