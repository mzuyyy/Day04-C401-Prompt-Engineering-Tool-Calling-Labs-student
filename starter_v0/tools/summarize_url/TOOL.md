---
name: summarize_url
track: team
kind: local_url_summarizer
requires_env: []
inputs: [url, summary_style, language, max_points]
outputs: [markdown, items, url, source]
side_effect: false
---
# summarize_url

Fetches a URL with a simple HTTP request, extracts readable text, and returns a
short markdown summary. Use when the user asks to summarize a concrete URL.
