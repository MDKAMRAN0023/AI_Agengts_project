import os

os.environ["HF_HUB_DISABLE_XET"] = "1"

from transformers import pipeline


_llm = None


def get_llm():

    global _llm

    if _llm is None:

        _llm = pipeline(
            "text-generation",
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            device=-1,
            return_full_text=False,
            clean_up_tokenization_spaces=False
        )

    return _llm