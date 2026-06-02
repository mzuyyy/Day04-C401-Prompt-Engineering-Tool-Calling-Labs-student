Listed directory DAY4_lab
Ran command: `git clone https://github.com/VinUni-AI20k/Day04-C401-Prompt-Engineering-Tool-Calling-Labs-student .`
Listed directory DAY4_lab
Viewed README.md:1-267

Chào bạn, dựa vào nội dung `README.md` của kho lưu trữ Github mà bạn cung cấp, bài lab này có khối lượng công việc khá rõ ràng xoay quanh việc xây dựng, đánh giá và tối ưu một Research Agent. Dưới đây là đề xuất phân chia công việc tối ưu và cân bằng nhất dành cho nhóm 3 người, dựa trên thế mạnh của từng vai trò:

### 🧑‍💻 Thành viên 1: AI Prompt Engineer & Tester (Tập trung vào Logic của Agent)
**Nhiệm vụ chính:** Tối ưu hóa khả năng suy luận và sử dụng công cụ của Agent.
*   **Tinh chỉnh Prompt & Công cụ:** Chịu trách nhiệm chính trong việc chỉnh sửa `artifacts/system_prompt.md` và `artifacts/tools.yaml` để khắc phục lỗi sau mỗi vòng đánh giá (v1, v2, v3).
*   **Thiết kế Test Case:** Viết 10 test case mới vào `data/eval_group.json` (5 single-turn và 5 multi-turn) đảm bảo độ phủ các trường hợp lỗi như `wrong_tool`, `missing_info`...
*   **Chat Live:** Chạy `chat.py` để tương tác trực tiếp nhiều vòng (multi-round) với Agent, thử nghiệm các kịch bản thực tế và tạo ra file log `transcripts/*.transcript.json`.

### 📊 Thành viên 2: Data Analyst & Reporter (Tập trung vào Đánh giá & Báo cáo)
**Nhiệm vụ chính:** Đảm bảo quá trình chạy đánh giá trơn tru, ghi nhận dữ liệu và viết báo cáo cuối cùng.
*   **Setup Môi trường:** Cấu hình file `.env` chứa API keys và chạy `scripts/preflight_provider.py` để đảm bảo kết nối API thành công.
*   **Chạy Pipeline Đánh Giá:** Chạy tập lệnh `run_eval.py` cho phiên bản baseline (`v0`) và các phiên bản tối ưu (`v1, v2, v3, group_eval`).
*   **Phân tích Lỗi:** Đọc file run JSON để tìm ra lý do agent bị lỗi (`observed_mismatch`, `failures`), cung cấp insight (giả thuyết) cho **Thành viên 1** sửa prompt.
*   **Ghi chú & Báo cáo:** Cập nhật liên tục file `artifacts/version_log.csv` và chịu trách nhiệm viết file tổng kết `artifacts/REPORT.md`.

### 🛠️ Thành viên 3: Software Engineer (Tập trung vào Lập trình & Điểm thưởng Bonus)
**Nhiệm vụ chính:** Viết code Python tạo các công cụ mới và xây dựng giao diện.
*   **Phát triển Tool Bắt buộc:** Code ít nhất 1 tool mới (tạo folder, viết `tool.py`, `TOOL.md`, và đăng ký vào `tools/__init__.py`).
*   **Săn Điểm Thưởng (Bonus Tools):** Code các công cụ nâng cao như `send` (có yêu cầu xác nhận), `policy` (đọc markdown nội bộ), `papers` và `paper_text` (tích hợp arXiv). Mục tiêu là làm >3 tool mới.
*   **Xây dựng Giao diện (UI):** Dựng một UI đơn giản bằng **Streamlit** (hoặc Vercel) để tương tác trực quan với Agent thay vì chỉ dùng terminal, nhằm lấy trọn vẹn điểm thưởng của giảng viên.

---

**⏳ Đề xuất phối hợp (Timeline 4 tiếng):**
*   **Giờ 1:** TV2 setup môi trường và chạy Baseline (v0). TV3 bắt đầu code ngay 1 tool cơ bản. TV1 bắt đầu đọc cấu trúc Prompt và log lỗi của v0 do TV2 gửi.
*   **Giờ 2:** TV1 và TV2 phối hợp lặp lại vòng lặp: **Sửa Prompt (TV1) -> Chạy Eval & Ghi Log (TV2)** để hoàn thiện v1, v2. TV3 tập trung code các Bonus tools.
*   **Giờ 3:** TV1 viết 10 Eval cases mới. TV2 chạy v3 và group eval. TV3 bắt đầu dựng UI Streamlit.
*   **Giờ 4:** TV1 chạy live chat. TV2 viết Report. TV3 hoàn thiện code và hỗ trợ TV2 kiểm tra lại toàn bộ file trước khi nộp.

Bạn thấy cách phân chia này đã phù hợp với kỹ năng của các thành viên trong nhóm bạn chưa? Nếu cần, tôi có thể điều chỉnh lại tỷ trọng công việc!