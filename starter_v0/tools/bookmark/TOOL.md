---
name: bookmark
track: bonus
kind: action
requires_env: []
inputs: [title, url, note, tags, action, bookmark_id]
outputs: [bookmark, count, bookmarks]
side_effect: true
---
# bookmark

Save research items locally for later reference. Supports add, list, and remove actions.
Use when user wants to save articles, tweets, or papers for later review.
