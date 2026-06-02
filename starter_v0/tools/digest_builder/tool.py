from __future__ import annotations

from typing import Any


def _item_line(item: dict[str, Any], index: int) -> str:
    title = item.get("title") or item.get("summary") or f"Item {index}"
    url = item.get("url") or ""
    source = item.get("source") or ""
    suffix = f" ({source})" if source else ""
    link = f" - {url}" if url else ""
    return f"- {title}{suffix}{link}"


def digest_builder(
    topic: str = "",
    sources: list[str] | None = None,
    language: str = "vi",
    template: str = "research_brief",
    max_items: int = 5,
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    sources = sources or []
    items = items or []
    limit = max(1, min(int(max_items or 5), 20))
    selected = items[:limit]

    title = topic or "Research digest"
    if template == "daily_ai_vn":
        heading = f"## Ban tin AI hom nay: {title}"
        sections = ["### Diem chinh"]
    elif template == "executive":
        heading = f"## Executive brief: {title}"
        sections = ["### Key takeaways"]
    else:
        heading = f"## Research brief: {title}"
        sections = ["### Highlights"]

    if selected:
        body = [_item_line(item, idx + 1) for idx, item in enumerate(selected)]
    else:
        source_text = ", ".join(sources) if sources else "provided sources"
        body = [f"- No items were provided. Use lookup, social_search, papers, or fetch first, then pass their items to this tool from {source_text}."]

    markdown = "\n".join([heading, "", f"Language: {language}", f"Sources: {', '.join(sources) if sources else 'unspecified'}", "", *sections, *body])
    return {
        "tool": "digest_builder",
        "topic": topic,
        "sources": sources,
        "language": language,
        "template": template,
        "markdown": markdown,
        "item_count": len(selected),
    }
