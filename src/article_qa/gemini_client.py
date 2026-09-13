from __future__ import annotations

import os
from typing import Any


MAX_PROMPT_CHARS = 120_000


class GeminiChatClient:
    """Thin wrapper around the Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self._validate_api_key(self.api_key)

    @staticmethod
    def _validate_api_key(api_key: str | None) -> None:
        if api_key is None or not str(api_key).strip():
            raise RuntimeError("GEMINI_API_KEY is not set. Configure the environment variable before calling Gemini.")

    @staticmethod
    def _coerce_contents(messages: list[dict[str, str]]) -> list[Any]:
        try:
            from google.genai import types
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on installed package
            raise RuntimeError(
                "The 'google-genai' package is required for Gemini access. "
                "Install it with 'pip install google-genai'."
            ) from exc

        coerced: list[Any] = []
        for message in messages:
            if not isinstance(message, dict):
                raise TypeError("Each Gemini message must be a dictionary with 'role' and 'content'.")
            role = str(message.get("role", "user"))
            content = message.get("content", "")
            if not isinstance(content, str):
                content = str(content)
            coerced.append(types.Content(role=role, parts=[types.Part.from_text(text=content)]))
        return coerced

    @staticmethod
    def _truncate_prompt(text: str, max_chars: int = MAX_PROMPT_CHARS) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n\n[Prompt truncated to stay within Gemini size limits.]"

    def build_request(self, system_prompt: str, messages: list[dict[str, str]]) -> dict[str, Any]:
        if not system_prompt.strip():
            raise ValueError("system_prompt cannot be empty.")
        return {
            "model": self.model,
            "system_instruction": self._truncate_prompt(system_prompt),
            "contents": messages,
        }

    def generate(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        self._validate_api_key(self.api_key)

        try:
            from google import genai
            from google.genai import types
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on installed package
            raise RuntimeError(
                "The 'google-genai' package is required for Gemini access. "
                "Install it with 'pip install google-genai'."
            ) from exc

        client = genai.Client(api_key=self.api_key)
        request = self.build_request(system_prompt, messages)

        try:
            response = client.models.generate_content(
                model=request["model"],
                contents=self._coerce_contents(request["contents"]),
                config=types.GenerateContentConfig(system_instruction=request["system_instruction"]),
            )
        except Exception as exc:  # pragma: no cover - depends on API backend behavior
            raise RuntimeError(
                "Gemini rejected the request due to a backend/server issue or an oversized prompt. "
                "This often happens when the source article is too large or the model service is temporarily failing. "
                "Try a smaller source excerpt or a different model."
            ) from exc

        text = getattr(response, "text", None)
        if text:
            return str(text)

        candidates = getattr(response, "candidates", None)
        if candidates:
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                if not content:
                    continue
                parts = getattr(content, "parts", []) or []
                assembled = "".join(part.text for part in parts if getattr(part, "text", None))
                if assembled:
                    return assembled

        raise RuntimeError("Gemini returned no usable text content.")
