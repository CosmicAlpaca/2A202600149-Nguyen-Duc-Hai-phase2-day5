# Multi-Agent System Design: GraphRAG Research Lab

## Problem
Hệ thống cần thực hiện nghiên cứu chuyên sâu về chủ đề "GraphRAG state-of-the-art", bao gồm việc tìm kiếm nguồn tin cậy, phân tích các khẳng định kỹ thuật và tổng hợp thành một bản tóm tắt khoảng 500 chữ có trích dẫn nguồn đầy đủ.

## Why multi-agent?
- **Separation of Concerns**: Việc tách biệt các kỹ năng Tìm kiếm (Researcher), Phân tích (Analyst) và Viết lách (Writer) giúp mỗi bước được tối ưu hóa bằng các prompt chuyên biệt.
- **Context Management**: Tránh việc LLM bị quá tải thông tin khi phải làm quá nhiều việc trong một prompt duy nhất (dilution of focus).
- **Error Isolation**: Nếu bước tìm kiếm thất bại, hệ thống có thể phát hiện sớm trước khi tiến hành viết bài.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối luồng công việc, quyết định agent tiếp theo | Shared State | Tên Agent kế tiếp | Lặp vô hạn nếu router logic sai |
| Researcher | Tìm kiếm web (DuckDuckGo) và tóm tắt nguồn | Query | Sources & Research Notes | Kết quả tìm kiếm không liên quan |
| Analyst | Phân tích các claim, đối chiếu thông tin và rút trích insight | Research Notes | Analysis Notes | Ảo giác (hallucination) hoặc bỏ lỡ chi tiết kỹ thuật |
| Writer | Tổng hợp báo cáo cuối cùng (500 chữ) với trích dẫn | Analysis Notes | Final Answer | Không tuân thủ số lượng từ hoặc trích dẫn sai |

## Shared state
- `request`: Chứa query gốc và yêu cầu về audience/sources.
- `sources`: Danh sách URL và tiêu đề tài liệu tham khảo.
- `research_notes`: Dữ liệu thô trích xuất từ các trang web.
- `analysis_notes`: Thông tin đã qua sàng lọc và cấu trúc hóa.
- `final_answer`: Kết quả đầu ra cuối cùng cho người dùng.
- `agent_results`: Lưu vết tokens và latency để làm benchmark.

## Routing policy
Sử dụng mô hình **Supervisor/Router** tập trung:
1. `START` -> `Supervisor`
2. `Supervisor` -> `Researcher` -> `Supervisor`
3. `Supervisor` -> `Analyst` -> `Supervisor`
4. `Supervisor` -> `Writer` -> `Supervisor`
5. `Supervisor` -> `END` (khi Writer hoàn tất)

## Guardrails
- **Max iterations**: 6 (Ngăn chặn vòng lặp vô hạn giữa Supervisor và các Agent).
- **Timeout**: 60 giây cho mỗi Agent (Đảm bảo hệ thống không treo).
- **Retry**: Tự động thử lại khi gặp lỗi API 503 (High Demand).
- **Fallback**: Trả về thông báo lỗi thân thiện nếu Workflow không thể hoàn thành sau max iterations.
- **Validation**: Analyst đóng vai trò validator cho dữ liệu của Researcher.

## Benchmark plan
- **Query**: "Research GraphRAG state-of-the-art and write a 500-word summary"
- **Metric**: 
    - Latency (giây)
    - Total Tokens (Input + Output)
    - Estimated Cost (USD)
    - Quality Score (Dựa trên độ dài, từ khóa chuyên môn và số lượng trích dẫn).
- **Expected outcome**: Hệ thống Multi-Agent sẽ có latency cao hơn nhưng Quality Score và độ chính xác của trích dẫn vượt trội so với Single-Agent Baseline.
