from __future__ import annotations

import os
from typing import Any


class GeminiChatClient:
    """Thin wrapper around the Gemini API."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model

    def build_request(self, system_prompt: str, messages: list[dict[str, str]]) -> dict[str, Any]:
        if not system_prompt.strip():
            raise ValueError("system_prompt cannot be empty.")
        return {
            "model": self.model,
            "system_instruction": system_prompt,
            "contents": messages,
        }

    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Configure the environment variable before calling Gemini.")

        try:
            from google import genai
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on installed package
            raise RuntimeError(
                "The 'google-genai' package is required for Gemini access. "
                "Install it with 'pip install google-genai'."
            ) from exc

        client = genai.Client(api_key=self.api_key)
        request = self.build_request(system_prompt, messages)

        response = client.models.generate_content(
            model=request["model"],
            contents=request["contents"],
            config={"system_instruction": request["system_instruction"]},
        )

        text = getattr(response, "text", None)
        if text:
            return str(text)

        candidate = getattr(response, "candidates", None)
        if candidate and candidate[0].content:
            parts = getattr(candidate[0].content, "parts", [])
            if parts:
                return "".join(getattr(part, "text", "") for part in parts if getattr(part, "text", None))

        raise RuntimeError("Gemini returned no usable text content.")
