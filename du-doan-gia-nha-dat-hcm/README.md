# Dự đoán giá nhà đất tại TP. Hồ Chí Minh

> **Môn học:** Lập trình Phân tích Dữ liệu (2101681) — Final Project
> **Nhóm 7, 8** — Nhóm trưởng: Nguyễn Thị Trâm
> **Thành viên:** Trần Thị Ngọc Ánh · Nguyễn Bá Công · Hà Trọng Hữu Duy · Lê Anh Duy · Văn Tường Vy

---

## 1. Giới thiệu đề tài

Dự án xây dựng mô hình **ước tính giá bán nhà đất tại TP.HCM** dựa trên đặc điểm tin đăng (diện tích, vị trí, loại hình bất động sản), nhằm đưa ra một **mức giá tham chiếu đáng tin** cho người bán, người mua và đội ngũ môi giới.

### Hai câu hỏi nghiên cứu

| # | Câu hỏi |
|---|---------|
| **1** | Những yếu tố nào trong một tin đăng giúp đưa ra một mức giá tham chiếu đáng tin cho một tin đăng mới? |
| **2** | Sau khi đã xem xét diện tích và loại nhà, khu vực nào đang bị định giá quá cao hoặc quá thấp? Chênh lệch giá giữa các khu vực xuất phát từ **vị trí** hay từ khác biệt về **quy mô và loại hình** nhà ở? |

Chi tiết bối cảnh, phân tích 5W1H và phân công công việc: xem [`reports/charter/`](reports/charter/).

---

## 2. Nguồn dữ liệu

| Nguồn | Số dòng thô | Sau làm sạch | Ghi chú |
|-------|-------------|--------------|---------|
| **CafeLand.vn** | 9.883 | 8.314 | Nguồn chính, 100% TP.HCM |
| **batdongsan.vn** | 30.149 | 27.783 | Quy mô lớn nhất, thiếu ~28% `Loai_hinh_BDS` |
| **chotot.com** | 5.000 | ~3.889 (TP.HCM) | Có cấp quận/phường; `area` & `price_per_m2` cần kiểm tra lại |

> ⚠️ **Cảnh báo chất lượng dữ liệu:** cột `area` của chotot chỉ khớp 0,1% với diện tích ghi trong tiêu đề và bị chặn ở 130m². Cột `price_per_m2` kế thừa lỗi này. Xem [`docs/DATA.md`](docs/DATA.md) trước khi dùng.

Mô tả chi tiết từng nguồn, schema và bảng ánh xạ: [`docs/DATA.md`](docs/DATA.md)

---

## 3. Cấu trúc thư mục

```
du-doan-gia-nha-dat-hcm/
├── data/
│   ├── raw/              # Dữ liệu thô từ crawler (KHÔNG chỉnh sửa)
│   ├── interim/          # Dữ liệu trung gian đang xử lý
│   ├── processed/        # Dữ liệu sạch, sẵn sàng cho mô hình
│   └── external/         # Dữ liệu ngoài (danh mục quận/phường...)
├── notebooks/            # Jupyter notebook theo 4 bài tập
│   ├── 01_thu_thap_du_lieu.ipynb
│   ├── 02_lam_sach_du_lieu.ipynb
│   ├── 03_phan_tich_kham_pha_eda.ipynb
│   └── 04_xay_dung_mo_hinh.ipynb
├── src/                  # Mã nguồn tái sử dụng
│   ├── data/             # Crawl & làm sạch
│   ├── features/         # Tạo đặc trưng
│   ├── models/           # Huấn luyện & đánh giá
│   └── visualization/    # Vẽ biểu đồ
├── reports/
│   ├── figures/          # Biểu đồ xuất ra
│   └── charter/          # Project Charter, slide
├── docs/                 # Tài liệu: dữ liệu, quy ước, đóng góp
├── tests/                # Unit test
├── config/               # File cấu hình tham số
├── requirements.txt
└── README.md
```

---

## 4. Cài đặt

### Yêu cầu
- Python **3.9** trở lên
- Git

### Các bước

```bash
# 1. Clone repo
git clone https://github.com/<TEN-TAI-KHOAN>/du-doan-gia-nha-dat-hcm.git
cd du-doan-gia-nha-dat-hcm

# 2. Tạo môi trường ảo
python -m venv venv

# Kích hoạt — Windows:
venv\Scripts\activate
# Kích hoạt — macOS/Linux:
source venv/bin/activate

# 3. Cài thư viện
pip install -r requirements.txt

# 4. Chạy Jupyter
jupyter notebook
```

### Tải dữ liệu

File dữ liệu **không được lưu trên Git** (quá lớn). Xem hướng dẫn tải tại [`docs/DATA.md`](docs/DATA.md), sau đó đặt file vào `data/raw/`.

---

## 5. Cách tái lập kết quả

Chạy lần lượt 4 notebook theo đúng thứ tự:

| Bước | Notebook | Đầu vào | Đầu ra |
|------|----------|---------|--------|
| 1 | `01_thu_thap_du_lieu.ipynb` | — | `data/raw/*.csv` |
| 2 | `02_lam_sach_du_lieu.ipynb` | `data/raw/` | `data/processed/du_lieu_sach.csv` |
| 3 | `03_phan_tich_kham_pha_eda.ipynb` | `data/processed/` | `reports/figures/*.png` |
| 4 | `04_xay_dung_mo_hinh.ipynb` | `data/processed/` | Kết quả mô hình, bảng so sánh |

Hoặc chạy toàn bộ pipeline bằng dòng lệnh:

```bash
python src/data/lam_sach_du_lieu.py      # Làm sạch + hợp nhất
python src/models/huan_luyen_mo_hinh.py  # Huấn luyện & đánh giá
```

---

## 6. Tiến độ

- [x] **Bài tập 1 — Tuần 4:** Project Charter, câu hỏi nghiên cứu
- [x] Thu thập dữ liệu từ 3 nguồn
- [ ] **Bài tập 2 — Tuần 7:** Làm sạch, hợp nhất dữ liệu
- [ ] **Bài tập 3 — Tuần 8:** EDA + ≥8 biểu đồ + 5-7 insight
- [ ] **Bài tập 4 — Tuần 9:** Xây mô hình, đánh giá, báo cáo cuối

---

## 7. Phân công

| Thành viên | Vai trò chính |
|------------|---------------|
| Nguyễn Thị Trâm | Nhóm trưởng · Business Question · EDA · GitHub repo |
| Trần Thị Ngọc Ánh | Business Question · EDA · Đánh giá mô hình · Ghi chú AI |
| Nguyễn Bá Công | Thu thập & làm sạch dữ liệu · Xây mô hình |
| Hà Trọng Hữu Duy | Thu thập & làm sạch dữ liệu · Đánh giá mô hình |
| Lê Anh Duy | Khung báo cáo · Insight · Xây mô hình |
| Văn Tường Vy | Khung báo cáo · Insight · Xây mô hình |

---

## 8. Ghi chú về việc sử dụng AI

Theo yêu cầu minh bạch của đề cương, mọi phần được AI hỗ trợ đều được ghi chú tại [`docs/GHI_CHU_AI.md`](docs/GHI_CHU_AI.md). Mỗi thành viên chịu trách nhiệm giải thích được mọi dòng code trong phần mình phụ trách.

---

## 9. Công nghệ sử dụng

`Python` · `pandas` · `numpy` · `scikit-learn` · `matplotlib` · `seaborn` · `BeautifulSoup` · `requests` · `Jupyter`
