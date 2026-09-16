"""
Các hàm tiện ích dùng chung cho toàn dự án.

Cách dùng:
    from src.utils import doc_config, duong_dan_goc
"""

from pathlib import Path
import re
import unicodedata

import yaml


# ==========================================================
# ĐƯỜNG DẪN
# ==========================================================

def duong_dan_goc() -> Path:
    """
    Trả về đường dẫn thư mục gốc của dự án.

    Hàm này đi ngược lên từ vị trí file utils.py (src/utils.py)
    nên luôn đúng dù chạy code từ notebook hay từ terminal.
    """
    return Path(__file__).resolve().parent.parent


def doc_config(ten_file: str = "config/config.yaml") -> dict:
    """
    Đọc file cấu hình YAML.

    Tham số:
        ten_file: đường dẫn tương đối từ thư mục gốc dự án.

    Trả về:
        dict chứa toàn bộ cấu hình.
    """
    duong_dan = duong_dan_goc() / ten_file
    with open(duong_dan, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ==========================================================
# XỬ LÝ CHUỖI TIẾNG VIỆT
# ==========================================================

def bo_dau(chuoi: str) -> str:
    """
    Bỏ dấu tiếng Việt và chuyển về chữ thường.

    Dùng để so khớp tên địa danh giữa 3 nguồn dữ liệu, vì mỗi
    nguồn viết một kiểu: "TP. Hồ Chí Minh" / "Tp Hồ Chí Minh" /
    "Thành phố Hồ Chí Minh".

    Ví dụ:
        >>> bo_dau("Quận Bình Thạnh")
        'quan binh thanh'
    """
    if not isinstance(chuoi, str):
        return ""
    # Chuẩn hóa Unicode: tách ký tự gốc và dấu
    chuoi = unicodedata.normalize("NFD", chuoi)
    # Bỏ các ký tự dấu (category Mn = Mark, nonspacing)
    chuoi = "".join(c for c in chuoi if unicodedata.category(c) != "Mn")
    # Riêng chữ đ/Đ không tách được bằng NFD, phải thay thủ công
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")
    return chuoi.lower().strip()


def chuan_hoa_khoang_trang(chuoi: str) -> str:
    """Gộp nhiều khoảng trắng liên tiếp thành một, bỏ khoảng trắng thừa."""
    if not isinstance(chuoi, str):
        return ""
    return re.sub(r"\s+", " ", chuoi).strip()


# ==========================================================
# TRÍCH XUẤT SỐ LIỆU TỪ VĂN BẢN
# ==========================================================

def trich_dien_tich_tu_tieu_de(tieu_de: str) -> float | None:
    """
    Trích diện tích (m²) từ tiêu đề tin đăng.

    LÝ DO CẦN HÀM NÀY: cột `area` của nguồn chotot.com bị lỗi crawl
    (chỉ khớp 0,1% với diện tích ghi trong tiêu đề, bị chặn ở 130m²).
    Hàm này dùng để khôi phục lại diện tích thật.

    Ví dụ:
        >>> trich_dien_tich_tu_tieu_de("Bán đất 85.7m² hẻm ô tô")
        85.7
        >>> trich_dien_tich_tu_tieu_de("Nhà đẹp giá tốt")

    Trả về:
        float nếu tìm thấy, None nếu không.
    """
    if not isinstance(tieu_de, str):
        return None

    # Bắt các dạng: 85m2, 85.7m², 85,7 m2, 100 M2
    mau = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(?:m2|m²|m\^2)",
        tieu_de.lower()
    )
    if not mau:
        return None

    try:
        # Dấu phẩy trong tiếng Việt là dấu thập phân: "85,7" -> 85.7
        return float(mau.group(1).replace(",", "."))
    except ValueError:
        return None


def phan_tich_gia_text(gia_text) -> float | None:
    """
    Chuyển chuỗi giá tiếng Việt về số, đơn vị TRIỆU VNĐ.

    LÝ DO CẦN HÀM NÀY: CafeLand và batdongsan.vn lưu giá dưới dạng
    VĂN BẢN tiếng Việt ("11 tỷ 500 triệu") chứ không phải số. Nếu
    dùng thẳng pd.to_numeric sẽ ra NaN toàn bộ và mất hết dữ liệu.

    Xử lý được các dạng:
        "11 tỷ 500 triệu"  -> 11500.0
        "7 tỷ"             -> 7000.0
        "850 triệu"        -> 850.0
        "3 tỷ 150 triệu"   -> 3150.0
        "4,X tỷ..."        -> None  (giá mập mờ, không dùng được)

    Trả về:
        float (triệu VNĐ) nếu phân tích được, None nếu không.
    """
    # Nếu đã là số thì trả về luôn
    if isinstance(gia_text, (int, float)):
        try:
            gia = float(gia_text)
            return gia if gia > 0 else None
        except (TypeError, ValueError):
            return None

    if not isinstance(gia_text, str):
        return None

    text = gia_text.lower().strip()

    # Loại các tin ghi giá mập mờ kiểu "4,X tỷ", "giá thỏa thuận"
    if "x" in text.replace("xưởng", "") or "thỏa thuận" in text:
        return None

    tong = 0.0
    tim_thay = False

    # Phần "tỷ" — 1 tỷ = 1.000 triệu
    mau_ty = re.search(r"(\d+(?:[.,]\d+)?)\s*tỷ", text)
    if mau_ty:
        tong += float(mau_ty.group(1).replace(",", ".")) * 1000
        tim_thay = True

    # Phần "triệu" — có thể đứng sau "tỷ" ("3 tỷ 150 triệu")
    mau_trieu = re.search(r"(\d+(?:[.,]\d+)?)\s*triệu", text)
    if mau_trieu:
        tong += float(mau_trieu.group(1).replace(",", "."))
        tim_thay = True

    if not tim_thay:
        return None

    return tong if tong > 0 else None


def phan_tich_dien_tich_text(dt_text) -> float | None:
    """
    Chuyển chuỗi diện tích về số (m²).

    Xử lý được: "74,8m2", "459m2", "33.5 m²", "128.4m2"

    Lưu ý: trong tiếng Việt dấu phẩy là dấu thập phân, nên
    "74,8m2" phải hiểu là 74.8 chứ không phải 748.
    """
    if isinstance(dt_text, (int, float)):
        try:
            dt = float(dt_text)
            return dt if dt > 0 else None
        except (TypeError, ValueError):
            return None

    if not isinstance(dt_text, str):
        return None

    mau = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(?:m2|m²|m\^2)",
        dt_text.lower()
    )
    if not mau:
        return None

    try:
        gia_tri = float(mau.group(1).replace(",", "."))
        return gia_tri if gia_tri > 0 else None
    except ValueError:
        return None


def doi_gia_sang_trieu(gia, don_vi_goc: str = "vnd") -> float | None:
    """
    Quy đổi giá về đơn vị TRIỆU VNĐ để thống nhất giữa 3 nguồn.

    Lý do: CafeLand và batdongsan.vn lưu giá bằng triệu VNĐ,
    còn chotot.com lưu bằng VNĐ nguyên.

    Tham số:
        gia: giá trị gốc
        don_vi_goc: "vnd" hoặc "trieu"

    Ví dụ:
        >>> doi_gia_sang_trieu(3500000000, "vnd")
        3500.0
        >>> doi_gia_sang_trieu(3500, "trieu")
        3500.0
    """
    try:
        gia = float(gia)
    except (TypeError, ValueError):
        return None

    if don_vi_goc == "vnd":
        return gia / 1_000_000
    return gia


# ==========================================================
# HIỂN THỊ
# ==========================================================

def in_tieu_de(tieu_de: str, ky_tu: str = "=", do_dai: int = 60) -> None:
    """In tiêu đề có khung để log dễ đọc."""
    print("\n" + ky_tu * do_dai)
    print(tieu_de)
    print(ky_tu * do_dai)


def tom_tat_dataframe(df, ten: str = "DataFrame") -> None:
    """
    In tóm tắt nhanh một DataFrame: kích thước, thiếu dữ liệu, trùng lặp.

    Dùng sau mỗi bước xử lý để kiểm tra dữ liệu không bị hỏng.
    """
    in_tieu_de(f"TÓM TẮT: {ten}")
    print(f"Kích thước      : {df.shape[0]:,} dòng × {df.shape[1]} cột")
    print(f"Trùng lặp toàn bộ: {df.duplicated().sum():,} dòng")

    thieu = df.isna().sum()
    thieu = thieu[thieu > 0].sort_values(ascending=False)
    if len(thieu) == 0:
        print("Thiếu dữ liệu   : không có")
    else:
        print("Thiếu dữ liệu   :")
        for cot, so_luong in thieu.items():
            ty_le = so_luong / len(df) * 100
            print(f"    {cot:<30} {so_luong:>7,} ({ty_le:5.1f}%)")
