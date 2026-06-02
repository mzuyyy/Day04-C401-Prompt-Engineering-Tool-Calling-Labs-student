from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


EXPORT_DIR = ROOT / "exports"


def export_digest(
    items: list[dict[str, Any]] | None = None,
    filename: str = "",
    format: str = "markdown",
    title: str = "Research Digest",
) -> dict[str, Any]:
    try:
        if not items:
            return {"tool": "export", "error": "no_items", "message": "No items to export"}

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"digest_{timestamp}.{format}"

        filepath = EXPORT_DIR / filename

        if format == "markdown":
            lines = [f"# {title}\n", f"Generated: {datetime.now().isoformat(timespec='seconds')}\n"]
            for i, item in enumerate(items, 1):
                lines.append(f"\n## {i}. {item.get('title', 'Untitled')}\n")
                if item.get('url'):
                    lines.append(f"**Source:** [{item.get('source', 'Link')}]({item['url']})\n")
                if item.get('summary'):
                    lines.append(f"\n{item['summary']}\n")
            content = "\n".join(lines)
        elif format == "json":
            data = {
                "title": title,
                "generated": datetime.now().isoformat(timespec="seconds"),
                "items": items,
            }
            content = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            return {"tool": "export", "error": "unsupported_format", "message": f"Format '{format}' not supported"}

        filepath.write_text(content, encoding="utf-8")

        return {
            "tool": "export",
            "format": format,
            "filename": filename,
            "filepath": str(filepath),
            "item_count": len(items),
            "size_bytes": len(content.encode("utf-8")),
        }
    except Exception as exc:
        return err("export", exc)
