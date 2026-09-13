from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


SYSTEM_PROMPT_TEMPLATE = """You are a careful research assistant helping a user understand the provided source material. Answer questions only from this source, and stay grounded in what it actually says. When useful, transform the material into clear, conversational explanations, concise summaries, comparisons, and practical takeaways in plain spoken English. Do not invent facts, add outside knowledge, or speculate beyond the source. If the text does not answer a question directly, say so plainly and avoid guessing. Keep the tone natural, helpful, and easy to follow, with no markdown headings, bullet lists, bold markers, or other formatting.

Source text:

{source_text}
"""


def strip_markdown(text: str) -> str:
    """Normalize source text and spoken output into plain prose."""
    if text is None:
        return ""

    cleaned = str(text)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\d+\.\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*|__|~~|`", "", cleaned)
    cleaned = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    return cleaned.strip()


def build_system_prompt(source_text: str) -> str:
    cleaned = strip_markdown(source_text or "")
    if not cleaned:
        raise ValueError("Source text cannot be empty.")
    return SYSTEM_PROMPT_TEMPLATE.format(source_text=cleaned)


@dataclass
class ConversationSession:
    source_text: str
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.source_text = strip_markdown(self.source_text or "").strip()
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
