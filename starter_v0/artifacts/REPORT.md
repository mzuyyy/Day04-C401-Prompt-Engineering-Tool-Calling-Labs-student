# Day 04 Lab v2 Report — Research Agent

## Team

- Team: 047
- Members: blinh
- Provider/model: OpenRouter / openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent giúp tìm kiếm tin tức, tweet Twitter, paper khoa học, đọc URL, tóm tắt nội dung, so sánh nguồn, và gửi bản tin lên Telegram. Agent tự động chọn tool phù hợp, hỏi lại khi thiếu thông tin, và xác nhận trước khi thực hiện hành động gửi bài.

**Link dùng thử (deploy):**

> https://volvo-webmaster-movement-tanks.trycloudflare.com/
## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (handle, URL, xác nhận) | không |
| timeline | Lấy tweet từ 1 tài khoản Twitter cụ thể | không |
| social_search | Tìm tweet theo chủ đề/từ khóa (Latest hoặc Top) | không |
| lookup | Tìm tin tức, kiến thức chung trên web (Tavily) | không |
| fetch | Đọc nội dung từ URL cụ thể | không |
| format | Định dạng dữ liệu thành bản tin markdown | không |
| send | Gửi nội dung lên kênh Telegram (cần xác nhận) | có (bonus) |
| policy | Tìm quy định nội bộ công ty | có (bonus) |
| papers | Tìm paper khoa học trên arXiv | có (bonus) |
| paper_text | Đọc nội dung paper PDF từ arXiv | có (bonus) |
| bookmark | Lưu/xem/xóa bookmark bài viết | có (mới) |
| summarize | Tóm tắt văn bản (brief, bullets, key_points) | có (mới) |
| export | Xuất kết quả ra file markdown/JSON | có (mới) |
| compare | So sánh 2 nguồn văn bản, tính điểm tương đồng | có (mới) |

## A3. Câu hỏi mẫu để thử

1. "Tin AI hôm nay có gì nổi bật?"
2. "Tìm tweet mới nhất của Elon Musk"
3. "Paper về LLM trên arXiv, lấy 3 bài"
4. "Đọc bài này: https://openai.com/research rồi tóm tắt"
5. "Gửi bản tin AI lên Telegram" (sẽ hỏi xác nhận trước)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Prompt baseline khuyến khích đoán, bỏ qua xác nhận | 0.0 | 0.7 | runs/v0_B_base_openrouter_20260602T135331357012.json |
| v1 | system_prompt.md + tools.yaml | Thêm routing rules, clarify guidance, out-of-scope handling | 0.7 | 0.9 | runs/v1_B_base_openrouter_20260602T135639452982.json |
| v2 | system_prompt.md | Thêm rule xác nhận send bằng yes_no, rule chuyển đổi tool | 0.9 | 1.0 | runs/v2_B_base_openrouter_20260602T135848252833.json |
| v3 | system_prompt.md + tools.yaml | Thêm parallel calls, cancel handling, bookmark tool | 1.0 | 1.0 | runs/v3_B_base_openrouter_20260602T140231917890.json |

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08 | out_of_scope | send | Gửi nội dung ngoài phạm vi research | Thêm rule: từ chối yêu cầu ngoài scope |
| R10 | missing_info | timeline | Đoán handle thay vì hỏi | Thêm rule: clarify khi thiếu handle |
| R11 | missing_info | fetch | Đoán URL thay vì hỏi | Thêm rule: clarify khi thiếu URL |
| R12 | wrong_boundary | send | Hỏi nội dung thay vì xác nhận | Sửa rule: xác nhận yes_no TRƯỚC khi hỏi nội dung |
| R13 | wrong_arg_value | lookup | Thiếu tham số topic | Thêm rule: luôn set topic cho lookup |
| R14 | out_of_scope | send | Gửi khi user hỏi về dịch thuật | Thêm rule: refuse out-of-scope |
| M06 | unnecessary_tool | social_search | Gọi cả 2 tool khi user bỏ 1 tool | Thêm rule: drop tool khi user nói "bỏ/thôi" |

## B3. Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_bookmark_add | Lưu bookmark từ URL | bookmark(action=add) | PASS |
| G02_bookmark_list | Xem danh sách bookmark | bookmark(action=list) | PASS |
| G03_out_of_scope_translate | Yêu cầu dịch thuật ngoài scope | no_tool, refuse | PASS |
| G04_policy_tool_usage | Hỏi policy trích dẫn nguồn | policy(policy_area=source_citation) | PASS |
| G05_missing_query_for_search | Thiếu chủ đề tìm tweet | clarify | PASS |
| G06_multi_clarify_then_search | 3 turns: carry topic, map Top, limit | social_search(query=Claude AI, search_type=Top, limit=3) | PASS |
| G07_multi_bookmark_after_fetch | 2 turns: carry URL, lưu bookmark | bookmark(action=add, url=...) | PASS |
| G08_multi_switch_topic | 3 turns: bỏ lookup, chuyển papers | papers(query=LLM, max_results=3) | PASS |
| G09_multi_fetch_two_urls | 3 turns: đọc 2 URLs song song | fetch(url=...) x2 | PASS |
| G10_multi_confirm_send_then_cancel | 3 turns: gửi rồi hủy | no_tool, acknowledge_cancel | PASS |

**Kết quả eval group:** 10/10 PASS (100%)

## B4. Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tin AI hôm nay có gì nổi bật?" | lookup(query=AI, topic=news, timeframe=day) | v3 | Trả về 5 tin AI mới nhất với nguồn rõ ràng |
| 2 | "Tìm tweet mới nhất của Elon Musk" | timeline(screenname=elonmusk) | v3 | Lấy được tweet, trả về đúng format |
| 3 | "Paper về LLM, lấy 3 bài" | papers(query=LLM, max_results=3) | v3 | Tìm được 3 paper trên arXiv |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | runs/v3_B_base_*.json | Gửi tin nhắn thành công khi confirmed=true | Clarify yes_no trước khi gửi |
| arXiv papers | runs/v3_B_extension_*.json | Tìm và đọc paper thành công | Rate limiting, retry on 429 |
| policy | runs/v3_B_group_*.json | Tìm policy theo category | Không có |
| UI (Streamlit) | app.py | Chat interface tiếng Việt, hiển thị tool details | Chạy local |

## B6. Reflection

- **system_prompt.md:** Các fix thuộc về routing rules (khi nào dùng tool nào), clarification rules (khi nào hỏi lại), confirmation rules (xác nhận trước khi gửi), multi-turn rules (carry args, drop tool, cancel action).
- **tools.yaml:** Các fix thuộc về mô tả tool chi tiết hơn để model hiểu đúng cách dùng, thêm tool mới (bookmark, summarize, export, compare).
- **Manual review needed:** Case G10 (cancel action) - eval tự động khó đánh giá chính xác hành vi "không gọi tool" khi user hủy.
- **Improvement tiếp:** Thêm nhiều eval case hơn cho edge cases, cải thiện parallel tool calls, thêm error handling cho tool failures.
