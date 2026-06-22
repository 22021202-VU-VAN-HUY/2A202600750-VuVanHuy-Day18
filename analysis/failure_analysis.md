# Failure Analysis - Lab 18: Production RAG

**Ca nhan:** Vu Van Huy  
**Ngay chay:** 22/06/2026  
**Pipeline:** M1 hierarchical chunking -> M5 contextual enrichment fallback -> M2 BM25 + dense/hash fallback -> M3 reranking -> M4 evaluation.

## RAGAS Scores

| Metric | Naive Baseline | Production | Delta |
|--------|---------------|------------|-------|
| Faithfulness | 0.4437 | 0.4635 | +0.0198 |
| Answer Relevancy | 0.5595 | 0.6065 | +0.0470 |
| Context Precision | 0.2800 | 0.3073 | +0.0273 |
| Context Recall | 0.3461 | 0.3734 | +0.0273 |

Production pipeline cai thien ca 4 metric. Muc tang lon nhat la answer relevancy, nho hybrid retrieval + reranking dua context dung hon vao prompt. Diem van thap chu yeu do cac cau hoi multi-hop/versioned can lay dong thoi nhieu tai lieu va so sanh nguong.

## Bottom-5 Failures

### #1
- **Question:** Muon mua thiet bi tri gia 55 trieu can ai phe duyet?
- **Expected:** Don hang tren 50.000.000 VND can Tong Giam doc (CEO) phe duyet.
- **Got:** Tra loi suy ra Truong phong + Ke toan truong, khong lay dung nguong CEO.
- **Worst metric:** context_precision = 0.1793
- **Error Tree:** Output sai -> Context co mot phan lien quan nhung thieu bang tham quyen day du -> Query can numeric threshold routing.
- **Root cause:** Retrieval lay cac chunk quy trinh mua sam/tam ung gan nghia, nhung khong uu tien chunk chua nguong `>50.000.000`.
- **Suggested fix:** Them metadata category `procurement`, boost numeric tokens, va parent expansion cho bang tham quyen phe duyet.

### #2
- **Question:** Luong thu viec cua nhan vien Junior muc cao nhat la bao nhieu?
- **Expected:** Junior cao nhat 20.000.000 VND/thang; 85% la 17.000.000 VND/thang.
- **Got:** Khong tim thay muc luong Junior cu the.
- **Worst metric:** context_recall = 0.1654
- **Error Tree:** Output sai -> Context thieu bang luong -> Query multi-hop chua lay ca `thu_viec.md` va `bang_luong_2024.md`.
- **Root cause:** Cau hoi can hop nhat hai tai lieu: quy tac 85% trong thu viec va khung luong Junior trong bang luong.
- **Suggested fix:** Multi-query decomposition: `luong thu viec 85%` + `Junior P1 P2 20.000.000`; sau do merge context theo source khac nhau.

### #3
- **Question:** Can mua laptop 30 trieu cho nhan vien moi, ai phe duyet va can gi tu CNTT?
- **Expected:** Director phe duyet, can xac nhan cau hinh ky thuat tu phong CNTT, va 3 bao gia.
- **Got:** Khong tim thay quy trinh mua laptop/CNTT.
- **Worst metric:** context_recall = 0.2140
- **Error Tree:** Output sai -> Context khong dung -> Query gom hai y procurement + IT requirement.
- **Root cause:** Retrieval bi hut sang dao tao/nghi phep thay vi mua sam; query dai lam loang token quan trong.
- **Suggested fix:** Query rewrite tach thanh 2 subquery: `laptop 30 trieu phe duyet mua sam` va `thiet bi CNTT xac nhan cau hinh`.

### #4
- **Question:** Nghi phep khong luong 20 ngay can ai phe duyet?
- **Expected:** Nghi 16-30 ngay can CEO phe duyet; nghi tren 14 ngay tu dong phan bao hiem cua minh.
- **Got:** Khong tim thay nguoi phe duyet cu the.
- **Worst metric:** context_recall = 0.2229
- **Error Tree:** Output sai -> Context co policy nhung thieu/khong noi bat nguong 16-30 ngay -> LLM khong du tu tin ket luan.
- **Root cause:** Child chunk khong giu tron bang/chuoi quy tac phe duyet theo so ngay.
- **Suggested fix:** Structure-aware chunking rieng cho section `Quy trinh phe duyet`, giu nguyen cac dong 1-5, 6-15, 16-30 trong cung mot chunk.

### #5
- **Question:** Bao lau phai doi mat khau mot lan?
- **Expected:** Hien hanh v2.0 la 120 ngay; v1.0 cu la 90 ngay da bi thay the.
- **Got:** Tra loi dung phan 120 ngay, nhung thieu so sanh voi version cu.
- **Worst metric:** context_precision = 0.2056
- **Error Tree:** Output gan dung -> Context co nhieu chunk mat khau lien quan -> Prompt chua ep noi ro version replacement.
- **Root cause:** LLM rut gon cau tra loi va bo chi tiet policy cu/bi thay the trong ground truth.
- **Suggested fix:** Them prompt rule: voi cau hoi versioned, phai neu `current policy`, `superseded policy`, va ngay hieu luc neu context co.

## Case Study

**Question chon phan tich:** Luong thu viec cua nhan vien Junior muc cao nhat la bao nhieu?

**Error Tree walkthrough:**
1. Output dung? -> Khong, answer noi khong tim thay.
2. Context dung? -> Chi co `thu_viec.md`, thieu `bang_luong_2024.md`.
3. Query rewrite OK? -> Chua. Query can tach thanh phep tinh `85% x max Junior salary`.
4. Fix o buoc: Retrieval/query planning, truoc khi rerank.

**Neu co them 1 gio, se optimize:**
- Them multi-hop retriever lay toi thieu 2 source khac nhau khi cau hoi co phep tinh/so sanh.
- Boost numeric + currency tokens trong BM25.
- Them metadata `category` va `effective_date` de loc policy hien hanh.
- Them prompt answer synthesis bat buoc trich cong thuc tinh toan.
