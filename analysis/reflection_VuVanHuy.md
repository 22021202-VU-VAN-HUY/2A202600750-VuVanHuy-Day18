# Reflection Cá Nhân - Lab 18

**Họ tên:** Vũ Văn Huy  
**Mã học viên:** 2A202600750
**Module phụ trách:** Toàn bộ pipeline M1-M5  
**Kết quả test:** 37/37 tests passed  
**Kết quả chạy pipeline:** Đã tạo `reports/naive_baseline_report.json` và `reports/ragas_report.json`.

## 1. Mapping Bài Giảng Vào Code

| Lecture Concept | Module | Hàm/Class cụ thể | Quan sát |
|----------------|--------|------------------|----------|
| Semantic chunking | M1 | `chunk_semantic()` | Tách câu và gom câu gần chủ đề bằng cosine lexical fallback, giúp không cắt ngữ cảnh quá vụn khi chưa có embedding local. |
| Hierarchical chunking | M1 | `chunk_hierarchical()` | Tạo parent chunk giữ ngữ cảnh rộng và child chunk để retrieve chính xác. Pipeline tạo 105 child chunks từ 26 tài liệu. |
| Structure-aware chunking | M1 | `chunk_structure_aware()` | Parse markdown headers và lưu `section` metadata, phù hợp với tài liệu chính sách có heading/bảng/quy tắc. |
| BM25 + Dense fusion | M2 | `BM25Search`, `DenseSearch`, `reciprocal_rank_fusion()` | BM25 bắt keyword tiếng Việt, dense/hash fallback bắt gần nghĩa, RRF giảm rủi ro phụ thuộc vào một retriever. |
| Cross-encoder reranking | M3 | `CrossEncoderReranker.rerank()` | Có production path dùng CrossEncoder và fallback lexical khi model chưa có local; kết quả vẫn sort theo `rerank_score`. |
| RAGAS 4 metrics | M4 | `evaluate_ragas()` | Có đường chạy RAGAS thật khi bật `LAB18_USE_REAL_RAGAS=1`, mặc định dùng fallback metrics để test ổn định. |
| Failure diagnostic tree | M4 | `failure_analysis()` | Bottom failures cho thấy lỗi chính nằm ở context recall/precision trong câu hỏi multi-hop và câu hỏi versioned policy. |
| Contextual enrichment | M5 | `contextual_prepend()`, `_enrich_single_call()` | Fallback thêm nguồn tài liệu vào chunk; khi bật `LAB18_USE_LLM_ENRICHMENT=1` có thể dùng Mimo để sinh summary/questions/context/metadata. |

## 2. Khó Khăn Và Cách Giải Quyết

- **Sai phiên bản Python:** Ban đầu `pip install -r requirements.txt` lỗi vì Python 3.14 phải build `numpy==1.26.4` từ source và máy thiếu C compiler. Cách xử lý là dùng Python 3.11 theo `.python-version`.
- **Resolver dependency:** `datasets>=2.19` kéo nhiều version và phụ thuộc `pandas`. Mình pin thêm `pandas>=2.0,<3` và `datasets>=2.19,<3` để resolver ổn định hơn.
- **Dùng Mimo thay OpenAI:** Scaffold hard-code `OPENAI_API_KEY`, `OpenAI()`, và `gpt-4o-mini`. Mình thêm `MIMO_API_KEY`, `MIMO_BASE_URL`, `MIMO_MODEL`, `create_llm_client()` trong `config.py`, sau đó dùng client chung trong pipeline/baseline/M5.
- **Phụ thuộc model/service ngoài:** Qdrant, SentenceTransformer và CrossEncoder có thể chưa sẵn trên máy chấm. Mình giữ production path nhưng thêm fallback hash/lexical để test và pipeline không bị crash.
- **Lỗi Unicode trên Windows:** `main.py` từng lỗi `UnicodeEncodeError: cp1252` khi in ký tự Unicode. Mình reconfigure stdout/stderr UTF-8 trong các entrypoint chính.

## 3. Action Plan Cho Project

## Project: Internal Policy RAG Assistant

### Hiện tại

- RAG pipeline hiện tại load markdown/PDF text layer, chunk theo hierarchical strategy, hybrid retrieve, rerank, rồi sinh câu trả lời bằng LLM OpenAI-compatible.
- Known issues: câu hỏi multi-hop cần lấy nhiều tài liệu, chính sách cũ/mới dễ bị nhầm, các câu hỏi có số tiền/ngưỡng phê duyệt cần boost tốt hơn.

### Plan Áp Dụng

1. [ ] **Chunking strategy:** Dùng hierarchical + structure-aware chunking cho tài liệu chính sách; giữ bảng approval trong cùng chunk.
2. [ ] **Search:** Dùng BM25 + dense hybrid; boost số tiền, số ngày, version, trạng thái “hiện hành/đã thay thế”.
3. [ ] **Reranking:** Dùng CrossEncoder khi đã cache model; fallback lexical trong CI/offline.
4. [ ] **Evaluation:** Dùng RAGAS thật khi có API budget; hằng ngày dùng fallback metrics và regression test set.
5. [ ] **Enrichment:** Dùng Mimo enrichment cho batch nhỏ, sinh summary/questions/metadata và cache kết quả.

### Timeline

- **Tuần 1:** Hoàn thiện metadata extraction: source, category, effective_date, status.
- **Tuần 2:** Thêm multi-query decomposition cho câu hỏi tính toán và multi-hop.
- **Tuần 3:** Thêm citation audit, rerank tuning và threshold-specific tests.
- **Tuần 4:** Chạy eval định kỳ, ghi failure dashboard và tối ưu prompt.

## 4. Tự Đánh Giá

| Tiêu chí | Tự chấm (1-5) | Ghi chú |
|----------|---------------|---------|
| Hiểu bài giảng | 5 | Đã map đủ M1-M5 vào code và report. |
| Code quality | 4 | Có fallback và tests, nhưng có thể tách helper thành module riêng hơn. |
| Problem solving | 5 | Đã xử lý dependency, Mimo config, Unicode Windows và fallback model. |
| Evaluation mindset | 4 | Có report/failure analysis, nhưng RAGAS thật được gate bằng env để tránh tốn API trong test. |
