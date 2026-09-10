"""
LÀM SẠCH VÀ HỢP NHẤT DỮ LIỆU TỪ 3 NGUỒN
========================================

Pipeline xử lý:
    1. Đọc dữ liệu thô từ 3 nguồn (mỗi nguồn một schema khác nhau)
    2. Ánh xạ về schema chung
    3. Tách tin BÁN / tin CHO THUÊ  → chỉ giữ tin bán
    4. Lọc đúng phạm vi TP.HCM
    5. Chuẩn hóa nhãn loại hình BĐS
    6. Xử lý ngoại lai (outlier) giá và diện tích
    7. Loại trùng lặp chéo nguồn
    8. Xuất file sạch

Chạy:
    python src/data/lam_sach_du_lieu.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Cho phép import module src khi chạy trực tiếp file này
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils import (
    bo_dau,
    doc_config,
    doi_gia_sang_trieu,
    duong_dan_goc,
    in_tieu_de,
    phan_tich_dien_tich_text,
    phan_tich_gia_text,
    tom_tat_dataframe,
    trich_dien_tich_tu_tieu_de,
)


# ==========================================================
# SCHEMA CHUNG
# Mọi nguồn đều được ánh xạ về đúng bộ cột này
# ==========================================================
SCHEMA_CHUNG = [
    "tieu_de",           # Tiêu đề tin đăng
    "gia_ban",           # Giá bán (triệu VNĐ)
    "dien_tich_m2",      # Diện tích (m²)
    "tinh_thanh",        # Tỉnh/thành phố
    "quan_huyen",        # Quận/huyện (chỉ chotot có sẵn)
    "phuong_xa",         # Phường/xã  (chỉ chotot có sẵn)
    "mo_ta_dac_diem",    # Mô tả đặc điểm (chỉ cafeland và batdongsan có sẵn)
    "loai_hinh",         # Loại hình BĐS (đã chuẩn hóa)
    "nguon_du_lieu",     # CafeLand / batdongsan / chotot
    "url",               # Link gốc, dùng để truy vết
]


# ==========================================================
# BƯỚC 1 — ĐỌC VÀ ÁNH XẠ TỪNG NGUỒN
# ==========================================================

def doc_cafeland(duong_dan: Path) -> pd.DataFrame:
    """
    Đọc nguồn CafeLand.vn và ánh xạ về schema chung.

    Đặc điểm nguồn:
        - 9 cột, giá đã tính bằng TRIỆU VNĐ
        - 100% đã là TP.HCM (crawler chuẩn hóa sẵn)
        - Chỉ có 1 cột địa điểm cấp tỉnh/thành
    """
    df = pd.read_csv(duong_dan)

    ket_qua = pd.DataFrame({
        "tieu_de": df["Tieu_de"],
        # Giá lưu dạng VĂN BẢN ("3 tỷ 150 triệu") -> phải parse
        "gia_ban": df["Gia_ban"].apply(phan_tich_gia_text),
        # Diện tích cũng dạng văn bản ("74,8m2")
        "dien_tich_m2": df["Dien_tich"].apply(phan_tich_dien_tich_text),
        "tinh_thanh": df["Dia_diem"],
        "quan_huyen": np.nan,      # nguồn này không có
        "mo_ta_dac_diem": df["Mo_ta_Dac_diem"],
        "loai_hinh": df["Loai_hinh_BDS"],
        "nguon_du_lieu": "cafeland",
        "url": df["URL"],
    })
    print(f"  [CafeLand]    đọc được {len(ket_qua):,} dòng")
    return ket_qua


def doc_batdongsan(duong_dan: Path) -> pd.DataFrame:
    """
    Đọc nguồn batdongsan.vn và ánh xạ về schema chung.

    Đặc điểm nguồn:
        - Cùng 9 cột như CafeLand, giá bằng TRIỆU VNĐ
        - File định dạng .xlsb → cần engine pyxlsb
        - Loai_hinh_BDS thiếu ~28%
    """
    if str(duong_dan).endswith(".xls"):
        df = pd.read_csv(duong_dan, encoding="utf-8-sig")
    else:
        df = pd.read_csv(duong_dan)

    ket_qua = pd.DataFrame({
        "tieu_de": df["Tieu_de"],
        # Giá dạng văn bản ("11 tỷ 500 triệu")
        "gia_ban": df["Gia_ban"].apply(phan_tich_gia_text),
        # Diện tích dạng văn bản ("33.5 m²")
        "dien_tich_m2": df["Dien_tich"].apply(phan_tich_dien_tich_text),
        "tinh_thanh": df["Dia_diem"],
        "quan_huyen": np.nan,
        "mo_ta_dac_diem": df["Mo_ta_Dac_diem"],
        "loai_hinh": df["Loai_hinh_BDS"],
        "nguon_du_lieu": "batdongsan",
        "url": df["URL"],
    })
    print(f"  [batdongsan]  đọc được {len(ket_qua):,} dòng")
    return ket_qua


def doc_chotot(duong_dan: Path) -> pd.DataFrame:
    """
    Đọc nguồn chotot.com và ánh xạ về schema chung.

    ⚠️ LƯU Ý QUAN TRỌNG — hai xử lý đặc biệt cho nguồn này:

    1. Giá lưu bằng VNĐ NGUYÊN (không phải triệu) → phải chia 1.000.000
    2. Cột `area` BỊ LỖI CRAWL: chỉ khớp 0,1% với diện tích ghi trong
       tiêu đề và bị chặn ở 130m². Vì vậy code KHÔNG dùng cột `area`,
       mà trích lại diện tích từ tiêu đề tin đăng.
       (Cột `price_per_m2` cũng bị loại vì được tính từ `area` lỗi.)
    """
    df = pd.read_csv(duong_dan)

    # Trích lại diện tích từ tiêu đề thay vì tin vào cột area lỗi
    dien_tich_that = df["title"].apply(trich_dien_tich_tu_tieu_de)
    so_trich_duoc = dien_tich_that.notna().sum()
    print(f"  [chotot]      trích lại diện tích từ tiêu đề: "
          f"{so_trich_duoc:,}/{len(df):,} dòng "
          f"({so_trich_duoc/len(df)*100:.1f}%)")

    ket_qua = pd.DataFrame({
        "tieu_de": df["title"],
        # Quy đổi VNĐ -> triệu VNĐ
        "gia_ban": df["price"].apply(
            lambda x: doi_gia_sang_trieu(x, "vnd")
        ),
        "dien_tich_m2": dien_tich_that,
        "tinh_thanh": df["region_name"],
        "quan_huyen": df["area_name"],
        "loai_hinh": df["property_type"],
        "nguon_du_lieu": "chotot",
        "url": df["url"],
    })
    print(f"  [chotot]      đọc được {len(ket_qua):,} dòng")
    return ket_qua


# ==========================================================
# BƯỚC 2 — TÁCH TIN BÁN / TIN CHO THUÊ
# ==========================================================

def phan_loai_giao_dich(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Phân loại từng tin là BÁN hay CHO THUÊ.

    VÌ SAO CẦN BƯỚC NÀY:
    Nguồn chotot trộn lẫn cả hai loại. Giá trung vị tin thuê là
    10 triệu, tin bán là 4,6 tỷ — chênh nhau ~460 lần. Nếu không
    tách, mô hình dự đoán giá bán sẽ cho kết quả vô nghĩa.

    CÁCH LÀM (kết hợp 2 tín hiệu vì chỉ dựa từ khóa thì 44% tin
    không phân loại được):
        1. Từ khóa trong tiêu đề ("cho thuê", "bán"...)
        2. Ngưỡng giá: tin dưới 100 triệu gần như chắc chắn là giá thuê
    """
    tieu_de_thuong = df["tieu_de"].fillna("").str.lower()

    # Tín hiệu 1: từ khóa
    mau_thue = "|".join(cfg["tu_khoa"]["thue"])
    mau_ban = "|".join(cfg["tu_khoa"]["ban"])

    co_tu_thue = tieu_de_thuong.str.contains(mau_thue, regex=True, na=False)
    co_tu_ban = tieu_de_thuong.str.contains(mau_ban, regex=True, na=False)

    # Tín hiệu 2: ngưỡng giá (giá thuê thường < 100 triệu/tháng)
    nguong_gia_ban_toi_thieu = cfg["nguong_loc"]["gia_trieu_vnd"]["min"]
    gia_qua_thap = df["gia_ban"] < nguong_gia_ban_toi_thieu

    # Quy tắc quyết định:
    #   - Có từ "thuê" mà không có từ "bán"  -> THUÊ
    #   - Giá quá thấp so với giá bán BĐS    -> THUÊ
    #   - Còn lại                            -> BÁN
    la_thue = (co_tu_thue & ~co_tu_ban) | gia_qua_thap

    df = df.copy()
    df["loai_giao_dich"] = np.where(la_thue, "thue", "ban")

    thong_ke = df["loai_giao_dich"].value_counts()
    print(f"  Tin BÁN : {thong_ke.get('ban', 0):,}")
    print(f"  Tin THUÊ: {thong_ke.get('thue', 0):,} (sẽ loại bỏ)")

    return df


# ==========================================================
# BƯỚC 3 — LỌC PHẠM VI ĐỊA LÝ
# ==========================================================

def loc_tp_hcm(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Chỉ giữ tin đăng thuộc TP.HCM.

    Mỗi nguồn viết tên thành phố một kiểu ("TP. Hồ Chí Minh",
    "Tp Hồ Chí Minh"...) nên phải so khớp sau khi bỏ dấu.
    """
    # Chuẩn hóa các biến thể tên về dạng không dấu để so khớp
    bien_the_chuan = {bo_dau(x) for x in cfg["pham_vi"]["bien_the_ten_tinh"]}

    tinh_thanh_chuan = df["tinh_thanh"].apply(bo_dau)
    thuoc_hcm = tinh_thanh_chuan.isin(bien_the_chuan)

    truoc = len(df)
    df = df[thuoc_hcm].copy()
    print(f"  Lọc TP.HCM: {truoc:,} -> {len(df):,} dòng "
          f"(loại {truoc - len(df):,})")
    return df


# ==========================================================
# BƯỚC 4 — CHUẨN HÓA NHÃN LOẠI HÌNH
# ==========================================================

def chuan_hoa_loai_hinh(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Gộp các nhãn loại hình BĐS về một bộ chung.

    VÌ SAO CẦN: cùng một loại hình nhưng 3 nguồn ghi khác nhau
    ("Nhà riêng" / "Bán nhà riêng" / "Nhà ở"). Nếu không gộp,
    mô hình sẽ coi đây là các nhóm riêng biệt -> sai lệch.
    """
    anh_xa = cfg["anh_xa_loai_hinh"]

    df = df.copy()
    df["loai_hinh"] = (
        df["loai_hinh"]
        .map(anh_xa)                    # ánh xạ theo bảng
        .fillna(df["loai_hinh"])        # giữ nguyên nếu chưa có trong bảng
    )

    print(f"  Số nhãn sau chuẩn hóa: {df['loai_hinh'].nunique()}")
    for nhan, sl in df["loai_hinh"].value_counts().items():
        print(f"    {nhan:<20} {sl:>7,}")
    print(f"  Số dòng thiếu loai_hinh: {df['loai_hinh'].isna().sum():,}")
    return df


# ==========================================================
# BƯỚC 5 — XỬ LÝ NGOẠI LAI
# ==========================================================

def loc_ngoai_lai(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Loại các giá trị giá / diện tích bất hợp lý.

    Dùng 2 lớp lọc:
        1. Ngưỡng cứng theo hiểu biết thực tế thị trường
        2. Phương pháp IQR (hệ số 3.0 thay vì 1.5 vì giá BĐS
           lệch phải rất mạnh, dùng 1.5 sẽ cắt nhầm nhà cao cấp)
    """
    truoc = len(df)

    # --- Lớp 1: ngưỡng cứng ---
    ng_gia = cfg["nguong_loc"]["gia_trieu_vnd"]
    ng_dt = cfg["nguong_loc"]["dien_tich_m2"]

    df = df[
        df["gia_ban"].between(ng_gia["min"], ng_gia["max"])
        & df["dien_tich_m2"].between(ng_dt["min"], ng_dt["max"])
    ].copy()
    print(f"  Lọc ngưỡng cứng: {truoc:,} -> {len(df):,}")

    # --- Lớp 2: IQR ---
    if cfg["nguong_loc"]["dung_iqr"]:
        he_so = cfg["nguong_loc"]["he_so_iqr"]
        for cot in ["gia_ban", "dien_tich_m2"]:
            q1, q3 = df[cot].quantile([0.25, 0.75])
            iqr = q3 - q1
            can_duoi = q1 - he_so * iqr
            can_tren = q3 + he_so * iqr
            df = df[df[cot].between(can_duoi, can_tren)]
        print(f"  Lọc IQR (hệ số {he_so}): -> {len(df):,}")

    print(f"  Tổng cộng loại: {truoc - len(df):,} dòng ngoại lai")
    return df


# ==========================================================
# BƯỚC 6 — LOẠI TRÙNG LẶP CHÉO NGUỒN
# ==========================================================

def loai_trung_cheo_nguon(df: pd.DataFrame) -> pd.DataFrame:
    """
    Loại tin trùng khi cùng một BĐS được đăng trên nhiều sàn.

    ⚠️ ĐÂY LÀ BƯỚC QUAN TRỌNG NHẤT VỀ MẶT THỐNG KÊ.

    Mỗi sàn có URL riêng nên KHÔNG dùng URL làm khóa được. Nếu để
    trùng, cùng một căn nhà bị đếm nhiều lần -> vi phạm giả định
    các quan sát độc lập của hồi quy -> sai số chuẩn bị co lại
    -> kiểm định thống kê cho kết quả sai.

    KHÓA SO KHỚP: (tiêu đề chuẩn hóa + diện tích + giá làm tròn).

    ⚠️ VÌ SAO KHÔNG DÙNG (quận + loại hình + diện tích + giá):
    Chỉ nguồn chotot có cột `quan_huyen` (98,5% dòng còn lại bị
    trống). Khi quận trống, khóa chỉ còn (loại hình + diện tích +
    giá) — quá lỏng, sẽ gộp nhầm nhiều BĐS KHÁC NHAU nhưng tình
    cờ cùng diện tích và cùng khoảng giá. Thử nghiệm cho thấy
    cách đó xóa nhầm ~8.900 dòng.

    Vì vậy khóa dùng TIÊU ĐỀ đã chuẩn hóa (bỏ dấu, bỏ ký tự đặc
    biệt) làm thành phần chính — tin đăng cùng một BĐS trên các
    sàn khác nhau thường có tiêu đề rất giống nhau.
    """
    truoc = len(df)
    df = df.copy()

    # Chuẩn hóa tiêu đề: bỏ dấu, bỏ ký tự đặc biệt, gộp khoảng trắng
    df["_khoa_tieu_de"] = (
        df["tieu_de"].fillna("")
        .apply(bo_dau)
        .str.replace(r"[^a-z0-9\s]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df["_khoa_dt"] = df["dien_tich_m2"].round(0)
    # Nhóm giá theo bậc 100 triệu để chấp nhận sai lệch nhỏ giữa các sàn
    df["_khoa_gia"] = (df["gia_ban"] / 100).round(0) * 100

    khoa = ["_khoa_tieu_de", "_khoa_dt", "_khoa_gia"]

    # Ưu tiên giữ bản ghi từ nguồn có nhiều thông tin địa lý nhất
    thu_tu_uu_tien = {"chotot": 0, "cafeland": 1, "batdongsan": 2}
    df["_uu_tien"] = df["nguon_du_lieu"].map(thu_tu_uu_tien)
    df = df.sort_values("_uu_tien").reset_index(drop=True)

    # Tách riêng dòng không có tiêu đề (không so khớp được -> giữ nguyên)
    co_tieu_de = df["_khoa_tieu_de"] != ""
    df_co_td = df.loc[co_tieu_de].drop_duplicates(subset=khoa, keep="first")
    df_khong_td = df.loc[~co_tieu_de]
    df = pd.concat([df_co_td, df_khong_td], ignore_index=True)

    # Xóa các cột phụ trợ
    df = df.drop(columns=[c for c in df.columns if c.startswith("_")])

    print(f"  Loại trùng chéo nguồn: {truoc:,} -> {len(df):,} "
          f"(loại {truoc - len(df):,})")
    return df


# ==========================================================
# PIPELINE CHÍNH
# ==========================================================

def chay_pipeline() -> pd.DataFrame:
    """Chạy toàn bộ quy trình làm sạch và hợp nhất."""
    cfg = doc_config()
    goc = duong_dan_goc()
    thu_muc_tho = goc / cfg["duong_dan"]["du_lieu_tho"]

    # ---------- 1. ĐỌC DỮ LIỆU ----------
    in_tieu_de("BƯỚC 1: ĐỌC DỮ LIỆU TỪ 3 NGUỒN")
    cac_df = []

    bo_doc = {
        "cafeland": doc_cafeland,
        "batdongsan": doc_batdongsan,
        "chotot": doc_chotot,
    }

    for ten_nguon, ham_doc in bo_doc.items():
        duong_dan = thu_muc_tho / cfg["file_nguon"][ten_nguon]
        if not duong_dan.exists():
            print(f"  ⚠️  Bỏ qua [{ten_nguon}]: không tìm thấy {duong_dan.name}")
            continue
        cac_df.append(ham_doc(duong_dan))

    if not cac_df:
        raise FileNotFoundError(
            f"Không tìm thấy file dữ liệu nào trong {thu_muc_tho}. "
            "Xem hướng dẫn tải dữ liệu tại docs/DATA.md"
        )

    df = pd.concat(cac_df, ignore_index=True)
    tom_tat_dataframe(df, "SAU KHI GỘP 3 NGUỒN")

    # ---------- 2. TÁCH BÁN / THUÊ ----------
    in_tieu_de("BƯỚC 2: TÁCH TIN BÁN / TIN CHO THUÊ")
    df = phan_loai_giao_dich(df, cfg)
    df = df[df["loai_giao_dich"] == "ban"].drop(columns=["loai_giao_dich"])

    # ---------- 3. LỌC ĐỊA LÝ ----------
    in_tieu_de("BƯỚC 3: LỌC PHẠM VI TP.HCM")
    df = loc_tp_hcm(df, cfg)

    # ---------- 4. CHUẨN HÓA LOẠI HÌNH ----------
    in_tieu_de("BƯỚC 4: CHUẨN HÓA NHÃN LOẠI HÌNH")
    df = chuan_hoa_loai_hinh(df, cfg)

    # ---------- 5. LOẠI DÒNG THIẾU DỮ LIỆU CỐT LÕI ----------
    in_tieu_de("BƯỚC 5: LOẠI DÒNG THIẾU GIÁ HOẶC DIỆN TÍCH")
    truoc = len(df)
    df = df.dropna(subset=["gia_ban", "dien_tich_m2"])
    print(f"  {truoc:,} -> {len(df):,} (loại {truoc - len(df):,})")

    # ---------- 6. LỌC NGOẠI LAI ----------
    in_tieu_de("BƯỚC 6: LỌC NGOẠI LAI")
    df = loc_ngoai_lai(df, cfg)

    # ---------- 7. LOẠI TRÙNG ----------
    in_tieu_de("BƯỚC 7: LOẠI TRÙNG LẶP")
    truoc = len(df)
    df = df.drop_duplicates(subset=["url"])
    print(f"  Loại trùng URL nội bộ: {truoc:,} -> {len(df):,}")
    df = loai_trung_cheo_nguon(df)

    # ---------- 8. TẠO BIẾN PHÁI SINH ----------
    in_tieu_de("BƯỚC 8: TẠO BIẾN PHÁI SINH")
    df["gia_moi_m2_trieu"] = df["gia_ban"] / df["dien_tich_m2"]
    print("  Đã tạo cột: gia_moi_m2_trieu")

    # ---------- 9. XUẤT FILE ----------
    in_tieu_de("KẾT QUẢ CUỐI CÙNG")
    tom_tat_dataframe(df, "DỮ LIỆU SẠCH")

    print("\nPhân bố theo nguồn:")
    for nguon, sl in df["nguon_du_lieu"].value_counts().items():
        print(f"    {nguon:<15} {sl:>7,} ({sl/len(df)*100:5.1f}%)")

    thu_muc_sach = goc / cfg["duong_dan"]["du_lieu_sach"]
    thu_muc_sach.mkdir(parents=True, exist_ok=True)
    file_ra = thu_muc_sach / "du_lieu_sach.csv"
    df.to_csv(file_ra, index=False, encoding="utf-8-sig")
    print(f"\n✅ Đã lưu: {file_ra}")

    return df


if __name__ == "__main__":
    chay_pipeline()
