# Ghi chú minh bạch về việc sử dụng AI

> Đề cương yêu cầu ghi chú minh bạch mọi phần được AI hỗ trợ, và **mỗi thành viên phải giải thích được mọi dòng code trong phần mình phụ trách** khi giảng viên vấn đáp.

**Người tổng hợp:** Trần Thị Ngọc Ánh

---

## Cách ghi

Mỗi lần dùng AI, thêm một dòng vào bảng dưới. Ghi **trung thực** — việc dùng AI không bị trừ điểm, nhưng giấu thì có.

| Ngày | Người dùng | Công cụ | Dùng để làm gì | Đã kiểm chứng thế nào |
|------|-----------|---------|----------------|----------------------|
| | | | | |

---

## Ví dụ cách ghi đúng

| Ngày | Người dùng | Công cụ | Dùng để làm gì | Đã kiểm chứng thế nào |
|------|-----------|---------|----------------|----------------------|
| 01/09 | Bá Công | Claude | Viết hàm crawl đa luồng với `ThreadPoolExecutor` | Chạy thử trên 50 trang, đối chiếu số tin thu được với số tin hiển thị trên web |
| 01/09 | Hữu Duy | ChatGPT | Giải thích cách hoạt động của `drop_duplicates` với nhiều cột | Đọc lại tài liệu pandas, tự viết ví dụ nhỏ kiểm tra |
| 02/09 | Trâm | Claude | Gợi ý các loại biểu đồ phù hợp cho EDA giá BĐS | Tự chọn lại 8 biểu đồ theo câu hỏi nghiên cứu của nhóm |

---

## Nguyên tắc bắt buộc

1. **Không copy-paste mù.** Đọc hiểu từng dòng trước khi đưa vào repo.
2. **Kiểm chứng mọi con số AI đưa ra.** AI có thể bịa số liệu.
3. **Tự viết lại comment bằng lời của mình.** Comment do AI viết thường chung chung.
4. **Nếu không giải thích được, không dùng.** Thà code đơn giản mà hiểu, còn hơn code phức tạp mà không biết nó làm gì.

---

## Câu hỏi vấn đáp có thể gặp

Mỗi thành viên nên chuẩn bị trả lời cho phần mình phụ trách:

### Phần dữ liệu (Bá Công, Hữu Duy)
- Vì sao chọn ngưỡng lọc outlier là IQR hệ số 3.0 mà không phải 1.5?
- Diện tích tối đa trong dữ liệu của em là bao nhiêu? Có hợp lý không?
- Làm sao em biết không còn tin trùng giữa 3 sàn?
- Vì sao phải tách tin bán và tin cho thuê?

### Phần EDA (Trâm, Ngọc Ánh)
- Vì sao biểu đồ phân bố giá dùng thang log?
- Từ biểu đồ này em rút ra được điều gì cho câu hỏi nghiên cứu?
- Vì sao dùng giá/m² thay vì giá tuyệt đối khi so sánh các quận?

### Phần mô hình (Anh Duy, Tường Vy, Bá Công)
- Vì sao biến mục tiêu là `log(giá)` mà không phải giá gốc?
- Vì sao giữ `nguon_du_lieu` làm biến trong mô hình?
- R² của em là bao nhiêu? Con số đó nghĩa là gì?
- Vì sao mô hình A tốt hơn mô hình B?
- RMSE 500 triệu nghĩa là gì với người mua nhà?
