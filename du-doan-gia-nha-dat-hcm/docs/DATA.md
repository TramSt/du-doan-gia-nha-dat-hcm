# Mô tả dữ liệu

## 1. Cách lấy dữ liệu

File dữ liệu **không lưu trên GitHub** vì dung lượng lớn. Tải từ link nội bộ nhóm (Google Drive) và đặt vào `data/raw/`:

```
data/raw/
├── cafeland_raw.csv
├── bat_dong_san_raw.xlsb
└── chotot_bds_dataset.csv
```

> 📌 **Người phụ trách:** Nguyễn Bá Công, Hà Trọng Hữu Duy

---

## 2. Ba nguồn dữ liệu

### 2.1. CafeLand.vn — nguồn chính

| Thuộc tính | Giá trị |
|---|---|
| Số dòng thô | 9.883 |
| Sau làm sạch | 8.314 |
| Số cột | 9 |
| Phạm vi | 100% TP.HCM |
| Đơn vị giá | **Triệu VNĐ** |

**Các cột:** `Tieu_de`, `Gia_ban`, `Dien_tich`, `Dia_diem`, `Loai_hinh_BDS`, `Mo_ta_Dac_diem`, `Nguoi_dang_Chu_dau_tu`, `Ngay_dang`, `URL`

**Vấn đề cần xử lý:**
- Ngoại lai: giá tối đa ~970 tỷ, diện tích tối đa ~18 triệu m²
- Nhãn loại hình chưa chuẩn hóa: `"Nhà riêng"` và `"Bán nhà riêng"` là hai nhãn riêng biệt

---

### 2.2. batdongsan.vn — quy mô lớn nhất

| Thuộc tính | Giá trị |
|---|---|
| Số dòng thô | 30.149 |
| Sau lọc TP.HCM | 27.783 |
| Số cột | 9 (giống CafeLand) |
| Định dạng | `.xlsb` — cần `pyxlsb` |
| Đơn vị giá | **Triệu VNĐ** |

**Vấn đề cần xử lý:**
- `Loai_hinh_BDS` thiếu **7.847 dòng (~28%)**
- `Gia_ban` thiếu 13 dòng
- Ngoại lai: giá tối đa ~999 tỷ, diện tích tối đa 720.000 m²

---

### 2.3. chotot.com — có cấp quận/phường

| Thuộc tính | Giá trị |
|---|---|
| Số dòng | 5.000 |
| Thuộc TP.HCM | 3.889 (77,8%) |
| Số cột | 14 |
| Đơn vị giá | **VNĐ nguyên** ⚠️ |

**Các cột:** `ad_id`, `title`, `price`, `area`, `price_per_m2`, `region_name`, `area_name`, `ward_name`, `street_name`, `property_type`, `rooms`, `direction`, `created_at`, `url`

**Ưu điểm:**
- Địa lý tách sẵn 4 cấp: tỉnh/thành → quận/huyện → phường/xã → đường
- Phủ 22 quận/huyện và 165 phường/xã trong TP.HCM
- `property_type` đã chuẩn hóa thành 5 nhóm
- Không có bản ghi trùng lặp

#### ⚠️ Ba lỗi nghiêm trọng của nguồn này

**Lỗi 1 — Cột `area` không dùng được**

Đối chiếu diện tích trong tiêu đề với cột `area` ở 894 tin có ghi rõ số m²: **chỉ khớp 1 tin (0,1%)**. Cột này chỉ có 77 giá trị khác nhau và bị chặn cứng ở 130m².

| Tiêu đề tin đăng | Cột `area` | Thực tế |
|---|---|---|
| BÁN ĐẤT LONG TRƯỜNG – THỦ ĐỨC \| **100M²** | 119 | 100 |
| Hàng nóng **212m2** (6,5x32) xả lỗ giá 620tr | 116 | 212 |
| CHO THUÊ MẶT TIỀN CAO THẮNG... DTSD **250M2** | 98 | 250 |

→ **Cách xử lý:** code trong `src/data/lam_sach_du_lieu.py` **không dùng** cột `area`, mà trích lại diện tích từ tiêu đề bằng hàm `trich_dien_tich_tu_tieu_de()`.

→ Cột `price_per_m2` cũng bị loại vì được tính bằng `price / area` (đã kiểm chứng khớp 5.000/5.000 dòng), nên kế thừa toàn bộ lỗi của `area`.

**Lỗi 2 — Trộn lẫn tin bán và tin cho thuê**

| Nhóm | Số tin | Giá trung vị |
|---|---|---|
| Tin cho thuê | 1.813 | 10.000.000 đ |
| Tin bán | 997 | 4.621.017.628 đ |
| Không rõ | 2.237 (44,7%) | — |

Chênh lệch ~460 lần. → **Cách xử lý:** hàm `phan_loai_giao_dich()` kết hợp từ khóa tiêu đề và ngưỡng giá.

**Lỗi 3 — Hai cột thiếu hoàn toàn**

`rooms` và `direction` thiếu **100%** (5.000/5.000). → Loại bỏ.

**Hạn chế khác:** toàn bộ 5.000 tin đăng trong **cùng ngày 24/08/2026**, khoảng chưa đầy 12 giờ — lát cắt thời gian rất hẹp.

---

## 3. Bảng ánh xạ về schema chung

Cả 3 nguồn được đưa về đúng bộ cột sau (xem `SCHEMA_CHUNG` trong code):

| Cột chung | CafeLand | batdongsan.vn | chotot.com |
|---|---|---|---|
| `tieu_de` | `Tieu_de` | `Tieu_de` | `title` |
| `gia_ban_trieu` | `Gia_ban` | `Gia_ban` | `price` ÷ 1.000.000 |
| `dien_tich_m2` | `Dien_tich` | `Dien_tich` | **trích từ `title`** |
| `tinh_thanh` | `Dia_diem` | `Dia_diem` | `region_name` |
| `quan_huyen` | — | — | `area_name` |
| `phuong_xa` | — | — | `ward_name` |
| `loai_hinh` | `Loai_hinh_BDS` | `Loai_hinh_BDS` | `property_type` |
| `nguon_du_lieu` | `"cafeland"` | `"batdongsan"` | `"chotot"` |
| `url` | `URL` | `URL` | `url` |

---

## 4. Quy trình làm sạch

| Bước | Việc làm | Lý do |
|---|---|---|
| 1 | Đọc & ánh xạ schema | 3 nguồn khác cấu trúc |
| 2 | Tách bán/thuê | Hai bài toán khác nhau, giá chênh ~460 lần |
| 3 | Lọc TP.HCM | Đúng phạm vi đề tài |
| 4 | Chuẩn hóa nhãn loại hình | Tránh mô hình coi cùng loại là khác nhau |
| 5 | Loại dòng thiếu giá/diện tích | Hai biến cốt lõi |
| 6 | Lọc ngoại lai | Ngưỡng cứng + IQR (hệ số 3.0) |
| 7 | Loại trùng chéo nguồn | **Quan trọng nhất về mặt thống kê** |
| 8 | Tạo biến phái sinh | `gia_moi_m2_trieu` |

### Vì sao bước 7 quan trọng nhất?

Mỗi sàn có URL riêng nên **không dùng URL làm khóa loại trùng chéo nguồn được**. Nếu cùng một căn nhà đăng trên cả 3 sàn mà không loại, nó bị đếm 3 lần → vi phạm **giả định các quan sát độc lập** của hồi quy → sai số chuẩn bị co lại → kiểm định thống kê cho kết quả sai.

**Khóa so khớp đang dùng:** `(quận/huyện + loại hình + diện tích làm tròn + giá nhóm 50 triệu)`

---

## 5. Biến trong dữ liệu sạch

| Biến | Kiểu | Mô tả |
|---|---|---|
| `tieu_de` | text | Tiêu đề tin đăng |
| `gia_ban_trieu` | float | **Biến mục tiêu** — giá bán (triệu VNĐ) |
| `dien_tich_m2` | float | Diện tích (m²) |
| `tinh_thanh` | text | Tỉnh/thành |
| `quan_huyen` | text | Quận/huyện (chỉ chotot có) |
| `phuong_xa` | text | Phường/xã (chỉ chotot có) |
| `loai_hinh` | text | Loại hình BĐS đã chuẩn hóa |
| `nguon_du_lieu` | text | **Biến kiểm soát** — cafeland/batdongsan/chotot |
| `gia_moi_m2_trieu` | float | Giá mỗi m² (biến phái sinh) |
| `url` | text | Link gốc để truy vết |

---

## 6. Lưu ý về mặt phương pháp luận

Vì gộp dữ liệu từ 3 nguồn có đặc thù khác nhau (mỗi sàn hút một phân khúc người đăng), **biến `nguon_du_lieu` phải được giữ làm biến kiểm soát trong mô hình**. Đây là cách xử lý chuẩn khi gộp dữ liệu đa nguồn.

Biểu đồ 7 (`bd07_so_sanh_nguon`) dùng để kiểm tra xem 3 nguồn có mặt bằng giá khác nhau rõ rệt hay không.

**Hạn chế cần nêu trong báo cáo:** dữ liệu là **giá niêm yết**, không phải giá giao dịch thực tế. Giá thực tế thường thấp hơn do thương lượng.
