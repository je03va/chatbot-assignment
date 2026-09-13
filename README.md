# Article QA with Gemini and TTS

This project is a small source-grounded Q&A app designed to answer questions only from the text the user provides. It is intentionally simple: one request, one source, one answer.

## What it does

- ingests one or more article strings or PDF/text files
- normalizes the source material into a single grounded context
- builds a source-aware system prompt that stays anchored to the provided text
- asks Gemini a single question from that source only
- optionally converts the final answer to spoken audio with TTS

## Core files

- `src/article_qa/ingest.py` — article ingestion and source normalization
- `src/article_qa/conversation.py` — source-grounded prompt construction and single-turn session behavior
- `src/article_qa/gemini_client.py` — Gemini request generation and API wrapper
- `src/article_qa/tts.py` — optional TTS support and markdown cleanup before speaking
- `src/article_qa/app.py` — CLI entry point
- `tests/test_article_qa.py` — checks for the main flow

## Quick start

1. Set your Gemini API key:

```bash
export GEMINI_API_KEY="your-key"
```

2. Run a question against a source article:

```bash
PYTHONPATH=src python -m article_qa --text "The article text goes here." --question "What is the author's main argument?"
```

3. Run against a file or PDF:

```bash
PYTHONPATH=src python -m article_qa --files /path/to/article.pdf --question "Summarize the article."
```

4. Run with spoken output:

```bash
PYTHONPATH=src python -m article_qa --text "The article text goes here." --question "Summarize the article." --speak
```

## Prompting behavior

The system prompt is intentionally structured to:

- stay grounded in the provided source text only
- answer in plain spoken English
- avoid markdown headings, bullet formatting, and noisy formatting markers
- be helpful without inventing facts or drifting beyond the article

## Notes

- The project keeps the architecture intentionally minimal: ingestion, prompt construction, Gemini API, and TTS.
- TTS output is sanitized before speaking so it reads more naturally.
- If no TTS provider is configured, the app still works in text-only mode.
