"""
VẼ BIỂU ĐỒ CHO PHẦN EDA
=======================

Đề cương yêu cầu ≥8 biểu đồ chuyên nghiệp có diễn giải.
Module này cung cấp sẵn 8 hàm vẽ, mỗi hàm một biểu đồ.

Chạy:
    python src/visualization/ve_bieu_do.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils import doc_config, duong_dan_goc, in_tieu_de


def thiet_lap_style(cfg: dict) -> None:
    """Thiết lập kiểu hiển thị chung cho mọi biểu đồ."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = cfg["bieu_do"]["kich_thuoc"]
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = cfg["bieu_do"]["dpi"]
    plt.rcParams["font.size"] = cfg["bieu_do"]["font_size"]
    plt.rcParams["axes.titlesize"] = cfg["bieu_do"]["font_size"] + 3
    plt.rcParams["axes.titleweight"] = "bold"
    # Font hỗ trợ tiếng Việt
    plt.rcParams["font.family"] = ["DejaVu Sans"]


def _luu(fig, ten_file: str, thu_muc: Path) -> None:
    """Lưu biểu đồ ra file PNG."""
    thu_muc.mkdir(parents=True, exist_ok=True)
    duong_dan = thu_muc / f"{ten_file}.png"
    fig.savefig(duong_dan, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"  ✅ {duong_dan.name}")


# ==========================================================
# 8 BIỂU ĐỒ CHO EDA
# ==========================================================

def bd01_phan_bo_gia(df: pd.DataFrame, thu_muc: Path) -> None:
    """
    Biểu đồ 1: Phân bố giá bán.

    Vẽ 2 bản: thang thường và thang log. Giá BĐS lệch phải rất
    mạnh nên thang log giúp nhìn rõ hình dạng phân phối hơn.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    sns.histplot(df["gia_ban_trieu"], bins=60, ax=ax1, color="#2D6A5A")
    ax1.set_title("Phân bố giá bán (thang thường)")
    ax1.set_xlabel("Giá bán (triệu VNĐ)")
    ax1.set_ylabel("Số lượng tin")

    sns.histplot(np.log10(df["gia_ban_trieu"]), bins=60, ax=ax2, color="#C0673D")
    ax2.set_title("Phân bố giá bán (thang log10)")
    ax2.set_xlabel("log10(Giá bán)")
    ax2.set_ylabel("Số lượng tin")

    fig.suptitle("Biểu đồ 1 — Phân bố giá bán nhà đất TP.HCM",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    _luu(fig, "bd01_phan_bo_gia", thu_muc)
    plt.show()
    plt.close(fig)


def bd02_phan_bo_dien_tich(df: pd.DataFrame, thu_muc: Path) -> None:
    """Biểu đồ 2: Phân bố diện tích."""
    fig, ax = plt.subplots()
    sns.histplot(df["dien_tich_m2"], bins=60, ax=ax, color="#2D6A5A")
    ax.set_title("Biểu đồ 2 — Phân bố diện tích bất động sản")
    ax.set_xlabel("Diện tích (m²)")
    ax.set_ylabel("Số lượng tin")
    _luu(fig, "bd02_phan_bo_dien_tich", thu_muc)


def bd03_gia_theo_loai_hinh(df: pd.DataFrame, thu_muc: Path) -> None:
    """
    Biểu đồ 3: So sánh giá theo loại hình BĐS (boxplot).

    Boxplot cho thấy cả trung vị lẫn độ phân tán — phù hợp để
    so sánh nhiều nhóm cùng lúc.
    """
    thu_tu = (df.groupby("loai_hinh")["gia_ban_trieu"]
              .median().sort_values(ascending=False).index)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x="loai_hinh", y="gia_ban_trieu",
                order=thu_tu, ax=ax, hue="loai_hinh", legend=False,
                palette="Set2", showfliers=False)
    ax.set_title("Biểu đồ 3 — Giá bán theo loại hình bất động sản")
    ax.set_xlabel("Loại hình")
    ax.set_ylabel("Giá bán (triệu VNĐ)")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    _luu(fig, "bd03_gia_theo_loai_hinh", thu_muc)


def bd04_tuong_quan_dien_tich_gia(df: pd.DataFrame, thu_muc: Path) -> None:
    """
    Biểu đồ 4: Mối quan hệ diện tích ↔ giá bán (scatter).

    Đây là biểu đồ then chốt trả lời Câu hỏi 1: diện tích có
    thực sự dự báo được giá không?
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.scatterplot(data=df, x="dien_tich_m2", y="gia_ban_trieu",
                    hue="loai_hinh", alpha=0.4, s=25, ax=ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Biểu đồ 4 — Quan hệ giữa diện tích và giá bán (thang log)")
    ax.set_xlabel("Diện tích (m²) — thang log")
    ax.set_ylabel("Giá bán (triệu VNĐ) — thang log")
    ax.legend(title="Loại hình", bbox_to_anchor=(1.02, 1), loc="upper left")
    _luu(fig, "bd04_tuong_quan_dien_tich_gia", thu_muc)


def bd05_top_quan_huyen(df: pd.DataFrame, thu_muc: Path) -> None:
    """
    Biểu đồ 5: Top quận/huyện theo giá trung vị mỗi m².

    Trả lời trực tiếp Câu hỏi 2 về chênh lệch giá giữa các khu vực.
    Dùng giá/m² thay vì giá tuyệt đối để loại bỏ ảnh hưởng của
    diện tích — đúng yêu cầu "sau khi đã xem xét diện tích".
    """
    sub = df.dropna(subset=["quan_huyen"])
    if len(sub) == 0:
        print("  ⚠️  Bỏ qua bd05: không có dữ liệu quận/huyện")
        return

    top = (sub.groupby("quan_huyen")
           .agg(gia_m2=("gia_moi_m2_trieu", "median"), so_tin=("gia_moi_m2_trieu", "size"))
           .query("so_tin >= 20")
           .sort_values("gia_m2", ascending=False)
           .head(15))

    fig, ax = plt.subplots(figsize=(11, 7))
    sns.barplot(x=top["gia_m2"], y=top.index, ax=ax,
                hue=top.index, legend=False, palette="viridis")
    ax.set_title("Biểu đồ 5 — Top 15 quận/huyện theo giá trung vị mỗi m²")
    ax.set_xlabel("Giá trung vị (triệu VNĐ/m²)")
    ax.set_ylabel("Quận / Huyện")
    _luu(fig, "bd05_top_quan_huyen", thu_muc)


def bd06_ma_tran_tuong_quan(df: pd.DataFrame, thu_muc: Path) -> None:
    """Biểu đồ 6: Ma trận tương quan giữa các biến số."""
    cot_so = ["gia_ban_trieu", "dien_tich_m2", "gia_moi_m2_trieu"]
    cot_so = [c for c in cot_so if c in df.columns]

    tuong_quan = df[cot_so].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(tuong_quan, annot=True, fmt=".3f", cmap="RdYlGn",
                center=0, square=True, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Biểu đồ 6 — Ma trận tương quan giữa các biến số")
    _luu(fig, "bd06_ma_tran_tuong_quan", thu_muc)


def bd07_so_sanh_nguon(df: pd.DataFrame, thu_muc: Path) -> None:
    """
    Biểu đồ 7: So sánh mặt bằng giá giữa 3 nguồn dữ liệu.

    ⚠️ BIỂU ĐỒ QUAN TRỌNG VỀ MẶT PHƯƠNG PHÁP LUẬN.
    Nếu 3 nguồn có phân phối giá khác nhau rõ rệt, việc gộp
    chung cần thận trọng và phải giữ `nguon_du_lieu` làm biến
    kiểm soát trong mô hình.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    sns.boxplot(data=df, x="nguon_du_lieu", y="gia_ban_trieu",
                ax=ax1, hue="nguon_du_lieu", legend=False,
                palette="Set3", showfliers=False)
    ax1.set_title("Phân bố giá bán theo nguồn")
    ax1.set_xlabel("Nguồn dữ liệu")
    ax1.set_ylabel("Giá bán (triệu VNĐ)")

    sns.countplot(data=df, x="nguon_du_lieu", ax=ax2,
                  hue="nguon_du_lieu", legend=False, palette="Set3")
    ax2.set_title("Số lượng tin theo nguồn")
    ax2.set_xlabel("Nguồn dữ liệu")
    ax2.set_ylabel("Số tin")

    fig.suptitle("Biểu đồ 7 — So sánh giữa 3 nguồn dữ liệu",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    _luu(fig, "bd07_so_sanh_nguon", thu_muc)


def bd08_gia_m2_theo_loai_hinh(df: pd.DataFrame, thu_muc: Path) -> None:
    """
    Biểu đồ 8: Phân bố giá mỗi m² theo loại hình (violin plot).

    Violin plot cho thấy hình dạng phân phối đầy đủ, không chỉ
    các phân vị như boxplot.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.violinplot(data=df, x="loai_hinh", y="gia_moi_m2_trieu",
                   ax=ax, hue="loai_hinh", legend=False,
                   palette="Set2", cut=0)
    ax.set_title("Biểu đồ 8 — Phân bố giá mỗi m² theo loại hình")
    ax.set_xlabel("Loại hình")
    ax.set_ylabel("Giá mỗi m² (triệu VNĐ)")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    _luu(fig, "bd08_gia_m2_theo_loai_hinh", thu_muc)


# ==========================================================
# CHẠY TẤT CẢ
# ==========================================================

def ve_tat_ca(df: pd.DataFrame | None = None) -> None:
    """Vẽ toàn bộ 8 biểu đồ và lưu vào reports/figures/."""
    cfg = doc_config()
    goc = duong_dan_goc()
    thiet_lap_style(cfg)

    if df is None:
        file_sach = goc / cfg["duong_dan"]["du_lieu_sach"] / "du_lieu_sach.csv"
        if not file_sach.exists():
            raise FileNotFoundError(
                f"Chưa có file {file_sach}. "
                "Chạy trước: python src/data/lam_sach_du_lieu.py"
            )
        df = pd.read_csv(file_sach)

    thu_muc = goc / cfg["duong_dan"]["bieu_do"]

    in_tieu_de("VẼ 8 BIỂU ĐỒ CHO PHẦN EDA")
    for ham in [
        bd01_phan_bo_gia,
        bd02_phan_bo_dien_tich,
        bd03_gia_theo_loai_hinh,
        bd04_tuong_quan_dien_tich_gia,
        bd05_top_quan_huyen,
        bd06_ma_tran_tuong_quan,
        bd07_so_sanh_nguon,
        bd08_gia_m2_theo_loai_hinh,
    ]:
        try:
            ham(df, thu_muc)
        except Exception as loi:
            print(f"  ❌ Lỗi ở {ham.__name__}: {loi}")

    print(f"\n✅ Biểu đồ đã lưu tại: {thu_muc}")


if __name__ == "__main__":
    ve_tat_ca()
