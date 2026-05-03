from __future__ import annotations

import os
from typing import TYPE_CHECKING, Sequence

from ..schemas import ChatMessage

if TYPE_CHECKING:
    from openai import OpenAI

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


def get_client() -> OpenAI:
    from openai import OpenAI

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")
    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    return OpenAI(api_key=api_key, base_url=base_url)


def completion(
    messages: Sequence[ChatMessage],
    *,
    temperature: float | None = None,
) -> tuple[str, str]:
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = get_client()
    payload = [{"role": m.role, "content": m.content} for m in messages]
    kwargs: dict = {
        "model": model,
        "messages": payload,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    response = client.chat.completions.create(**kwargs)
    choice = response.choices[0]
    text = (choice.message.content or "").strip()
    used = getattr(response, "model", None) or model
    return text, used
