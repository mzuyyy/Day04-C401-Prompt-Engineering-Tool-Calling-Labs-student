from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


BOOKMARK_FILE = ROOT / "bookmarks.json"


def _load_bookmarks() -> list[dict[str, Any]]:
    if BOOKMARK_FILE.exists():
        return json.loads(BOOKMARK_FILE.read_text(encoding="utf-8"))
    return []


def _save_bookmarks(bookmarks: list[dict[str, Any]]) -> None:
    BOOKMARK_FILE.write_text(json.dumps(bookmarks, ensure_ascii=False, indent=2), encoding="utf-8")


def save_bookmark(
    title: str = "",
    url: str = "",
    note: str = "",
    tags: list[str] | None = None,
    action: str = "add",
    bookmark_id: int | None = None,
) -> dict[str, Any]:
    try:
        bookmarks = _load_bookmarks()

        if action == "list":
            return {
                "tool": "bookmark",
                "action": "list",
                "count": len(bookmarks),
                "bookmarks": bookmarks,
            }

        if action == "remove":
            if bookmark_id is None:
                return {"tool": "bookmark", "error": "missing_bookmark_id", "message": "Provide bookmark_id to remove"}
            before = len(bookmarks)
            bookmarks = [b for b in bookmarks if b.get("id") != bookmark_id]
            _save_bookmarks(bookmarks)
            return {
                "tool": "bookmark",
                "action": "remove",
                "removed": before - len(bookmarks),
                "remaining": len(bookmarks),
            }

        new_id = max((b.get("id", 0) for b in bookmarks), default=0) + 1
        entry = {
            "id": new_id,
            "title": title,
            "url": url,
            "note": note,
            "tags": tags or [],
            "saved_at": datetime.now().isoformat(timespec="seconds"),
        }
        bookmarks.append(entry)
        _save_bookmarks(bookmarks)
        return {
            "tool": "bookmark",
            "action": "add",
            "bookmark": entry,
            "total_bookmarks": len(bookmarks),
        }
    except Exception as exc:
        return err("bookmark", exc)
