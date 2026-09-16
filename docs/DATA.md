# Nguồn dữ liệu

| File | Nguồn | Ngày cào | Quy mô | Ghi chú |
|---|---|---|---|---|
| `data/raw/cafeland_raw.csv` | nhadat.cafeland.vn (trang "Nhà đất bán tại TP.HCM") | 31/08–01/09/2026 | 9.883 × 9 | Crawler: `notebooks/00a_crawl_cafeland.ipynb` (xuất `cafeland.csv`, đổi tên khi đưa vào `data/raw/`) |
| `data/raw/bat_dong_san_raw.xls` | batdongsan.vn (`/ban-nha-dat/p{trang}`) | 31/08–01/09/2026 | 30.149 × 9 | Đuôi `.xls` nhưng là CSV UTF-8-sig. Crawler: `notebooks/00b_crawl_batdongsan.ipynb` |
| `data/raw/chotot_bds_dataset.xls` | API chotot.com (`limit=100`, nghỉ 1–3 s) | 01/09/2026 | 5.000 × 14 | Là CSV. **Chỉ khảo sát**, không đưa vào pipeline (lẫn tỉnh khác, tin cho thuê, cột `area` lỗi) |

robots.txt của ba trang được kiểm tra ngày 01/09/2026. Dữ liệu chỉ dùng cho mục đích học tập.

Cột trong hai file CafeLand/batdongsan: `Tieu_de, Gia_ban, Dien_tich, Dia_diem, Loai_hinh_BDS, Mo_ta_Dac_diem, Nguoi_dang_Chu_dau_tu, Ngay_dang, URL`.

Mô tả chi tiết từng biến sau làm sạch: `docs/Data_Dictionary_Nhom7_8.pdf`.
