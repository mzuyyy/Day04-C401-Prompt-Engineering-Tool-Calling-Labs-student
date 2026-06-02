from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def _sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if len(part.strip()) > 40]


def _extract_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def summarize_url(
    url: str = "",
    summary_style: str = "brief",
    language: str = "vi",
    max_points: int = 5,
) -> dict[str, Any]:
    try:
        if not url:
            raise ValueError("url is required")
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "research-agent-lab/1.0"})
        response.raise_for_status()
        text = _extract_text(response.text)
        points = _sentences(text)[: max(1, min(int(max_points or 5), 10))]
        if not points and text:
            points = [text[:500]]

        title_match = re.search(r"<title[^>]*>(.*?)</title>", response.text, flags=re.I | re.S)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else url
        if summary_style == "detailed":
            markdown = f"## {title}\n\n" + "\n".join(f"- {point}" for point in points)
        elif summary_style == "bullets":
            markdown = "\n".join(f"- {point}" for point in points)
        else:
            markdown = " ".join(points[:2])

        return {
            "tool": "summarize_url",
            "url": url,
            "source": domain(url),
            "language": language,
            "summary_style": summary_style,
            "markdown": markdown,
            "items": [{
                "title": title,
                "url": url,
                "source": domain(url),
                "summary": " ".join(points),
                "section": "URL Summary",
            }],
        }
    except Exception as exc:
        return err("summarize_url", exc)
