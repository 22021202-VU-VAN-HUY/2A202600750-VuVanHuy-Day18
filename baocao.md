# Báo Cáo Riêng - Quá Trình Làm Lab 18

**Người thực hiện:** Vũ Văn Huy  
**Ngày:** 22/06/2026  
**Mục tiêu:** Hoàn thành Production RAG Pipeline M1-M5, dùng Mimo API thay cho OpenAI API theo cấu hình `.env`, chạy full test và tạo report.

## 1. Chuẩn Bị Môi Trường

- Dùng Python 3.11 theo `.python-version` để tránh lỗi Python 3.14 khi build `numpy`.
- Cập nhật dependency để pip resolve ổn định hơn:
  - `pandas>=2.0,<3`
  - `datasets>=2.19,<3`
  - `pytest>=8.0`
- Thêm `.venv/` vào `.gitignore`.
- Thêm biến môi trường Mimo vào `.env.example`:
  - `MIMO_API_KEY`
  - `MIMO_BASE_URL`
  - `MIMO_MODEL`

## 2. Các Bước Implement

### M1 - Advanced Chunking

- Implement `chunk_semantic()` bằng sentence split và lexical cosine fallback.
- Implement `chunk_hierarchical()` tạo parent-child chunks, child có `parent_id`.
- Implement `chunk_structure_aware()` parse markdown headers và lưu `section` metadata.

### M2 - Hybrid Search

- Implement `segment_vietnamese()` bằng `underthesea`, có fallback raw text.
- Implement BM25 index/search.
- Implement DenseSearch có production path với Qdrant + SentenceTransformer local.
- Thêm fallback in-memory hash vector khi Qdrant hoặc model chưa sẵn.
- Implement Reciprocal Rank Fusion để merge BM25 và dense results.

### M3 - Reranking

- Implement `CrossEncoderReranker`.
- Có cache model và fallback lexical rerank khi model chưa tải local.
- `benchmark_reranker()` chạy ổn định trong test.

### M4 - Evaluation

- Implement `evaluate_ragas()` trả đủ 4 metric key.
- Có production path RAGAS thật khi bật `LAB18_USE_REAL_RAGAS=1`.
- Mặc định dùng fallback overlap metric để unit test và pipeline không phụ thuộc API.
- Implement `failure_analysis()` với diagnostic tree và bottom failures.

### M5 - Enrichment

- Implement summary, hypothesis questions, contextual prepend và metadata extraction.
- Implement combined single-call mode.
- Dùng `create_llm_client()` để hỗ trợ Mimo theo chuẩn OpenAI-compatible.
- Mặc định dùng fallback để tránh gọi API hàng loạt trong test; có thể bật LLM enrichment bằng `LAB18_USE_LLM_ENRICHMENT=1`.

### Pipeline / Baseline

- Đổi hard-code `OpenAI()` và `gpt-4o-mini` sang config chung:
  - `LLM_API_KEY`
  - `LLM_BASE_URL`
  - `LLM_MODEL`
  - `create_llm_client()`
- Thêm guard: nếu LLM generation fail một lần thì không retry liên tục cho các câu sau.
- Sửa lỗi Windows console `UnicodeEncodeError: cp1252` bằng stdout/stderr UTF-8.

## 3. Kết Quả Chạy

### Unit Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

Kết quả:

```text
37 passed
```

### Full Pipeline

```powershell
.\.venv\Scripts\python.exe main.py
```

Kết quả evaluation:

| Metric | Naive Baseline | Production | Chênh lệch |
|--------|----------------|------------|------------|
| Faithfulness | 0.4437 | 0.4635 | +0.0198 |
| Answer Relevancy | 0.5595 | 0.6065 | +0.0470 |
| Context Precision | 0.2800 | 0.3073 | +0.0273 |
| Context Recall | 0.3461 | 0.3734 | +0.0273 |

Reports đã sinh:

- `reports/naive_baseline_report.json`
- `reports/ragas_report.json`

## 4. Các File Deliverable

- `src/m1_chunking.py`
- `src/m2_search.py`
- `src/m3_rerank.py`
- `src/m4_eval.py`
- `src/m5_enrichment.py`
- `src/pipeline.py`
- `analysis/failure_analysis.md`
- `analysis/group_report.md` - giữ tên file theo checker, nhưng nội dung là báo cáo cá nhân.
- `analysis/reflection_VuVanHuy.md`
- `analysis/reflections/reflection_VuVanHuy.md`
- `reports/ragas_report.json`
- `reports/naive_baseline_report.json`

## 5. Ghi Chú Quan Trọng

- Mimo được ưu tiên nếu có `MIMO_API_KEY`, kể cả khi `.env` vẫn có `OPENAI_API_KEY`.
- RAGAS thật được gate bằng `LAB18_USE_REAL_RAGAS=1` vì một số endpoint OpenAI-compatible có thể không hỗ trợ đầy đủ embedding/eval giống OpenAI.
- Enrichment LLM được gate bằng `LAB18_USE_LLM_ENRICHMENT=1` để tránh tốn API cho 105 chunks mỗi lần test.
- PDF scan ảnh bị bỏ qua vì không có text layer; cần OCR nếu muốn đưa vào RAG.

## 6. Kết Luận Cá Nhân

Bài lab giúp mình thấy rõ production RAG không chỉ là gọi embedding và LLM. Các bước chunking, hybrid retrieval, reranking, evaluation và failure analysis đều ảnh hưởng trực tiếp đến chất lượng câu trả lời. Phần khó nhất là câu hỏi multi-hop và câu hỏi có version policy; hướng tối ưu tiếp theo là query decomposition, metadata filtering và numeric boosting.
