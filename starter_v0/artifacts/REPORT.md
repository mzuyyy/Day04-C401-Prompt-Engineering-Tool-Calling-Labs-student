# Day 04 Lab v2 Report — Research Agent

## Team

- Team: [Team Name]
- Members: [Member 1, Member 2, Member 3]
- Provider/model: openrouter / openai/gpt-4o-mini

## Final Metrics

- Final version: v3
- Final artifact_version: v3+p89882dc04213+t7915ebf3951b
- Best base run file: runs/v3_B_base_openrouter_20260602T140231917890.json
- Base case accuracy: 1.0 (20/20)
- Base tool routing accuracy: 1.0
- Base argument accuracy: 1.0
- Group eval run file: runs/v3_B_group_openrouter_20260602T140733201950.json
- Group eval accuracy: 1.0 (10/10)
- Extension eval run file: runs/v3_B_extension_openrouter_20260602T140948997167.json
- Extension eval accuracy: 0.9 (9/10)
- Chat transcript file: transcripts/v3_openrouter_20260602T141015659303.transcript.json

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Baseline prompt encourages guessing, never asking, and sending without confirmation | — | 0.70 | runs/v0_B_base_openrouter_20260602T135331357012.json |
| v1 | system_prompt.md + tools.yaml | Rewrote prompt with routing rules, clarify/out-of-scope/confirm guidance; improved tool descriptions | 0.70 | 0.90 | runs/v1_B_base_openrouter_20260602T135639452982.json |
| v2 | system_prompt.md | Added explicit yes_no confirmation rule for send; added multi-turn tool-switching rule (drop previous tool) | 0.90 | 1.00 | runs/v2_B_base_openrouter_20260602T135848252833.json |
| v3 | system_prompt.md + tools.yaml | Added parallel tool call rules, cancel/stop handling, bookmark tool registration | 1.00 | 1.00 | runs/v3_B_base_openrouter_20260602T140231917890.json |

## Failure Analysis

Baseline v0 failures (6 cases):

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | send(text="x^3/3 + C") | Agent called send to answer math question instead of refusing | v1: Added "out of scope" rule — math/coding → answer without tool |
| R10_missing_handle | missing_info | timeline(screenname="sama") | Agent guessed "sama" instead of asking user who | v1: Added clarify rule — missing handle → ask, don't guess |
| R11_missing_url | missing_info | fetch(url="https://example.com/article") | Agent invented a URL instead of asking user | v1: Added clarify rule — no URL → ask, never invent URLs |
| R12_confirm_before_send | wrong_boundary | send(text="...") | Agent sent directly without confirmation | v2: Explicit rule — send/post → clarify yes_no FIRST |
| R13_parallel_web_and_tweets | wrong_tool | lookup(query="AI news") + social_search | lookup had wrong query ("AI news" vs "AI") and missing topic="news" | v1: Added arg convention — query is core term, always set topic |
| R14_out_of_scope_coding | out_of_scope | send(text="def fibonacci...") | Agent called send to provide code instead of refusing | v1: Added "out of scope" rule — coding → answer without tool |

v1 remaining failures (2 cases):

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R12_confirm_before_send | wrong_boundary | clarify(question="provide content?", response_type="text") | Agent asked for content (text) instead of confirming action (yes_no) | v2: Explicit: "đăng/gửi" → IMMEDIATELY clarify yes_no, not ask for content |
| M06_switch_tool | wrong_tool | lookup + social_search | Agent called both tools when user said "bỏ Twitter" | v2: Added rule — "bỏ/stop/drop X" → don't use tool X |

## Team Eval Cases

10 cases added to `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_bookmark_add | Bookmark add action with URL | bookmark(action=add, url=...) | PASS |
| G02_bookmark_list | Bookmark list action | bookmark(action=list) | PASS |
| G03_out_of_scope_translate | Translation request → no tool | no_tool (refuse) | PASS |
| G04_policy_tool_usage | Policy source_citation routing | policy(policy_area=source_citation) | PASS |
| G05_missing_query_for_search | Missing topic + handle → clarify | clarify(response_type=text) | PASS |
| G06_multi_clarify_then_search | Multi-turn: carry topic + search_type + limit | social_search(query="Claude AI", search_type=Top, limit=3) | PASS |
| G07_multi_bookmark_after_fetch | Multi-turn: carry URL into bookmark | bookmark(action=add, url=...) | PASS |
| G08_multi_switch_topic | Multi-turn: drop news → switch to arXiv papers | papers(query="LLM", max_results=3) | PASS |
| G09_multi_fetch_two_urls | Multi-turn: fetch 2 URLs in parallel | fetch(url1) + fetch(url2) | PASS |
| G10_multi_confirm_send_then_cancel | Multi-turn: cancel action → no tool | no_tool (acknowledge cancel) | PASS |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tin AI hôm nay có gì nổi bật?" | lookup(query="AI", topic="news", timeframe="day") | v3 routing correct | Returned 5 AI news articles with sources |
| 2 | "Tóm tắt 5 tweet mới nhất giúp mình" | social_search(query="AI", limit=5) | Agent searched general tweets (no handle given) | Returned 5 tweets |
| 3 | "Của Elon Musk nhé" | timeline(screenname="elonmusk", limit=5) | Multi-turn carry: limit=5, map name→handle | Returned 5 Elon Musk tweets |
| 4 | "Đăng bản tin AI lên Telegram giúp mình" | clarify(question="confirm?", response_type="yes_no") | v2 confirm-before-send rule working | Agent asked for confirmation instead of sending |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | tools/send/tool.py + tools.yaml | Send tool with confirmed=true flag; agent asks yes_no before sending | Agent never sends without explicit user confirmation |
| arXiv/company policy | tools/papers/tool.py + tools/policy/tool.py | Policy search across 5 company policy docs; arXiv paper search + PDF text extraction | Policy uses trusted/untrusted text boundary; arXiv has rate limiting |
| bookmark (new tool) | tools/bookmark/tool.py + TOOL.md | Save/list/remove bookmarks locally; registered in __init__.py + tools.yaml | No external API needed; local JSON storage |

## Reflection

- **Which fixes belonged in `system_prompt.md`?** Most fixes: routing rules (which tool for which request), clarify-when-missing rules, out-of-scope refusal, confirm-before-send, multi-turn context handling (carry args, drop tools, cancel actions). The system prompt is where behavioral rules live.

- **Which fixes belonged in `tools.yaml`?** Tool descriptions needed to be specific about WHEN to use each tool (e.g., timeline = specific person's tweets, social_search = topic tweets, lookup = web news). Parameter descriptions needed conventions (topic=news for news, search_type=Top for popular). Vague descriptions caused routing confusion.

- **Which failure needed manual review instead of automatic grading?** E01 (extension): agent used policy_area="all" instead of "source_citation" for a query about tweet credibility. Both are reasonable interpretations — "all" is broader but still correct tool. Auto-grading is too strict for ambiguous policy_area routing.

- **What would you improve next?**
  1. Add more nuanced policy_area routing in the prompt (map "nguồn tin" → source_citation, "đăng/gửi" → external_publishing).
  2. Add a `summarize` tool that combines fetch + format into one step for common "read and summarize" requests.
  3. Improve multi-turn handling to better carry context across 4+ turns.
  4. Build a Streamlit UI for visual interaction with the agent.
