---
name: digest_builder
track: team
kind: local_digest_composer
requires_env: []
inputs: [topic, sources, language, template, max_items, items]
outputs: [markdown, item_count, sources]
side_effect: false
---
# digest_builder

Composes a structured research digest from items already gathered by other
tools or provided by the user. It does not fetch new data.
