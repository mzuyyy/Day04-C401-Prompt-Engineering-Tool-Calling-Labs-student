---
name: export
track: bonus
kind: action
requires_env: []
inputs: [items, filename, format, title]
outputs: [filename, filepath, item_count, size_bytes]
side_effect: true
---
# export

Export research items to a file. Supports markdown and JSON formats.
Use when user wants to save research results to a file for later reference or sharing.
