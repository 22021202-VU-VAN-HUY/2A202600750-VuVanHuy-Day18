# Bao cao rieng - Qua trinh lam Lab 18

**Nguoi thuc hien:** Vu Van Huy  
**Ngay:** 22/06/2026  
**Muc tieu:** Hoan thanh Production RAG Pipeline M1-M5, dung Mimo API thay OpenAI API, chay test va tao report.

## 1. Setup moi truong

- Dung Python 3.11 theo `.python-version`; tranh loi Python 3.14 khi build `numpy`.
- Cap nhat dependency:
  - `pandas>=2.0,<3`
  - `datasets>=2.19,<3`
  - `pytest>=8.0`
- Them `.venv/` vao `.gitignore`.
- Them bien Mimo vao `.env.example`:
  - `MIMO_API_KEY`
  - `MIMO_BASE_URL`
  - `MIMO_MODEL`

## 2. Cac step implement

### M1 - Advanced Chunking
- Implement `chunk_semantic()` bang sentence split + lexical cosine fallback.
- Implement `chunk_hierarchical()` tao parent-child chunks, child co `parent_id`.
- Implement `chunk_structure_aware()` parse markdown headers va luu `section`.

### M2 - Hybrid Search
- Implement `segment_vietnamese()` voi `underthesea`, fallback raw text.
- Implement BM25 index/search.
- Implement DenseSearch production path voi Qdrant + SentenceTransformer local.
- Them fallback in-memory hash vector khi Qdrant/model khong san.
- Implement Reciprocal Rank Fusion.

### M3 - Reranking
- Implement `CrossEncoderReranker`.
- Co cache model va fallback lexical rerank khi model chua tai local.
- Benchmark van chay on dinh trong test.

### M4 - Evaluation
- Implement `evaluate_ragas()` co du 4 metric key.
- Co production path RAGAS khi bat `LAB18_USE_REAL_RAGAS=1`.
- Mac dinh dung fallback overlap metric de unit test va pipeline khong phu thuoc API.
- Implement `failure_analysis()` voi diagnostic tree va bottom failures.

### M5 - Enrichment
- Implement summary, HyQA questions, contextual prepend, metadata extraction.
- Implement combined single-call mode.
- Dung `create_llm_client()` de ho tro Mimo OpenAI-compatible.
- Mac dinh fallback de tranh goi API hang loat trong test; bat LLM enrichment bang `LAB18_USE_LLM_ENRICHMENT=1`.

### Pipeline / Baseline
- Doi hard-code `OpenAI()` va `gpt-4o-mini` sang config chung:
  - `LLM_API_KEY`
  - `LLM_BASE_URL`
  - `LLM_MODEL`
  - `create_llm_client()`
- Them guard: neu LLM generation fail mot lan thi khong retry lien tuc.
- Sua loi Windows console `UnicodeEncodeError: cp1252` bang stdout/stderr UTF-8.

## 3. Ket qua chay

### Unit tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

Ket qua:

```text
37 passed
```

### Full pipeline

```powershell
.\.venv\Scripts\python.exe main.py
```

Ket qua:

| Metric | Naive | Production | Delta |
|--------|-------|------------|-------|
| Faithfulness | 0.4437 | 0.4635 | +0.0198 |
| Answer Relevancy | 0.5595 | 0.6065 | +0.0470 |
| Context Precision | 0.2800 | 0.3073 | +0.0273 |
| Context Recall | 0.3461 | 0.3734 | +0.0273 |

Reports sinh ra:

- `reports/naive_baseline_report.json`
- `reports/ragas_report.json`

## 4. Cac file deliverable da viet

- `src/m1_chunking.py`
- `src/m2_search.py`
- `src/m3_rerank.py`
- `src/m4_eval.py`
- `src/m5_enrichment.py`
- `src/pipeline.py`
- `analysis/failure_analysis.md`
- `analysis/group_report.md`
- `analysis/reflection_VuVanHuy.md`
- `analysis/reflections/reflection_VuVanHuy.md`
- `reports/ragas_report.json`
- `reports/naive_baseline_report.json`

## 5. Ghi chu quan trong

- Mimo duoc uu tien neu co `MIMO_API_KEY`, ke ca khi `.env` van co `OPENAI_API_KEY`.
- RAGAS that bi gate bang `LAB18_USE_REAL_RAGAS=1` vi mot so endpoint OpenAI-compatible co the khong ho tro embedding/eval dung nhu OpenAI.
- Enrichment LLM bi gate bang `LAB18_USE_LLM_ENRICHMENT=1` de tranh ton API cho 105 chunks moi lan test.
- PDF scan anh bi bo qua vi khong co text layer; can OCR neu muon dua vao RAG.
