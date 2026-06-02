from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

import requests

from tools._shared import ROOT, TIMEOUT, err


ARXIV_DIR = ROOT / "arxiv_papers"
ARXIV_MIN_INTERVAL_SECONDS = 3.0
_last_arxiv_request_at = 0.0


def _arxiv_user_agent() -> str:
    return os.getenv("ARXIV_USER_AGENT", "AI20k-Day04-Research-Agent/1.0 (educational lab; contact: local)")


def _rate_limit_arxiv() -> None:
    global _last_arxiv_request_at
    elapsed = time.monotonic() - _last_arxiv_request_at
    if elapsed < ARXIV_MIN_INTERVAL_SECONDS:
        time.sleep(ARXIV_MIN_INTERVAL_SECONDS - elapsed)
    _last_arxiv_request_at = time.monotonic()


def _arxiv_id(value: str) -> str:
    match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", value or "")
    if not match:
        raise ValueError("Invalid arXiv ID or URL")
    return match.group(1)


def _download_arxiv_pdf(arxiv_url: str) -> tuple[str, Path, str]:
    arxiv_id = _arxiv_id(arxiv_url)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    ARXIV_DIR.mkdir(parents=True, exist_ok=True)
    output_path = ARXIV_DIR / f"{arxiv_id}.pdf"
    temp_path = output_path.with_suffix(".pdf.tmp")
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            _rate_limit_arxiv()
            response = requests.get(pdf_url, headers={"User-Agent": _arxiv_user_agent()}, timeout=TIMEOUT, stream=True)
            response.raise_for_status()
            with temp_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            data = temp_path.read_bytes()
            if not data.startswith(b"%PDF") or b"%%EOF" not in data[-2048:]:
                raise RuntimeError("Downloaded arXiv PDF appears incomplete")
            temp_path.replace(output_path)
            break
        except Exception as exc:
            last_error = exc
            temp_path.unlink(missing_ok=True)
            time.sleep(2 * (attempt + 1))
    else:
        assert last_error is not None
        raise last_error
    return arxiv_id, output_path, pdf_url


def _extract_pdf_text(pdf_path: Path, max_pages: int) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf first: pip install pypdf") from exc

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    pages_to_read = min(max(1, int(max_pages or 5)), page_count)
    parts: list[str] = []
    for page in reader.pages[:pages_to_read]:
        parts.append(page.extract_text() or "")
    return "\n\n".join(part for part in parts if part.strip()), page_count


def _cached_text(pdf_path: Path, max_chars: int) -> str:
    txt_path = pdf_path.with_suffix(".txt")
    if not txt_path.exists():
        return ""
    return txt_path.read_text(encoding="utf-8")[:max_chars]


def get_arxiv_paper_text(arxiv_url: str = "", max_pages: int = 5, max_chars: int = 8000) -> dict[str, Any]:
    try:
        arxiv_id, pdf_path, pdf_url = _download_arxiv_pdf(arxiv_url)
        max_chars = max(1000, min(int(max_chars or 8000), 20000))
        try:
            text, page_count = _extract_pdf_text(pdf_path, max_pages=max_pages)
        except Exception:
            text = _cached_text(pdf_path, max_chars)
            if not text:
                raise
            page_count = 0
        excerpt = text[:max_chars]
        txt_path = pdf_path.with_suffix(".txt")
        txt_path.write_text(excerpt, encoding="utf-8")
        return {
            "tool": "get_arxiv_paper_text",
            "arxiv_id": arxiv_id,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": pdf_url,
            "pdf_path": str(pdf_path),
            "txt_path": str(txt_path),
            "page_count": page_count,
            "pages_read": min(max(1, int(max_pages or 5)), page_count),
            "chars_returned": len(excerpt),
            "items": [{
                "title": f"arXiv paper {arxiv_id}",
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "source": "arxiv.org",
                "summary": excerpt,
            }],
        }
    except Exception as exc:
        return err("get_arxiv_paper_text", exc)
