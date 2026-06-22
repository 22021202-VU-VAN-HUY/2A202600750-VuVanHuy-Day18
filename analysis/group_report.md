# Group Report - Lab 18: Production RAG

**Nhom:** Ca nhan - Vu Van Huy  
**Ngay:** 22/06/2026

## Thanh vien & Phan cong

| Ten | Module | Hoan thanh | Tests pass |
|-----|--------|------------|------------|
| Vu Van Huy | M1: Chunking | Done | 13/13 |
| Vu Van Huy | M2: Hybrid Search | Done | 5/5 |
| Vu Van Huy | M3: Reranking | Done | 5/5 |
| Vu Van Huy | M4: Evaluation | Done | 4/4 |
| Vu Van Huy | M5: Enrichment | Done | 10/10 |

## Ket qua evaluation

| Metric | Naive | Production | Delta |
|--------|-------|------------|-------|
| Faithfulness | 0.4437 | 0.4635 | +0.0198 |
| Answer Relevancy | 0.5595 | 0.6065 | +0.0470 |
| Context Precision | 0.2800 | 0.3073 | +0.0273 |
| Context Recall | 0.3461 | 0.3734 | +0.0273 |

## Key Findings

1. **Biggest improvement:** Answer relevancy tang +0.0470 nho hybrid retrieval + reranking dua context gan cau hoi hon.
2. **Biggest challenge:** Cau hoi multi-hop can lay nhieu source, vi du `thu_viec.md` + `bang_luong_2024.md`.
3. **Surprise finding:** Versioned policy van de nham ban cu neu retrieval khong boost `hien hanh`, `thay the`, `v2024`.

## Presentation Notes (5 phut)

1. RAGAS scores: production cai thien ca 4 metric so voi naive baseline.
2. Biggest win: M2 + M3, vi RRF va rerank giup giam phu thuoc vao mot retriever.
3. Case study: cau hoi luong thu viec Junior fail do thieu context bang luong; can multi-hop query.
4. Next optimization: metadata effective_date/category, numeric boost, va query decomposition cho cau hoi tinh toan.
