# Báo Cáo Cá Nhân - Lab 18: Production RAG

**Sinh viên:** Vũ Văn Huy  
**Ngày thực hiện:** 22/06/2026  
**Hình thức:** Bài lab cá nhân, triển khai toàn bộ pipeline M1-M5.

## Phân Công Cá Nhân

| Hạng mục | Nội dung thực hiện | Trạng thái | Kết quả test |
|----------|--------------------|------------|--------------|
| M1: Chunking | Semantic, hierarchical, structure-aware chunking | Hoàn thành | 13/13 |
| M2: Hybrid Search | Vietnamese BM25, dense search, RRF fusion | Hoàn thành | 5/5 |
| M3: Reranking | CrossEncoder reranker và fallback rerank | Hoàn thành | 5/5 |
| M4: Evaluation | RAGAS/fallback metrics và failure analysis | Hoàn thành | 4/4 |
| M5: Enrichment | Summary, HyQA, contextual prepend, metadata | Hoàn thành | 10/10 |

Tổng kiểm thử tự động: **37/37 tests passed**.

## Kết Quả Evaluation

| Metric | Naive Baseline | Production | Chênh lệch |
|--------|----------------|------------|------------|
| Faithfulness | 0.4437 | 0.4635 | +0.0198 |
| Answer Relevancy | 0.5595 | 0.6065 | +0.0470 |
| Context Precision | 0.2800 | 0.3073 | +0.0273 |
| Context Recall | 0.3461 | 0.3734 | +0.0273 |

Production pipeline cải thiện cả 4 metric so với naive baseline. Mức tăng tốt nhất là **Answer Relevancy**, nhờ kết hợp hybrid retrieval và reranking trước khi sinh câu trả lời.

## Nhận Xét Chính

1. **Điểm cải thiện lớn nhất:** Hybrid Search + Reranking giúp câu trả lời bám câu hỏi hơn, đặc biệt ở các câu hỏi tra cứu chính sách đơn.
2. **Khó khăn lớn nhất:** Các câu hỏi multi-hop cần lấy đồng thời nhiều tài liệu, ví dụ `thu_viec.md` và `bang_luong_2024.md`.
3. **Phát hiện quan trọng:** Các chính sách có phiên bản cũ/mới dễ gây nhầm nếu retrieval không ưu tiên từ khóa như “hiện hành”, “thay thế”, “v2024”.

## Case Study

**Câu hỏi:** Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu?

Pipeline chưa trả lời đúng vì context lấy được phần quy định “lương thử việc = 85%”, nhưng chưa lấy được bảng lương Junior cao nhất 20.000.000 VND/tháng. Đây là lỗi retrieval multi-hop: cần truy xuất cả quy tắc tính và dữ liệu đầu vào để tính ra 17.000.000 VND/tháng.

## Hướng Tối Ưu Tiếp Theo

- Thêm query decomposition cho câu hỏi cần nhiều nguồn thông tin.
- Boost token số tiền, số ngày, version policy trong BM25.
- Gắn metadata `category`, `effective_date`, `status` để lọc chính sách hiện hành.
- Giữ nguyên bảng hoặc cụm quy tắc phê duyệt trong cùng một structure-aware chunk.
