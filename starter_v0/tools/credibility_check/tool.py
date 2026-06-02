from __future__ import annotations

from typing import Any

from tools._shared import domain, err


HIGH_TRUST_DOMAINS = {
    "apnews.com",
    "bbc.com",
    "nature.com",
    "reuters.com",
    "science.org",
    "who.int",
}

LOW_TRUST_HINTS = {"blogspot.", "medium.com", "substack.com", "wordpress.", "rumor", "viral"}


def credibility_check(url: str = "", claim: str = "", check_depth: str = "standard") -> dict[str, Any]:
    try:
        if not url and not claim:
            raise ValueError("url or claim is required")
        source = domain(url) if url else ""
        checks: list[dict[str, Any]] = []
        score = 50

        if source:
            checks.append({"signal": "source_domain", "value": source})
            if source in HIGH_TRUST_DOMAINS or source.endswith(".gov") or source.endswith(".edu"):
                score += 25
                checks.append({"signal": "recognized_source", "passed": True})
            else:
                checks.append({"signal": "recognized_source", "passed": False})

            if any(hint in source for hint in LOW_TRUST_HINTS):
                score -= 20
                checks.append({"signal": "low_trust_platform_hint", "passed": False})
        else:
            score -= 10
            checks.append({"signal": "missing_url", "passed": False})

        if claim:
            checks.append({"signal": "claim_provided", "passed": True, "value": claim[:240]})
        else:
            score -= 5
            checks.append({"signal": "claim_provided", "passed": False})

        if check_depth == "standard":
            checks.append({"signal": "recommended_next_step", "value": "Corroborate with lookup or primary sources."})

        score = max(0, min(score, 100))
        rating = "high" if score >= 70 else "medium" if score >= 45 else "low"
        markdown = f"Credibility rating: **{rating}** ({score}/100)"
        if source:
            markdown += f"\n\nSource: `{source}`"
        markdown += "\n\n" + "\n".join(f"- {item['signal']}: {item.get('value', item.get('passed'))}" for item in checks)

        return {
            "tool": "credibility_check",
            "url": url,
            "claim": claim,
            "check_depth": check_depth,
            "rating": rating,
            "score": score,
            "checks": checks,
            "markdown": markdown,
        }
    except Exception as exc:
        return err("credibility_check", exc)
