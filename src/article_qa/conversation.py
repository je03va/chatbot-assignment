from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SYSTEM_PROMPT_TEMPLATE = """You are an expert on the following material. Answer questions accurately and only from this source, citing specifics where relevant. Here is the source text:

{source_text}
"""


def build_system_prompt(source_text: str) -> str:
    cleaned = (source_text or "").strip()
    if not cleaned:
        raise ValueError("Source text cannot be empty.")
    return SYSTEM_PROMPT_TEMPLATE.format(source_text=cleaned)


@dataclass
class ConversationSession:
    source_text: str
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.source_text = (self.source_text or "").strip()
        if not self.source_text:
            raise ValueError("Source text cannot be empty.")

    @property
    def system_prompt(self) -> str:
        return build_system_prompt(self.source_text)

    def ask(self, question: str) -> str:
        question_text = (question or "").strip()
        if not question_text:
            raise ValueError("Question text cannot be empty.")
        self.messages.append({"role": "user", "content": question_text})
        return question_text

    def record_answer(self, answer: str) -> str:
        answer_text = (answer or "").strip()
        if not answer_text:
            raise ValueError("Answer text cannot be empty.")
        self.messages.append({"role": "assistant", "content": answer_text})
        return answer_text

    def build_gemini_payload(self) -> dict[str, Any]:
        return {
            "system_instruction": self.system_prompt,
            "contents": self.messages,
        }

    def build_messages_for_display(self) -> list[dict[str, str]]:
        return [dict(message) for message in self.messages]
