# Article QA with Gemini and TTS

This project is a small source-grounded chatbot built around a single idea: answer questions only from the text the user provided, while preserving a full conversation history across turns.

## What it does

- ingests one or more article strings
- builds a source-grounded system prompt
- keeps a `messages` history and reuses it on every call
- sends the system prompt + history to the Gemini API
- optionally converts the final answer to spoken audio with TTS

## Core files

- `src/article_qa/ingest.py` — article ingestion and source normalization
- `src/article_qa/conversation.py` — message history and prompt-building logic
- `src/article_qa/gemini_client.py` — Gemini request generation and API wrapper
- `src/article_qa/tts.py` — optional TTS support
- `src/article_qa/app.py` — CLI entry point
- `tests/test_article_qa.py` — behavior checks for the main flow

## Quick start

1. Set your Gemini API key:

```bash
export GEMINI_API_KEY="your-key"
```

2. Run a question against a source article:

```bash
PYTHONPATH=src python -m article_qa --text "The article text goes here." --question "What is the author's main argument?"
```

3. Run with spoken output:

```bash
PYTHONPATH=src python -m article_qa --text "The article text goes here." --question "Summarize the article." --speak
```

## Conversation pattern

The critical behavior is the full message history loop:

- append the user question
- call Gemini with the system prompt + all prior turns
- append the model response
- repeat the same pattern on the next question

This makes the assistant feel interactive and “expert” without requiring exotic retrieval or memory logic.

## Notes

- The project intentionally keeps the architecture simple: ingestion, chat history, Gemini API, and TTS.
- TTS is isolated behind a small interface so you can swap providers or disable it cleanly.
- If no TTS provider is configured, the app still works in text-only mode.
