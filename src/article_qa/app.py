from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from article_qa.conversation import ConversationSession
from article_qa.gemini_client import GeminiChatClient
from article_qa.ingest import load_article_text, normalize_articles
from article_qa.tts import TTSEngine

load_dotenv()


def _run_chat(source_text: str, question: str, *, api_key: str | None = None, speak: bool = False) -> tuple[str, bytes | None]:
    session = ConversationSession(source_text)
    session.ask(question)
    client = GeminiChatClient(api_key=api_key or os.getenv("GEMINI_API_KEY"))
    payload = session.build_gemini_payload()
    response = client.generate(payload["system_instruction"], payload["contents"])
    session.record_answer(response)

    audio = None
    if speak:
        engine = TTSEngine()
        audio = engine.synthesize(response)
        engine.play(audio)

    return response, audio


def main() -> None:
    parser = argparse.ArgumentParser(description="Source-grounded Gemini Q&A with optional TTS.")
    parser.add_argument("--text", help="The source article text to ground the chatbot in.")
    parser.add_argument("--files", nargs="*", default=[], help="Optional text files to ingest as source material.")
    parser.add_argument("--question", required=True, help="The question to answer from the provided source text.")
    parser.add_argument("--api-key", default=None, help="Optional Gemini API key. Defaults to GEMINI_API_KEY env var.")
    parser.add_argument("--speak", action="store_true", help="Speak the final response using the configured TTS engine.")
    args = parser.parse_args()

    if args.text:
        source_text = normalize_articles(args.text)
    elif args.files:
        source_text = load_article_text(args.files)
    else:
        raise ValueError("Provide either --text or --files for the source material.")

    response, audio = _run_chat(source_text, args.question, api_key=args.api_key, speak=args.speak)
    print(response)
    if args.speak and audio is not None:
        print("Playing spoken output...")


if __name__ == "__main__":
    main()
