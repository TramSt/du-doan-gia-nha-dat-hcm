# Dự đoán giá nhà đất TP.HCM – Case study CafeLand.vn

Đồ án môn **Lập trình Phân tích Dữ liệu (2101681)** – Liên minh Nhóm 7 & 8.

**Câu hỏi chính:** Những yếu tố nào trong một tin đăng giúp đưa ra mức giá tham chiếu đáng tin cho tin đăng mới? (hồi quy, biến mục tiêu `gia_ban`, triệu VNĐ)
**Câu hỏi phụ:** Sau khi tính diện tích và loại nhà, quận nào đang bị định giá cao hoặc thấp?

## Cấu trúc thư mục

```
├── config/config.yaml          # đường dẫn, ngưỡng lọc, nguồn sử dụng
├── data/
│   ├── raw/                    # dữ liệu cào gốc (không sửa tay)
│   ├── interim/df_raw.csv      # làm sạch lần 1 – 11.888 × 10 (bản đã chốt)
│   ├── interim/loai_ape_lan_chay_goc.csv  # 227 URL bị loại ở bước APE
│   └── processed/df_clean.csv  # làm sạch lần 2 – 7.436 × 27
├── docs/
│   ├── DATA.md                 # nguồn và cách thu thập
│   └── Data_Dictionary_Nhom7_8.pdf
├── notebooks/
│   ├── 00a_crawl_cafeland.ipynb
│   ├── 00b_crawl_batdongsan.ipynb
│   ├── 01_thu_thap_du_lieu.ipynb     # mô tả nguồn, chất lượng dữ liệu thô
│   ├── 02_lam_sach_du_lieu.ipynb     # raw → df_raw
│   ├── 02_lam_sach_du_lieu_2.ipynb   # df_raw → df_clean (+ bảng kiểm toán)
│   ├── 03_phan_tich_kham_pha_eda.ipynb   # Bài tập 3 (đang làm)
│   └── 04_xay_dung_mo_hinh.ipynb         # Bài tập 4 (đang làm)
├── reports/figures/
└── src/
    ├── utils.py
    ├── data/lam_sach_du_lieu.py      # tao_df_raw()
    ├── features/tao_dac_trung.py     # tao_df_clean()
    ├── visualization/ve_bieu_do.py
    └── models/huan_luyen_mo_hinh.py
```

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Yêu cầu Python 3.11+ và pandas 2.2.x.

## Tái lập kết quả Bài tập 2

Chạy từ **thư mục gốc** dự án:

```bash
python -m src.data.lam_sach_du_lieu     # → data/interim/df_raw_chay_lai.csv (11.888 dòng, để đối chiếu)
python -m src.features.tao_dac_trung    # → data/processed/df_clean.csv (7.436 dòng)
```

Hoặc mở và chạy lần lượt `notebooks/01` → `02` → `02_..._2` (Run All). Notebook tự tìm thư mục gốc, không cần sửa đường dẫn.

`df_raw.csv` là bản nhóm đã chốt, dùng cho Project Charter. Chạy lại từ dữ liệu thô cho cùng 11.888 dòng và cùng phân bố nguồn (99,23% URL trùng) nên được ghi ra file riêng, không ghi đè.

Không cần chạy lại crawler: dữ liệu thô đã có trong `data/raw/` (xem `docs/DATA.md`).

## Tóm tắt xử lý

| Bước | Dòng còn lại |
|---|---|
| Gộp CafeLand + batdongsan | 40.032 |
| Bỏ tin thuê, ngoài TP.HCM, thiếu giá/diện tích, ngoại lai thô, trùng chéo nguồn | 29.532 |
| Bỏ tin không trích được quận → **df_raw** | 11.888 |
| Bỏ tin thiếu loại hình (2.809), trùng 4 cột (989), ngoại lai đơn giá (420), diện tích ngoài 15–500 m² (7) | 7.663 |
| Bỏ tin có sai số dự đoán thử APE > 50% (227) → **df_clean** | 7.436 |

> ⚠️ 227 tin ở bước cuối đều thuộc phần test của `train_test_split(random_state=42)`. Bài tập 4 không dùng lại đúng phép chia này để báo cáo điểm; đánh giá bằng cross-validation và báo cáo thêm trên 7.663 dòng.

Chi tiết từng bước và lý do: `docs/Data_Dictionary_Nhom7_8.pdf`, mục 4.1.

## Phân công

| Thành viên | MSSV | Phụ trách chính |
|---|---|---|
| Trần Thị Ngọc Ánh | 24639511 | 5W1H, EDA, đánh giá mô hình, slide, ghi chú AI |
| Nguyễn Bá Công | 24689091 | Cào batdongsan/chotot, làm sạch, mô hình, slide |
| Hà Trọng Hữu Duy | 24702061 | Cào CafeLand, pipeline làm sạch, so sánh mô hình, slide |
| Lê Anh Duy | 24681951 | Khung báo cáo, insight, mô hình |
| Nguyễn Thị Trâm | 24689661 | Project Charter, GitHub, EDA, README |
| Văn Tường Vy | 24648771 | Khung báo cáo, slide, insight, mô hình |

## Sử dụng công cụ AI

Theo mục IV của đề cương: nhóm dùng Claude (Anthropic) để rà soát tính tái lập, đóng gói các bước làm sạch thành hàm trong `src/`, đổi đường dẫn tuyệt đối sang tương đối và đối chiếu số liệu với Data Dictionary. Logic xử lý do nhóm thiết kế; mọi thành viên giải thích được code đã nộp.

## Lưu ý

- `notebooks/03` và `04` là khung cho Bài tập 3–4; code trong `src/visualization` và `src/models` còn dùng tên cột cũ (`gia_ban_trieu`, `gia_moi_m2_trieu`) và sẽ được cập nhật theo `df_clean.csv`.
- Giá trong dữ liệu là giá chào bán trên tin đăng, không phải giá giao dịch.
