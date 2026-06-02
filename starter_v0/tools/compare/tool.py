from __future__ import annotations

from typing import Any

from tools._shared import err, terms


def compare_sources(
    source_a: str = "",
    source_b: str = "",
    label_a: str = "Source A",
    label_b: str = "Source B",
) -> dict[str, Any]:
    try:
        if not source_a or not source_b:
            return {"tool": "compare", "error": "missing_source", "message": "Both sources required"}

        terms_a = terms(source_a)
        terms_b = terms(source_b)

        common = terms_a & terms_b
        unique_a = terms_a - terms_b
        unique_b = terms_b - terms_a

        total_terms = len(terms_a | terms_b)
        similarity = len(common) / total_terms if total_terms > 0 else 0.0

        len_a = len(source_a.split())
        len_b = len(source_b.split())

        return {
            "tool": "compare",
            "label_a": label_a,
            "label_b": label_b,
            "length_a": len_a,
            "length_b": len_b,
            "common_terms": len(common),
            "unique_to_a": len(unique_a),
            "unique_to_b": len(unique_b),
            "similarity_score": round(similarity, 3),
            "overlap_percent": round(similarity * 100, 1),
            "summary": (
                f"{label_a}: {len_a} words, {len(unique_a)} unique terms. "
                f"{label_b}: {len_b} words, {len(unique_b)} unique terms. "
                f"Overlap: {len(common)} common terms ({round(similarity * 100, 1)}% similarity)."
            ),
        }
    except Exception as exc:
        return err("compare", exc)
