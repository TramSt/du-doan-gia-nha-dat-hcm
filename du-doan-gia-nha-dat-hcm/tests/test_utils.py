"""
Kiểm thử các hàm tiện ích.

Chạy:
    pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils import (
    bo_dau,
    chuan_hoa_khoang_trang,
    doi_gia_sang_trieu,
    trich_dien_tich_tu_tieu_de,
)


# ==========================================================
# TEST: bo_dau
# ==========================================================

class TestBoDau:
    """Kiểm tra hàm bỏ dấu tiếng Việt."""

    def test_bo_dau_co_ban(self):
        assert bo_dau("Quận Bình Thạnh") == "quan binh thanh"

    def test_bo_dau_chu_d(self):
        """Chữ đ/Đ phải chuyển thành d/D."""
        assert bo_dau("Đường Điện Biên Phủ") == "duong dien bien phu"

    def test_cac_bien_the_ten_tp_hcm_deu_giong_nhau(self):
        """
        Đây là test quan trọng: 3 nguồn viết tên TP.HCM khác nhau,
        sau khi bỏ dấu phải ra kết quả so khớp được.
        """
        assert bo_dau("TP. Hồ Chí Minh") == bo_dau("tp. ho chi minh")
        assert bo_dau("Tp Hồ Chí Minh") == "tp ho chi minh"

    def test_dau_vao_khong_phai_chuoi(self):
        assert bo_dau(None) == ""
        assert bo_dau(123) == ""


# ==========================================================
# TEST: trich_dien_tich_tu_tieu_de
# ==========================================================

class TestTrichDienTich:
    """
    Kiểm tra hàm trích diện tích từ tiêu đề.

    Hàm này rất quan trọng vì dùng để khôi phục diện tích cho
    nguồn chotot (cột `area` bị lỗi crawl).
    """

    @pytest.mark.parametrize("tieu_de,mong_doi", [
        ("Bán đất 85.7m² hẻm ô tô", 85.7),
        ("Nhà 78m2 hẻm xe hơi", 78.0),
        ("Cho thuê 22 m2 giá 2tr", 22.0),
        ("BÁN ĐẤT 100M² FULL THỔ CƯ", 100.0),
        ("Căn hộ 60,5m2 2PN", 60.5),          # dấu phẩy thập phân VN
    ])
    def test_trich_duoc_dien_tich(self, tieu_de, mong_doi):
        assert trich_dien_tich_tu_tieu_de(tieu_de) == mong_doi

    def test_khong_co_dien_tich_tra_ve_none(self):
        assert trich_dien_tich_tu_tieu_de("Nhà đẹp giá tốt") is None

    def test_dau_vao_khong_hop_le(self):
        assert trich_dien_tich_tu_tieu_de(None) is None
        assert trich_dien_tich_tu_tieu_de(123) is None


# ==========================================================
# TEST: doi_gia_sang_trieu
# ==========================================================

class TestDoiGia:
    """
    Kiểm tra quy đổi giá.

    Quan trọng vì chotot lưu giá bằng VNĐ nguyên, còn 2 nguồn
    kia lưu bằng triệu VNĐ. Sai bước này là sai toàn bộ mô hình.
    """

    def test_doi_tu_vnd_sang_trieu(self):
        assert doi_gia_sang_trieu(3_500_000_000, "vnd") == 3500.0

    def test_giu_nguyen_neu_da_la_trieu(self):
        assert doi_gia_sang_trieu(3500, "trieu") == 3500.0

    def test_gia_tri_khong_hop_le(self):
        assert doi_gia_sang_trieu(None) is None
        assert doi_gia_sang_trieu("abc") is None


# ==========================================================
# TEST: chuan_hoa_khoang_trang
# ==========================================================

def test_chuan_hoa_khoang_trang():
    assert chuan_hoa_khoang_trang("Nhà   đẹp    giá tốt") == "Nhà đẹp giá tốt"
    assert chuan_hoa_khoang_trang("  có khoảng trắng thừa  ") == "có khoảng trắng thừa"
