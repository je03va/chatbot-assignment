from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _read_file_contents(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on installed package
            raise RuntimeError(
                "PDF support requires the 'pypdf' package. "
                "Install it with 'pip install pypdf'."
            ) from exc

        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            extracted = page.extract_text() or ""
            if extracted.strip():
                pages.append(extracted.strip())
        return "\n\n".join(pages)

    return path.read_text(encoding="utf-8")


def normalize_articles(articles: str | Iterable[str] | None) -> str:
    """Coalesce one or many article strings into a single source text."""
    if articles is None:
        return ""

    if isinstance(articles, str):
        return articles.strip()

    parts = []
    for article in articles:
        if article is None:
            continue
        cleaned = str(article).strip()
        if cleaned:
            parts.append(cleaned)
    return "\n\n".join(parts)


def load_article_text(paths: str | Iterable[str] | None) -> str:
    """Read one or more text or PDF files and combine them into a single source string."""
    if paths is None:
        return ""

    if isinstance(paths, str):
        paths = [paths]

    chunks: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.exists() and path.is_file():
            chunks.append(_read_file_contents(path))
    return normalize_articles(chunks)
