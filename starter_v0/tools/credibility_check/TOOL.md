---
name: credibility_check
track: team
kind: local_source_evaluator
requires_env: []
inputs: [url, claim, check_depth]
outputs: [rating, score, checks, markdown]
side_effect: false
---
# credibility_check

Runs a lightweight heuristic check on a URL or source for research triage. It is
not a fact-checking oracle; it flags source quality signals for the agent.
