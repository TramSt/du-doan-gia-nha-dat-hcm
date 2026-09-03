"""
XÂY DỰNG VÀ SO SÁNH MÔ HÌNH DỰ ĐOÁN GIÁ
========================================

Đề cương yêu cầu:
    - Xây dựng ≥2 mô hình khác nhau và so sánh
    - Đánh giá bằng ≥2 chỉ số phù hợp

Module này xây 3 mô hình (Hồi quy tuyến tính, Cây quyết định,
Rừng ngẫu nhiên) và đánh giá bằng 3 chỉ số (R², RMSE, MAE).

Chạy:
    python src/models/huan_luyen_mo_hinh.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils import doc_config, duong_dan_goc, in_tieu_de


# ==========================================================
# CHUẨN BỊ DỮ LIỆU
# ==========================================================

def chuan_bi_dac_trung(df: pd.DataFrame) -> tuple:
    """
    Chuẩn bị ma trận đặc trưng X và biến mục tiêu y.

    LƯU Ý VỀ BIẾN MỤC TIÊU:
    Dùng log(giá) thay vì giá gốc vì:
        1. Giá BĐS lệch phải rất mạnh
        2. Hồi quy tuyến tính giả định phần dư phân phối chuẩn
        3. Hệ số sau đó diễn giải được theo % thay đổi

    LƯU Ý VỀ BIẾN `nguon_du_lieu`:
    Giữ lại làm biến kiểm soát vì 3 nguồn có thể có mặt bằng giá
    khác nhau (mỗi sàn hút một phân khúc người đăng khác nhau).
    Đây là cách xử lý chuẩn khi gộp dữ liệu từ nhiều nguồn.
    """
    dac_trung_so = ["dien_tich_m2"]
    dac_trung_hang = ["loai_hinh", "nguon_du_lieu"]

    # Thêm quận/huyện nếu đủ dữ liệu (chỉ nguồn chotot có)
    if "quan_huyen" in df.columns and df["quan_huyen"].notna().mean() > 0.3:
        dac_trung_hang.append("quan_huyen")
        df = df.copy()
        df["quan_huyen"] = df["quan_huyen"].fillna("Khong ro")

    cot_dung = dac_trung_so + dac_trung_hang
    df_sach = df.dropna(subset=cot_dung + ["gia_ban_trieu"])

    X = df_sach[cot_dung]
    y = np.log(df_sach["gia_ban_trieu"])  # log-transform

    print(f"  Số mẫu       : {len(X):,}")
    print(f"  Đặc trưng số : {dac_trung_so}")
    print(f"  Đặc trưng hạng: {dac_trung_hang}")
    print(f"  Biến mục tiêu: log(gia_ban_trieu)")

    return X, y, dac_trung_so, dac_trung_hang


def tao_bo_tien_xu_ly(dac_trung_so: list, dac_trung_hang: list):
    """
    Tạo bộ tiền xử lý: chuẩn hóa biến số + mã hóa one-hot biến hạng.

    Đặt trong Pipeline để tránh rò rỉ dữ liệu (data leakage):
    bộ chuẩn hóa chỉ học từ tập train, không nhìn thấy tập test.
    """
    return ColumnTransformer([
        ("so", StandardScaler(), dac_trung_so),
        ("hang", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         dac_trung_hang),
    ])


# ==========================================================
# ĐÁNH GIÁ
# ==========================================================

def danh_gia(y_that, y_du_doan, ten_mo_hinh: str) -> dict:
    """
    Tính các chỉ số đánh giá.

    Vì mô hình dự đoán log(giá), cần đổi ngược về giá gốc (exp)
    trước khi tính RMSE và MAE — để con số có ý nghĩa thực tế
    (đơn vị triệu VNĐ), dễ giải thích cho người không chuyên.
    """
    # R² tính trên thang log (thang mà mô hình thực sự học)
    r2 = r2_score(y_that, y_du_doan)

    # RMSE, MAE tính trên thang gốc để dễ diễn giải
    y_that_goc = np.exp(y_that)
    y_du_doan_goc = np.exp(y_du_doan)
    rmse = np.sqrt(mean_squared_error(y_that_goc, y_du_doan_goc))
    mae = mean_absolute_error(y_that_goc, y_du_doan_goc)

    return {
        "Mô hình": ten_mo_hinh,
        "R2": round(r2, 4),
        "RMSE (triệu)": round(rmse, 1),
        "MAE (triệu)": round(mae, 1),
    }


# ==========================================================
# HUẤN LUYỆN
# ==========================================================

def chay_huan_luyen(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Huấn luyện và so sánh 3 mô hình."""
    cfg = doc_config()
    goc = duong_dan_goc()

    if df is None:
        file_sach = goc / cfg["duong_dan"]["du_lieu_sach"] / "du_lieu_sach.csv"
        if not file_sach.exists():
            raise FileNotFoundError(
                f"Chưa có file {file_sach}. "
                "Chạy trước: python src/data/lam_sach_du_lieu.py"
            )
        df = pd.read_csv(file_sach)

    # ---------- Chuẩn bị ----------
    in_tieu_de("BƯỚC 1: CHUẨN BỊ ĐẶC TRƯNG")
    X, y, dt_so, dt_hang = chuan_bi_dac_trung(df)

    # ---------- Chia train/test ----------
    in_tieu_de("BƯỚC 2: CHIA TẬP TRAIN / TEST")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=cfg["mo_hinh"]["ty_le_test"],
        random_state=cfg["mo_hinh"]["random_state"],
    )
    print(f"  Train: {len(X_train):,} mẫu")
    print(f"  Test : {len(X_test):,} mẫu")

    # ---------- Định nghĩa mô hình ----------
    rs = cfg["mo_hinh"]["random_state"]
    cac_mo_hinh = {
        "Hồi quy tuyến tính": LinearRegression(),
        "Cây quyết định": DecisionTreeRegressor(
            max_depth=12, min_samples_leaf=20, random_state=rs
        ),
        "Rừng ngẫu nhiên": RandomForestRegressor(
            n_estimators=200, max_depth=20, min_samples_leaf=5,
            random_state=rs, n_jobs=-1
        ),
    }

    # ---------- Huấn luyện & đánh giá ----------
    in_tieu_de("BƯỚC 3: HUẤN LUYỆN VÀ ĐÁNH GIÁ")
    ket_qua = []
    mo_hinh_da_train = {}

    for ten, bo_uoc_luong in cac_mo_hinh.items():
        print(f"\n  ▶ {ten}")

        pipeline = Pipeline([
            ("tien_xu_ly", tao_bo_tien_xu_ly(dt_so, dt_hang)),
            ("mo_hinh", bo_uoc_luong),
        ])
        pipeline.fit(X_train, y_train)
        y_du_doan = pipeline.predict(X_test)

        chi_so = danh_gia(y_test, y_du_doan, ten)

        # Kiểm định chéo để chắc chắn kết quả ổn định
        diem_cv = cross_val_score(
            pipeline, X_train, y_train,
            cv=cfg["mo_hinh"]["so_fold_cv"], scoring="r2", n_jobs=-1
        )
        chi_so["R2 (CV trung bình)"] = round(diem_cv.mean(), 4)
        chi_so["R2 (CV độ lệch)"] = round(diem_cv.std(), 4)

        ket_qua.append(chi_so)
        mo_hinh_da_train[ten] = pipeline

        print(f"     R²   = {chi_so['R2']}")
        print(f"     RMSE = {chi_so['RMSE (triệu)']:,} triệu VNĐ")
        print(f"     MAE  = {chi_so['MAE (triệu)']:,} triệu VNĐ")
        print(f"     R² qua {cfg['mo_hinh']['so_fold_cv']}-fold CV = "
              f"{chi_so['R2 (CV trung bình)']} "
              f"(± {chi_so['R2 (CV độ lệch)']})")

    # ---------- Bảng so sánh ----------
    in_tieu_de("BẢNG SO SÁNH CÁC MÔ HÌNH")
    bang = pd.DataFrame(ket_qua).sort_values("R2", ascending=False)
    print(bang.to_string(index=False))

    tot_nhat = bang.iloc[0]["Mô hình"]
    print(f"\n🏆 Mô hình tốt nhất: {tot_nhat}")

    # ---------- Độ quan trọng đặc trưng ----------
    if tot_nhat in ("Rừng ngẫu nhiên", "Cây quyết định"):
        in_tieu_de("ĐỘ QUAN TRỌNG CỦA CÁC ĐẶC TRƯNG")
        pipe = mo_hinh_da_train[tot_nhat]
        ten_dac_trung = pipe.named_steps["tien_xu_ly"].get_feature_names_out()
        do_quan_trong = pipe.named_steps["mo_hinh"].feature_importances_

        top = (pd.DataFrame({
            "Đặc trưng": ten_dac_trung,
            "Độ quan trọng": do_quan_trong,
        }).sort_values("Độ quan trọng", ascending=False).head(15))
        print(top.to_string(index=False))

    # ---------- Lưu kết quả ----------
    thu_muc_bc = goc / "reports"
    thu_muc_bc.mkdir(parents=True, exist_ok=True)
    file_ra = thu_muc_bc / "ket_qua_mo_hinh.csv"
    bang.to_csv(file_ra, index=False, encoding="utf-8-sig")
    print(f"\n✅ Đã lưu bảng so sánh: {file_ra}")

    return bang


if __name__ == "__main__":
    chay_huan_luyen()
