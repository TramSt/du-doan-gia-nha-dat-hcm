"""
TẠO TẬP LÀM SẠCH LẦN 2 (df_clean.csv) TỪ df_raw.csv
====================================================

Các bước (đúng thứ tự trong notebook 02_lam_sach_du_lieu_2.ipynb):
    1. Bỏ cột rò rỉ nhãn (gia_moi_m2_trieu) và cột một giá trị (tinh_thanh)
    2. Bỏ tin thiếu nhãn loại hình
    3. Trích xuất đặc trưng từ tiêu đề + mô tả
    4. Chuẩn hóa loai_hinh về 8 nhóm
    5. Khử trùng lặp theo (giá, diện tích, quận, loại hình)
    6. Lọc ngoại lai đơn giá hai tầng + lọc diện tích
    7. Điền khuyết có kiểm soát (kèm cột đánh dấu)
    8. Che cụm số giá/diện tích trong văn bản
    9. Tạo biến phái sinh, sắp xếp cột
   10. Loại tin có sai số dự đoán lớn (APE > 50%) theo danh sách của lần chạy gốc

Chạy từ thư mục gốc dự án:
    python -m src.features.tao_dac_trung
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils import doc_config, duong_dan_goc  # noqa: E402

# Ngưỡng lọc — giải thích trong notebook 02_lam_sach_du_lieu_2, mục 6
DON_GIA_MIN, DON_GIA_MAX = 15, 450      # triệu VNĐ/m²
HE_SO_IQR = 1.5                         # tính riêng trong từng quận
DIEN_TICH_MIN, DIEN_TICH_MAX = 15, 500  # m²

# Trần chống lỗi nhập liệu cho các số trích từ văn bản
TRAN_GIA_TRI = {"so_phong_ngu": 10, "so_tang": 8, "so_wc": 8,
                "mat_tien_m": 30, "rong_hem_m": 15}

ANH_XA_LOAI_HINH = {
    "nhà rieng": "Nhà riêng", "nhà riêng": "Nhà riêng", "căn hộ": "Căn hộ",
    "nhà phố": "Nhà phố", "nhà mặt tiền": "Nhà mặt tiền", "đất": "Đất",
    "biệt thự": "Biệt thự", "shophouse": "Shophouse",
    "kho - nhà xưởng": "Khác", "nhà hàng - khách sạn": "Khác",
    "bán nhà hàng - khách sạn": "Khác",
}

KHOA_TRUNG_LAP = ["gia_ban", "dien_tich_m2", "quan_huyen", "loai_hinh"]

MAU_SO_KEM_DON_VI = re.compile(
    r"\d+[\.,]?\d*\s*(tỷ|ty|triệu|trieu|tr/m2|tr\b|m²|m2)", re.I)

THU_TU_COT = [
    "gia_ban", "log_gia_ban", "dien_tich_m2", "log_dien_tich",
    "quan_huyen", "phuong", "ten_duong", "loai_hinh",
    "so_phong_ngu", "so_tang", "so_wc", "mat_tien_m", "rong_hem_m", "mat_do_xay",
    "la_hem", "la_mat_tien", "co_so_hong", "co_noi_that", "oto_vao",
    "gan_truong_cho", "chinh_chu", "co_tt_phong_ngu", "co_tt_mat_tien",
    "nguon_du_lieu", "tieu_de_sach", "mo_ta_sach", "url",
]


def trich_dac_trung_van_ban(df: pd.DataFrame) -> pd.DataFrame:
    """Bóc số phòng, số tầng, mặt tiền, hẻm, phường, đường và 7 cờ 0/1 từ văn bản."""
    df = df.copy()
    txt = df["tieu_de"].fillna("") + " || " + df["mo_ta_dac_diem"].fillna("")
    low = txt.str.lower()

    def so(pattern):
        return pd.to_numeric(low.str.extract(pattern, expand=False), errors="coerce")

    # Biến số
    df["so_phong_ngu"] = so(r"(\d{1,2})\s*(?:phòng ngủ|pn\b|p\.ngủ|phong ngu)")
    df["so_tang"] = so(r"(\d{1,2})\s*(?:tầng|lầu|tang\b|lau\b)")
    df["so_wc"] = so(r"(\d{1,2})\s*(?:wc|vệ sinh|toilet)")
    df["mat_tien_m"] = so(r"(?:mt|mặt tiền|ngang)[^\d\n]{0,6}(\d{1,2}(?:[.,]\d{1,2})?)\s*m\b")
    df["rong_hem_m"] = so(r"hẻm[^\d\n]{0,8}(\d{1,2}(?:[.,]\d{1,2})?)\s*m\b")

    # Cờ 0/1: "tin có viết", không phải kiểm chứng thực địa
    df["la_hem"] = low.str.contains(r"hẻm|hẽm|hem \d").astype(int)
    df["la_mat_tien"] = low.str.contains(r"mặt tiền|mặt phố|mt đường").astype(int)
    df["co_so_hong"] = low.str.contains(r"sổ hồng|sổ đỏ|shr\b|sở hữu riêng|pháp lý rõ").astype(int)
    df["co_noi_that"] = low.str.contains(r"nội thất").astype(int)
    df["oto_vao"] = low.str.contains(r"ô tô|oto|xe hơi|ôtô").astype(int)
    df["gan_truong_cho"] = low.str.contains(r"trường học|chợ|siêu thị|bệnh viện").astype(int)
    df["chinh_chu"] = low.str.contains(r"chính chủ").astype(int)

    # Địa danh chi tiết
    df["phuong"] = (txt.str.extract(
        r"(?:[Pp]hường|\bP\.\s?|\bP\s(?=\d))\s*([A-Za-zÀ-ỹ0-9][A-Za-zÀ-ỹ0-9\s]{0,24}?)"
        r"(?=[,\.\-–\|/]|\s{2}|\s(?:quận|Quận|Q\.|q\.)|$)", expand=False)
        .str.strip().str.title().replace("", np.nan))
    df["ten_duong"] = (txt.str.extract(
        r"[ĐđDd]ường\s+([A-ZÀ-Ỹ][A-Za-zÀ-ỹ0-9\s]{1,28}?)(?=[,\.\-–\|]|\s{2}|$)", expand=False)
        .str.strip().str.title().replace("", np.nan))
    return df


def loc_ngoai_lai_don_gia(df: pd.DataFrame) -> pd.Series:
    """Trả về mask giữ lại: chặn cứng 15–450 tr/m² VÀ nằm trong 1.5×IQR của quận."""
    don_gia = df["gia_ban"] / df["dien_tich_m2"]
    chan_cung = don_gia.between(DON_GIA_MIN, DON_GIA_MAX)
    nhom = don_gia.groupby(df["quan_huyen"])
    q1 = nhom.transform(lambda s: s.quantile(0.25))
    q3 = nhom.transform(lambda s: s.quantile(0.75))
    iqr = q3 - q1
    chan_mem = don_gia.between(q1 - HE_SO_IQR * iqr, q3 + HE_SO_IQR * iqr)
    return chan_cung & chan_mem


def dien_khuyet(df: pd.DataFrame) -> pd.DataFrame:
    """Điền khuyết theo bản chất từng cột; tạo cờ đánh dấu TRƯỚC khi điền."""
    df = df.copy()
    df["co_tt_phong_ngu"] = df["so_phong_ngu"].notna().astype(int)
    df["co_tt_mat_tien"] = df["mat_tien_m"].notna().astype(int)

    for cot, tran in TRAN_GIA_TRI.items():
        df[cot] = df[cot].clip(upper=tran)

    df["so_phong_ngu"] = (df["so_phong_ngu"]
                          .fillna(df.groupby("loai_hinh")["so_phong_ngu"].transform("median"))
                          .fillna(df["so_phong_ngu"].median()))
    df["so_tang"] = df["so_tang"].fillna(1)
    df["so_wc"] = df["so_wc"].fillna(df["so_phong_ngu"].clip(upper=4))
    df["mat_tien_m"] = df["mat_tien_m"].fillna(-1)   # −1 = không ghi, KHÔNG phải số đo
    df["rong_hem_m"] = df["rong_hem_m"].fillna(-1)
    df["phuong"] = df["phuong"].fillna("Khong_ro")
    df["ten_duong"] = df["ten_duong"].fillna("Khong_ro")
    return df


FILE_DANH_SACH_APE = "loai_ape_lan_chay_goc.csv"
COT_MO_HINH_APE = ["dien_tich_m2", "so_phong_ngu", "so_tang", "so_wc", "mat_tien_m",
                   "rong_hem_m", "mat_do_xay", "la_hem", "la_mat_tien", "co_so_hong",
                   "co_noi_that", "oto_vao", "gan_truong_cho", "chinh_chu",
                   "co_tt_phong_ngu", "co_tt_mat_tien",
                   "quan_huyen", "loai_hinh", "nguon_du_lieu", "phuong"]


def tai_tao_buoc_ape(df: pd.DataFrame, nguong: float = 0.5) -> pd.Series:
    """
    Tái tạo gần đúng bước lọc APE của lần chạy gốc (để kiểm chứng).

    Random Forest (400 cây, random_state=0) học log(giá) trên 80% dữ liệu
    (train_test_split random_state=42), dự đoán 20% còn lại; đánh dấu tin
    trong phần 20% có |dự đoán − giá| / giá > nguong.
    Lần chạy gốc không lưu phiên bản thư viện nên kết quả chỉ gần khớp.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split

    X = pd.get_dummies(df[COT_MO_HINH_APE]).astype(float)
    y = np.log(df["gia_ban"])
    idx_tr, idx_te = train_test_split(df.index, test_size=0.2, random_state=42)
    mo_hinh = RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1)
    du_doan = np.exp(mo_hinh.fit(X.loc[idx_tr], y.loc[idx_tr]).predict(X.loc[idx_te]))
    ape = (pd.Series(du_doan, index=idx_te) - df.loc[idx_te, "gia_ban"]).abs() / df.loc[idx_te, "gia_ban"]
    return df.index.to_series().isin(ape[ape > nguong].index)


def tao_df_clean(df_raw: pd.DataFrame, in_nhat_ky: bool = True, danh_sach_ape: pd.DataFrame | None = None):
    """
    Chạy toàn bộ bước 1–10. Trả về (df_clean, nhat_ky).
    Bước 10 chỉ chạy khi truyền danh_sach_ape (DataFrame có cột url).

    nhat_ky['bang_loai_dong'] ghi số dòng bị loại ở từng bước — dùng để
    đối chiếu với mục 4.1 của Data Dictionary.
    """
    df = df_raw.copy()
    nk = {"n_ban_dau": len(df), "bang_loai_dong": {}}

    def ghi(ten_buoc, truoc):
        nk["bang_loai_dong"][ten_buoc] = truoc - len(df)

    # 1. Cột rò rỉ nhãn / một giá trị
    df = df.drop(columns=["gia_moi_m2_trieu", "tinh_thanh"])

    # 2. Tin thiếu loại hình (toàn bộ thuộc batdongsan)
    truoc = len(df)
    df = df.dropna(subset=["loai_hinh"])
    ghi("1. Thiếu nhãn loại hình", truoc)

    # 3. Đặc trưng từ văn bản
    df = trich_dac_trung_van_ban(df)
    nk["ty_le_trich_duoc"] = {c: round(float(df[c].notna().mean()), 3) for c in
                             ["so_phong_ngu", "so_tang", "so_wc", "mat_tien_m",
                              "rong_hem_m", "phuong", "ten_duong"]}

    # 4. Chuẩn hóa loại hình
    df["loai_hinh"] = df["loai_hinh"].str.lower().str.strip().map(ANH_XA_LOAI_HINH)
    if df["loai_hinh"].isna().any():
        raise ValueError("Có nhãn loại hình chưa nằm trong ANH_XA_LOAI_HINH")

    # 5. Khử trùng lặp
    truoc = len(df)
    df = df.drop_duplicates(subset=KHOA_TRUNG_LAP, keep="first")
    ghi("2. Trùng (giá, diện tích, quận, loại hình)", truoc)

    # 6. Ngoại lai
    truoc = len(df)
    df = df[loc_ngoai_lai_don_gia(df)].copy()
    ghi("3. Ngoại lai đơn giá (15–450 tr/m² và IQR theo quận)", truoc)

    truoc = len(df)
    df = df[df["dien_tich_m2"].between(DIEN_TICH_MIN, DIEN_TICH_MAX)]
    ghi("4. Diện tích ngoài 15–500 m²", truoc)

    # 7. Điền khuyết
    df = dien_khuyet(df)

    # 8. Che số trong văn bản (chống lộ giá)
    df["mo_ta_sach"] = df["mo_ta_dac_diem"].fillna("").str.replace(
        MAU_SO_KEM_DON_VI, " <SO> ", regex=True)
    df["tieu_de_sach"] = df["tieu_de"].fillna("").str.replace(
        MAU_SO_KEM_DON_VI, " <SO> ", regex=True)

    # 9. Biến phái sinh
    df["log_gia_ban"] = np.log(df["gia_ban"])
    df["log_dien_tich"] = np.log(df["dien_tich_m2"])
    df["mat_do_xay"] = df["so_tang"] * df["dien_tich_m2"]

    df = df[THU_TU_COT].reset_index(drop=True)

    # 10. Loại tin sai số dự đoán lớn (danh sách cố định từ lần chạy gốc)
    if danh_sach_ape is not None:
        truoc = len(df)
        df = df[~df["url"].isin(danh_sach_ape["url"])].reset_index(drop=True)
        ghi("5. Sai số dự đoán thử APE > 50%", truoc)

    nk["tong_loai"] = nk["n_ban_dau"] - len(df)
    nk["n_con_lai"] = len(df)
    nk["loai_hinh"] = df["loai_hinh"].value_counts().to_dict()

    if in_nhat_ky:
        print(json.dumps(nk, ensure_ascii=False, indent=1))
    return df, nk


def main():
    cfg = doc_config()
    goc = duong_dan_goc()
    thu_muc = goc / cfg["duong_dan"]["du_lieu_trung_gian"]
    df_raw = pd.read_csv(thu_muc / "df_raw.csv")
    danh_sach_ape = pd.read_csv(thu_muc / FILE_DANH_SACH_APE)
    df, _ = tao_df_clean(df_raw, danh_sach_ape=danh_sach_ape)
    file_ra = goc / cfg["duong_dan"]["du_lieu_sach"] / "df_clean.csv"
    file_ra.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_ra, index=False)
    print(f"✅ Đã lưu: {file_ra}  ({len(df):,} dòng × {df.shape[1]} cột)")


if __name__ == "__main__":
    main()
