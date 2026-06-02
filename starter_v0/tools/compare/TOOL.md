---
name: compare
track: bonus
kind: analysis
requires_env: []
inputs: [source_a, source_b, label_a, label_b]
outputs: [similarity_score, overlap_percent, common_terms, unique_to_a, unique_to_b, summary]
side_effect: false
---
# compare

Compare two text sources for similarity and differences.
Analyzes word overlap, unique terms, and provides a similarity score.
Use when user wants to compare articles, tweets, or research findings from different sources.
