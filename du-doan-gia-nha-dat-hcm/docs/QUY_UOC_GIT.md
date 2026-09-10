# Quy ước làm việc với Git

> Tài liệu này giúp 6 thành viên làm việc song song mà không đè code lên nhau.

---

## 1. Quy tắc vàng

| ❌ Không làm | ✅ Nên làm |
|---|---|
| Push thẳng lên `main` | Tạo nhánh riêng rồi mở Pull Request |
| Commit file dữ liệu lớn | Để `.gitignore` lo, chia sẻ qua Drive |
| Commit `.ipynb_checkpoints` | Đã có trong `.gitignore` |
| Commit message kiểu "update", "fix" | Ghi rõ đã làm gì |
| Sửa code người khác không báo | Báo trong nhóm chat trước |

---

## 2. Cấu trúc nhánh

```
main                    ← Nhánh chính, luôn chạy được. Chỉ merge qua PR.
├── data/lam-sach       ← Bá Công, Hữu Duy
├── eda/bieu-do         ← Trâm, Ngọc Ánh
├── model/hoi-quy       ← Anh Duy, Tường Vy
└── docs/bao-cao        ← Tường Vy, Anh Duy
```

### Đặt tên nhánh

```
<loại>/<mô-tả-ngắn>
```

| Loại | Dùng khi |
|---|---|
| `data/` | Thu thập, làm sạch dữ liệu |
| `eda/` | Phân tích khám phá, biểu đồ |
| `model/` | Xây dựng mô hình |
| `docs/` | Tài liệu, báo cáo |
| `fix/` | Sửa lỗi |

**Ví dụ:** `data/tach-ban-thue`, `eda/bieu-do-quan-huyen`, `fix/loi-doc-file-xlsb`

---

## 3. Quy trình làm việc hằng ngày

```bash
# 1. Cập nhật main mới nhất trước khi bắt đầu
git checkout main
git pull origin main

# 2. Tạo nhánh mới cho việc của mình
git checkout -b eda/bieu-do-quan-huyen

# 3. Làm việc... rồi kiểm tra file nào đã đổi
git status

# 4. Thêm file và commit
git add src/visualization/ve_bieu_do.py
git commit -m "them: bieu do gia trung vi theo quan huyen"

# 5. Đẩy nhánh lên GitHub
git push origin eda/bieu-do-quan-huyen

# 6. Vào GitHub, mở Pull Request để nhóm trưởng review
```

---

## 4. Viết commit message

**Cú pháp:**
```
<loại>: <mô tả ngắn không dấu, chữ thường>
```

| Loại | Ý nghĩa | Ví dụ |
|---|---|---|
| `them` | Thêm tính năng mới | `them: ham trich dien tich tu tieu de` |
| `sua` | Sửa lỗi | `sua: loi doc file xlsb thieu engine` |
| `capnhat` | Cập nhật code cũ | `capnhat: nguong loc outlier tu 1.5 len 3.0 IQR` |
| `xoa` | Xóa code/file | `xoa: bo cot rooms va direction thieu 100%` |
| `tailieu` | Sửa tài liệu | `tailieu: bo sung mo ta loi cot area cua chotot` |

**Nguyên tắc:** đọc commit message phải hiểu được đã làm gì mà không cần mở code.

---

## 5. Xử lý xung đột (conflict)

Xung đột xảy ra khi hai người sửa cùng một chỗ. Đừng hoảng:

```bash
# 1. Lấy main mới nhất về nhánh của mình
git checkout eda/bieu-do-quan-huyen
git pull origin main

# 2. Git báo conflict ở file nào, mở file đó ra sẽ thấy:
#    <<<<<<< HEAD
#    code của mình
#    =======
#    code của người khác
#    >>>>>>> main

# 3. Sửa tay: giữ phần đúng, xóa các dấu <<<, ===, >>>

# 4. Đánh dấu đã giải quyết xong
git add <file-bi-conflict>
git commit -m "sua: giai quyet conflict voi main"
git push origin eda/bieu-do-quan-huyen
```

> 💡 **Mẹo tránh conflict:** mỗi người làm ở file khác nhau, `pull` main thường xuyên (ít nhất mỗi ngày một lần).

---

## 6. Quy ước với Jupyter Notebook

Notebook rất dễ gây conflict vì lưu cả output. Trước khi commit:

1. Vào menu **Kernel → Restart & Clear Output**
2. Lưu file
3. Rồi mới `git add`

Như vậy chỉ commit phần code, không commit kết quả chạy.

---

## 7. Checklist trước khi mở Pull Request

- [ ] Code chạy được từ đầu đến cuối không lỗi
- [ ] Đã xóa output notebook (Restart & Clear Output)
- [ ] Không commit file dữ liệu (kiểm tra bằng `git status`)
- [ ] Commit message rõ ràng
- [ ] Đã `pull` main mới nhất và giải quyết conflict
- [ ] Có comment giải thích cho đoạn code phức tạp

---

## 8. Các lệnh hay dùng

```bash
git status                    # Xem file nào đã đổi
git log --oneline -10         # Xem 10 commit gần nhất
git diff                      # Xem chi tiết đã sửa gì
git branch                    # Xem đang ở nhánh nào
git checkout main             # Chuyển về nhánh main

git restore <file>            # Hoàn tác sửa đổi chưa commit
git reset --soft HEAD~1       # Hoàn tác commit cuối, giữ lại code
```

---

## 9. Nếu lỡ commit nhầm file dữ liệu lớn

```bash
# Gỡ file khỏi git nhưng vẫn giữ trên máy
git rm --cached data/raw/file_lon.csv
git commit -m "xoa: bo file du lieu khoi git"
git push
```

Nếu đã push lên GitHub từ lâu, báo nhóm trưởng để xử lý bằng `git filter-branch`.
