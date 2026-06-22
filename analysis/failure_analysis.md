# Phân Tích Lỗi - Lab 18: Production RAG

**Sinh viên:** Vũ Văn Huy  
**Ngày chạy pipeline:** 22/06/2026  
**Pipeline:** M1 hierarchical chunking -> M5 contextual enrichment -> M2 BM25 + dense/hash fallback -> M3 reranking -> M4 evaluation.

## Điểm Evaluation

| Metric | Naive Baseline | Production | Chênh lệch |
|--------|----------------|------------|------------|
| Faithfulness | 0.4437 | 0.4635 | +0.0198 |
| Answer Relevancy | 0.5595 | 0.6065 | +0.0470 |
| Context Precision | 0.2800 | 0.3073 | +0.0273 |
| Context Recall | 0.3461 | 0.3734 | +0.0273 |

Pipeline production cải thiện cả bốn chỉ số. Tuy vậy, điểm tuyệt đối vẫn chưa cao vì test set có nhiều câu hỏi multi-hop, câu hỏi cần tính toán, và câu hỏi phải phân biệt chính sách cũ với chính sách hiện hành.

## Bottom-5 Failures

### #1. Mua thiết bị trị giá 55 triệu cần ai phê duyệt?

- **Câu hỏi:** Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt?
- **Đáp án đúng:** Đơn hàng trên 50.000.000 VND cần Tổng Giám đốc/CEO phê duyệt.
- **Câu trả lời của pipeline:** Suy ra Trưởng phòng + Kế toán trưởng, chưa lấy đúng ngưỡng CEO.
- **Metric thấp nhất:** `context_precision = 0.1793`
- **Error tree:** Output sai -> Context có một phần liên quan nhưng thiếu bảng thẩm quyền đầy đủ -> Query cần xử lý ngưỡng số tiền.
- **Nguyên nhân gốc:** Retrieval lấy các chunk gần nghĩa về quy trình mua sắm/tạm ứng nhưng không ưu tiên chunk chứa ngưỡng `>50.000.000`.
- **Hướng sửa:** Thêm metadata `procurement`, boost token số tiền, và mở rộng parent chunk khi gặp bảng thẩm quyền phê duyệt.

### #2. Lương thử việc Junior mức cao nhất là bao nhiêu?

- **Câu hỏi:** Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu?
- **Đáp án đúng:** Junior cao nhất là 20.000.000 VND/tháng; lương thử việc bằng 85%, tức 17.000.000 VND/tháng.
- **Câu trả lời của pipeline:** Không tìm thấy mức lương Junior cụ thể.
- **Metric thấp nhất:** `context_recall = 0.1654`
- **Error tree:** Output sai -> Context thiếu bảng lương -> Query multi-hop chưa lấy cả `thu_viec.md` và `bang_luong_2024.md`.
- **Nguyên nhân gốc:** Câu hỏi cần hợp nhất hai tài liệu: quy tắc 85% trong chính sách thử việc và khung lương Junior trong bảng lương.
- **Hướng sửa:** Tách truy vấn thành `lương thử việc 85%` và `Junior P1 P2 20.000.000`, sau đó merge context từ nhiều source.

### #3. Mua laptop 30 triệu cần ai phê duyệt và cần gì từ CNTT?

- **Câu hỏi:** Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới, ai phê duyệt và cần gì từ phòng CNTT?
- **Đáp án đúng:** Director phê duyệt, cần xác nhận cấu hình kỹ thuật từ phòng CNTT, và cần ít nhất 3 báo giá.
- **Câu trả lời của pipeline:** Không tìm thấy quy trình mua laptop/CNTT.
- **Metric thấp nhất:** `context_recall = 0.2140`
- **Error tree:** Output sai -> Context không đúng -> Query gom hai ý procurement và IT requirement.
- **Nguyên nhân gốc:** Retrieval bị hút sang đào tạo/nghỉ phép thay vì chính sách mua sắm; câu hỏi dài làm loãng token quan trọng.
- **Hướng sửa:** Query rewrite thành hai subquery: `laptop 30 triệu phê duyệt mua sắm` và `thiết bị CNTT xác nhận cấu hình`.

### #4. Nghỉ phép không lương 20 ngày cần ai phê duyệt?

- **Câu hỏi:** Nghỉ phép không lương 20 ngày cần ai phê duyệt?
- **Đáp án đúng:** Nghỉ 16-30 ngày cần CEO phê duyệt; nghỉ trên 14 ngày thì nhân viên tự đóng phần bảo hiểm của mình.
- **Câu trả lời của pipeline:** Không tìm thấy người phê duyệt cụ thể.
- **Metric thấp nhất:** `context_recall = 0.2229`
- **Error tree:** Output sai -> Context có policy nhưng chưa làm nổi bật ngưỡng 16-30 ngày -> LLM không đủ tự tin kết luận.
- **Nguyên nhân gốc:** Child chunk chưa giữ trọn cụm quy tắc phê duyệt theo số ngày.
- **Hướng sửa:** Dùng structure-aware chunking riêng cho section “Quy trình phê duyệt”, giữ các dòng 1-5, 6-15, 16-30 trong cùng một chunk.

### #5. Bao lâu phải đổi mật khẩu một lần?

- **Câu hỏi:** Bao lâu phải đổi mật khẩu một lần?
- **Đáp án đúng:** Chính sách hiện hành v2.0 là 120 ngày; chính sách cũ v1.0 là 90 ngày và đã bị thay thế.
- **Câu trả lời của pipeline:** Trả lời đúng phần 120 ngày nhưng thiếu so sánh với chính sách cũ.
- **Metric thấp nhất:** `context_precision = 0.2056`
- **Error tree:** Output gần đúng -> Context có nhiều chunk mật khẩu liên quan -> Prompt chưa ép nêu rõ version replacement.
- **Nguyên nhân gốc:** LLM rút gọn câu trả lời và bỏ chi tiết chính sách cũ/đã thay thế trong ground truth.
- **Hướng sửa:** Thêm prompt rule: với câu hỏi versioned, phải nêu `current policy`, `superseded policy`, và ngày hiệu lực nếu context có.

## Case Study

**Câu hỏi chọn phân tích:** Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu?

1. **Output đúng chưa?** Chưa. Pipeline trả lời “không tìm thấy”.
2. **Context đúng chưa?** Chưa đủ. Context có `thu_viec.md` nhưng thiếu `bang_luong_2024.md`.
3. **Query rewrite ổn chưa?** Chưa. Câu hỏi cần tách thành phép tính `85% x max Junior salary`.
4. **Nên sửa ở bước nào?** Retrieval/query planning, trước khi rerank.

## Nếu Có Thêm Thời Gian

- Thêm multi-hop retriever để lấy tối thiểu hai source khác nhau khi câu hỏi có phép tính hoặc so sánh.
- Boost numeric/currency tokens trong BM25.
- Thêm metadata `category`, `effective_date`, `status` để lọc chính sách hiện hành.
- Cập nhật prompt synthesis để bắt buộc trình bày công thức tính toán.
