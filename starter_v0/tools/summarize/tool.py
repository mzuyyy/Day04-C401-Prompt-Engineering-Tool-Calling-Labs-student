from __future__ import annotations

from typing import Any

from tools._shared import err


def summarize_text(
    text: str = "",
    max_length: int = 200,
    style: str = "brief",
) -> dict[str, Any]:
    try:
        if not text or not text.strip():
            return {"tool": "summarize", "error": "empty_text", "message": "No text provided to summarize"}

        words = text.split()
        if len(words) <= max_length:
            return {
                "tool": "summarize",
                "style": style,
                "original_length": len(words),
                "summary": text.strip(),
                "truncated": False,
            }

        if style == "brief":
            summary_words = words[:max_length]
            summary = " ".join(summary_words)
            if len(words) > max_length:
                summary += "..."
        elif style == "bullets":
            sentences = text.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|")
            sentences = [s.strip() for s in sentences if s.strip()]
            summary = "\n".join(f"- {s}" for s in sentences[:5])
        elif style == "key_points":
            sentences = text.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|")
            sentences = [s.strip() for s in sentences if s.strip()]
            summary = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences[:5]))
        else:
            summary_words = words[:max_length]
            summary = " ".join(summary_words) + "..."

        return {
            "tool": "summarize",
            "style": style,
            "original_length": len(words),
            "summary_length": len(summary.split()),
            "summary": summary,
            "truncated": True,
        }
    except Exception as exc:
        return err("summarize", exc)
