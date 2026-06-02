---
name: summarize
track: bonus
kind: transform
requires_env: []
inputs: [text, max_length, style]
outputs: [summary, original_length, summary_length, truncated]
side_effect: false
---
# summarize

Summarize long text into a shorter version. Supports multiple styles:
- brief: truncate to max_length words
- bullets: extract key sentences as bullet points
- key_points: numbered list of key sentences

Use when user wants to condense long articles or research findings.
