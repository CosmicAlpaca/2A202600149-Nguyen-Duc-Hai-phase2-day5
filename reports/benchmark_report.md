# Báo cáo Đánh giá Hiệu năng (Benchmark Report)
**Sinh viên:** Nguyễn Đức Hải
**MSV:** 2A202600149
**Đề tài:** So sánh Single-Agent Baseline vs Multi-Agent Research Workflow

## 1. Kết quả thực nghiệm
Dưới đây là bảng so sánh hiệu năng dựa trên truy vấn: *"Research GraphRAG state-of-the-art and write a 500-word summary"*

| Run | Latency (s) | Tokens | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---:|---|
| **Baseline** | 89.39 | ~2,500 | 0.0005 | 8.0 | Trả về văn bản đơn luồng, thiếu chiều sâu phân tích và trích dẫn cụ thể. |
| **Multi-Agent** | 283.32 | ~6,500 | 0.0008 | 10.0 | Phân tích đa chiều, có trích dẫn nguồn từ Microsoft Research (GraphRAG-R1, LazyGraphRAG). |

## 2. Phân tích chi tiết (Analysis)

### Single-Agent Baseline
- **Ưu điểm**: Tốc độ nhanh (gần gấp 3 lần Multi-Agent), chi phí thấp.
- **Nhược điểm**: Câu trả lời mang tính tổng quát, đôi khi thiếu các thông tin cập nhật nhất (như các biến thể R1). Cấu trúc bài viết đơn giản, không có sự đối soát thông tin giữa các nguồn.

### Multi-Agent Workflow (Researcher -> Analyst -> Writer)
- **Ưu điểm**: 
    - **Độ chính xác cao**: Nhờ bước Analyst đối soát, thông tin về "GraphRAG-R1" và "LazyGraphRAG" được trích xuất chính xác.
    - **Tính minh bạch**: Có trích dẫn nguồn cụ thể [1], [2] giúp người dùng kiểm chứng được thông tin.
    - **Tính chuyên nghiệp**: Bài viết có cấu trúc rõ ràng, phù hợp với đối tượng học thuật/kỹ thuật.
- **Nhược điểm**: Độ trễ (latency) cao do phải chạy qua nhiều bước và nhiều lần gọi model. Chi phí token cao hơn do cần truyền context giữa các Agent.

## 3. Failure Mode và Cách khắc phục (Failure Mode & Fix)

### Vấn đề 1: Lỗi TypeError khi tính toán Tokens
- **Mô tả**: Hệ thống gặp lỗi `unsupported operand type(s) for +=: 'int' and 'NoneType'` khi cộng dồn số lượng token từ API Gemini.
- **Nguyên nhân**: API Gemini đôi khi trả về giá trị `None` thay vì số nguyên trong metadata của response.
- **Cách fix**: Cập nhật logic trong `benchmark.py` sử dụng cú pháp `res.metadata.get("input_tokens") or 0` để đảm bảo luôn có giá trị số nguyên khi tính toán.

### Vấn đề 2: Lỗi 503 High Demand từ Google API
- **Mô tả**: Khi chạy song song nhiều Agent, đôi khi gặp lỗi server quá tải.
- **Nguyên nhân**: Do sử dụng model Flash-Lite với tần suất cao trong thời gian ngắn vượt quá quota tạm thời của server.
- **Cách fix**: Triển khai cơ chế **Retry với Exponential Backoff** trong `LLMClient` và giới hạn `max_iterations` trong workflow để tránh gửi quá nhiều yêu cầu dồn dập.

## 4. Kết luận
Mô hình Multi-Agent vượt trội hoàn toàn về chất lượng nội dung và độ tin cậy cho các tác vụ nghiên cứu phức tạp. Mặc dù chi phí và thời gian cao hơn, nhưng giá trị thông tin mang lại là hoàn toàn xứng đáng cho các bài toán đòi hỏi tính chuyên môn cao.
