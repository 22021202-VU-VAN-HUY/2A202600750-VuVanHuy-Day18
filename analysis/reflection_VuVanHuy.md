# Individual Reflection - Lab 18

**Ten:** Vu Van Huy  
**Module phu trach:** Full pipeline M1-M5  
**Tests:** 37/37 passed  
**Run:** `python main.py` da tao `reports/naive_baseline_report.json` va `reports/ragas_report.json`.

## 1. Mapping bai giang vao code

| Lecture Concept | Module | Ham/Class cu the | Observation |
|----------------|--------|------------------|-------------|
| Semantic chunking | M1 | `chunk_semantic()` | Dung sentence boundary + lexical cosine fallback de gom cau lien quan; tranh cat giua y khi khong co embedding local. |
| Hierarchical chunking | M1 | `chunk_hierarchical()` | Parent chunk giu ngu canh dai, child chunk dung cho retrieval chinh xac; pipeline index 105 child chunks tu 26 documents. |
| Structure-aware chunking | M1 | `chunk_structure_aware()` | Parse markdown headers va giu `section` metadata; huu ich cho policy co bang/quy tac theo section. |
| BM25 + Dense fusion | M2 | `BM25Search`, `DenseSearch`, `reciprocal_rank_fusion()` | BM25 bat keyword/tieng Viet, dense/hash fallback bat ngu nghia; RRF hop nhat rank list va giam lech do mot retriever sai. |
| Cross-encoder reranking | M3 | `CrossEncoderReranker.rerank()` | Thu load CrossEncoder local, fallback lexical khi model chua tai; ket qua van sorted va uu tien doc lien quan trong tests. |
| RAGAS 4 metrics | M4 | `evaluate_ragas()` | Co production path RAGAS that khi bat `LAB18_USE_REAL_RAGAS=1`, mac dinh fallback metric de test/pipeline on dinh. |
| Failure diagnostic tree | M4 | `failure_analysis()` | Bottom failures cho thay loi chinh la context recall/precision trong cau hoi multi-hop va versioned policy. |
| Contextual enrichment | M5 | `contextual_prepend()`, `_enrich_single_call()` | Fallback them prefix source vao chunk; khi bat `LAB18_USE_LLM_ENRICHMENT=1` co the dung Mimo de sinh summary/questions/context/metadata. |

## 2. Kho khan va cach giai quyet

- **Python version:** Ban dau `pip install -r requirements.txt` loi do Python 3.14 build `numpy==1.26.4` tu source va thieu C compiler. Cach xu ly: dung Python 3.11 theo `.python-version`.
- **Dependency resolver:** `datasets>=2.19` keo pandas moi va co luc pip bao khong co distribution. Cach xu ly: pin `pandas>=2.0,<3` va `datasets>=2.19,<3`.
- **Mimo thay OpenAI:** Repo scaffold hard-code `OPENAI_API_KEY`, `OpenAI()`, va `gpt-4o-mini`. Cach xu ly: them `MIMO_API_KEY`, `MIMO_BASE_URL`, `MIMO_MODEL`, `create_llm_client()` trong `config.py`, sau do pipeline/baseline/M5 dung client chung.
- **Model va service ngoai:** CrossEncoder, SentenceTransformer, Qdrant co the chua san tren may cham. Cach xu ly: production path van co, nhung co fallback hash/lexical de test va pipeline khong bi crash.
- **Windows Unicode:** `main.py` loi `UnicodeEncodeError: cp1252` khi in emoji. Cach xu ly: reconfigure stdout/stderr UTF-8 trong `main.py`, `pipeline.py`, `naive_baseline.py`, `check_lab.py`.

## 3. Action Plan cho project

## Project: Internal Policy RAG Assistant

### Hien tai
- RAG pipeline hien tai: load markdown/PDF text layer, chunk hierarchical, hybrid retrieve, rerank, generate answer bang LLM OpenAI-compatible.
- Known issues: cau hoi multi-hop can lay nhieu tai lieu, versioned policy de nham ban cu, numeric threshold/bang phe duyet chua duoc boost.

### Plan ap dung
1. [ ] Chunking strategy: dung hierarchical + structure-aware cho policy section; giu bang approval trong cung chunk.
2. [ ] Search: hybrid BM25/Dense, them boost cho so tien, ngay, version, va tu khoa phong ban.
3. [ ] Reranking: dung CrossEncoder local neu da cache; fallback lexical trong CI/offline.
4. [ ] Evaluation: chay RAGAS that khi co API budget, con hang ngay dung fallback metrics + regression test set.
5. [ ] Enrichment: bat Mimo enrichment cho batch nho, sinh summary/questions/metadata; cache ket qua de tranh goi lai.

### Timeline
- Tuan 1: Hoan thien metadata extraction, source/effective_date/category.
- Tuan 2: Them multi-query decomposition cho cau hoi tinh toan va multi-hop.
- Tuan 3: Them rerank/citation audit va threshold-specific tests.
- Tuan 4: Chay eval hang ngay, ghi failure dashboard va toi uu prompt.

## 4. Tu danh gia

| Tieu chi | Tu cham (1-5) | Ghi chu |
|----------|---------------|---------|
| Hieu bai giang | 5 | Da map du M1-M5 vao code va report. |
| Code quality | 4 | Co fallback va tests, con co the tach helper thanh module rieng. |
| Problem solving | 5 | Xu ly dependency, Mimo config, Unicode Windows, model fallback. |
| Evaluation mindset | 4 | Co report/failure analysis, nhung RAGAS that duoc gate bang env de tranh ton API trong test. |
