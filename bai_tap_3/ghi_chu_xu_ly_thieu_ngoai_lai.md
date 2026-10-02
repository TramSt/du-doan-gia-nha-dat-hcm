# Ghi chú xử lý giá trị thiếu và ngoại lai

**Bài tập 3 — Lập trình Phân tích Dữ liệu (2101681) · Liên minh Nhóm 7 & 8**
Dữ liệu: tin đăng bất động sản TP.HCM thu thập từ CafeLand và batdongsan.com.vn
Đầu vào: `df_raw` → `df_clean.csv` (BT2) → `df_bt3.csv` (BT3)

---

## 1. Bức tranh tổng thể

`df_clean.csv` có **7.436 dòng × 27 cột** và `df.isna().sum().sum() = 0`. **Con số 0 này không có nghĩa là dữ liệu đầy đủ.** BT2 đã chuyển mọi giá trị thiếu thành *giá trị mã hóa* để không mất dấu vết của chúng:

| Dạng mã hóa | Cột áp dụng | Tỷ lệ |
|---|---|---|
| `−1` (số canh gác) | `mat_tien_m` | 78,3% |
| `−1` | `rong_hem_m` | 88,2% |
| `'Khong_ro'` | `phuong` | 67,3% |
| `'Khong_ro'` | `ten_duong` | 38,8% |
| Điền trung vị + cờ `co_tt_phong_ngu = 0` | `so_phong_ngu` | 26,2% |

Nguyên tắc xuyên suốt: **không xóa dấu vết của việc thiếu**. Mỗi lần điền giá trị đều đi kèm một cờ 0/1 cho biết giá trị đó là thật hay là suy ra, để các bước phân tích sau có thể lọc lại.

---

## 2. Xử lý giá trị thiếu — từng biến một

### 2.1. `so_phong_ngu` — điền trung vị theo `loai_hinh`

**Cách làm:** với mỗi loại hình (Căn hộ, Nhà riêng, Biệt thự…), điền giá trị thiếu bằng trung vị số phòng ngủ của chính loại hình đó. Đánh dấu `co_tt_phong_ngu = 0`.

**Vì sao không điền trung vị chung:** số phòng ngủ phụ thuộc rất mạnh vào loại hình — căn hộ 2 PN và biệt thự 6 PN là hai thế giới khác nhau. Một trung vị chung sẽ gán 3 PN cho cả hai.

**Vì sao trung vị chứ không phải trung bình:** phân phối số phòng ngủ lệch phải và bị winsorize ở 10 (xem 3.3), trung bình sẽ bị kéo lên.

**Hệ quả quan sát được:** trong 1.950 tin được điền, **1.683 tin (86%) nhận giá trị 3 PN**. Nếu phân tích trên toàn bộ dữ liệu, nhóm 3 PN phình lên gần 3.000 tin mà hơn một nửa là số bịa, kéo trung vị nhóm này lệch hẳn. Vì vậy **mục 3.6 của notebook lọc `co_tt_phong_ngu == 1` trước khi vẽ boxplot** — đây là lý do cờ tồn tại.

### 2.2. `so_tang` — điền 1

Thiếu tập trung ở Căn hộ và Đất. Với căn hộ, "1 tầng" đúng về bản chất (một căn là một mặt sàn), không phải một phép đoán. Với đất trống, 1 là quy ước. Không tạo cờ riêng vì giá trị điền trùng với giá trị đúng về ngữ nghĩa.

### 2.3. `so_wc` — suy từ `so_phong_ngu`

Hệ số tương quan `r(so_wc, so_phong_ngu) = 0,727` — đủ chặt để suy. Lưu ý: chính vì quan hệ chặt này mà **`so_wc` sẽ bị loại khỏi tập đặc trưng** ở BT4 (trùng thông tin + đa cộng tuyến), nên chất lượng phép suy không ảnh hưởng tới mô hình.

### 2.4. `mat_tien_m`, `rong_hem_m` — mã `−1`, **cố ý không điền**

**Đây là quyết định quan trọng nhất trong nhóm xử lý thiếu.**

Tỷ lệ thiếu quá cao (78,3% và 88,2%) để điền bất kỳ giá trị nào — điền trung vị nghĩa là bịa ra một mặt tiền cho gần 5.800 tin. Quan trọng hơn: **việc không ghi tự nó là thông tin**. Nhà trong hẻm không có mặt tiền để khoe nên không ghi; nhà mặt tiền thì luôn ghi vì đó là điểm bán hàng.

Mục 5.4 của notebook kiểm chứng trực tiếp giả thuyết này:
- Nhóm **có ghi** mặt tiền đắt hơn nhóm `−1` khoảng **7%** (115,4 so với 107,7 tr/m²) → *việc có ghi* mang thông tin.
- Nhưng trong nội bộ nhóm có số đo, Spearman(mặt tiền, đơn giá) = **−0,20** → *con số* gần như không mang thêm thông tin, vì mặt tiền rộng đi kèm diện tích lớn mà đơn giá/m² lại giảm theo diện tích.

**Kết luận:** giữ cờ `co_tt_mat_tien`, bỏ cột số khi chạy hồi quy tuyến tính (để nguyên `−1` thì mô hình tuyến tính sẽ diễn giải là "mặt tiền âm 1 mét").

**Một lỗi thiết kế biến cần ghi nhận:** mã `−1` của `rong_hem_m` gộp hai trường hợp khác hẳn nhau — **4.286 tin không ở trong hẻm** và **2.272 tin ở trong hẻm nhưng không ghi độ rộng**. Một giá trị đại diện cho hai ý nghĩa là không chuẩn. Ở BT4 nên tách thành hai cờ, hoặc chỉ dùng `la_hem` kết hợp một cờ `co_tt_rong_hem`.

### 2.5. `phuong`, `ten_duong` — `'Khong_ro'` thành một mức riêng

Thiếu ở đây **không ngẫu nhiên (MNAR)**: môi giới thường giấu địa chỉ chi tiết để giữ khách phải gọi điện. Vì vậy không điền mode (sẽ dồn sai vào một phường đông tin) mà gán thành một mức riêng, giữ lại chính tín hiệu "tin này giấu địa chỉ".

Hai cột này **không dùng làm đặc trưng** ở BT4: `phuong` có 67,3% là `Khong_ro`, `ten_duong` có 1.332 giá trị khác nhau. Nếu muốn dùng `ten_duong` thì bắt buộc target-encoding theo K-fold *trong tập train*, nếu không sẽ rò rỉ nhãn.

---

## 3. Xử lý ngoại lai

### 3.1. Lọc hai tầng theo đơn giá (triệu VNĐ/m²)

**Tầng 1 — chặn cứng 15–450 tr/m².**
- Dưới 15: gần như chắc chắn là lỗi đơn vị. Người đăng gõ "3,5" với ý "3,5 tỷ" nhưng hệ thống đọc là 3,5 triệu, cho ra đơn giá vài triệu/m² — bất khả thi ở TP.HCM.
- Trên 450: tin câu view hoặc bất động sản thương mại (mặt bằng kinh doanh phố cổ) không cùng thị trường với nhà ở.

**Tầng 2 — IQR × 1,5 *trong từng quận*, không dùng một ngưỡng chung.**

Đây là điểm cốt lõi. Đơn giá trung vị **Quận 5 là 208,1 tr/m²** còn **Hóc Môn là 46,0 tr/m²** — chênh **4,5 lần**. Nếu lọc bằng một ngưỡng IQR chung cho toàn thành phố thì:
- nhà bình thường ở Quận 5 sẽ bị xem là "ngoại lai đắt" và bị xóa oan;
- tin ảo ở Hóc Môn vẫn lọt vì vẫn thấp hơn ngưỡng chung.

Lọc trong từng quận giữ đúng tinh thần "ngoại lai so với mặt bằng của chính khu vực đó". → **loại 420 tin**.

### 3.2. Diện tích — chặn 15–500 m²

Dưới 15 m² không phải nhà ở hợp pháp để bán; trên 500 m² là dự án/khu đất lớn, khác thị trường nhà ở dân cư. → **loại 7 tin**.

### 3.3. Số phòng ngủ — **winsorize ở 10** thay vì xóa

Mọi tin ≥10 PN bị kéo về đúng 10, không bị xóa, vì tin nhiều phòng thường là nhà trọ/CCMN — vẫn là giao dịch thật, chỉ là phân khúc khác.

**Hệ quả phải ghi nhận (và là một hạn chế của bước làm sạch):** nhóm "10 PN" có **171 tin, nhiều hơn tổng nhóm 8 PN và 9 PN cộng lại (100 tin)** — một phân phối không thể xảy ra tự nhiên. Nhóm này phải đọc là **"10 phòng trở lên"**, không phải "đúng 10 phòng". Khi diễn giải hệ số mô hình ở BT4 phải nhắc lại điều này, nếu không sẽ kết luận sai rằng "nhà 10 phòng đặc biệt đắt".

### 3.4. **Quyết định KHÔNG cắt đuôi giá cao**

Giá bán max là 44 tỷ, gấp 3,5 lần Q3 — theo quy tắc IQR thì đây là ngoại lai. Nhóm vẫn giữ, vì:

1. Sau log-transform, skewness giảm từ **1,765 xuống 0,091**; các tin 40+ tỷ nằm gọn trong thân phân phối chứ không còn là điểm cực đoan tách biệt (mục 3.1).
2. Chúng nhất quán với loại hình và vị trí: biệt thự ở Quận 2, Quận 7 — tức là phân khúc cao cấp thật, không phải lỗi nhập liệu.
3. Xóa chúng sẽ làm mô hình mù hoàn toàn với phân khúc cao cấp, trong khi đây lại là phân khúc có giá trị thương mại lớn nhất.

Thay vì xóa, nhóm xử lý bằng **log-transform biến mục tiêu** — một phép biến đổi, không phải một phép loại bỏ dữ liệu.

---

## 4. Những gì xử lý thiếu / ngoại lai **không thể** khắc phục

Phần này quyết định cách đọc kết quả mô hình ở BT4.

**4.1. Giá niêm yết là giá chào đã làm tròn.** 7.436 tin chỉ có **831 mức giá khác nhau**; **77,6%** là bội số của 100 triệu, **17,9%** là số tròn tỷ, riêng mức 7,5 tỷ xuất hiện 115 lần (mục 3.2). Người bán niêm yết số tròn để mở biên thương lượng; giá chốt thật thấp hơn một khoảng không nằm trong dữ liệu. **Không có kỹ thuật làm sạch nào khử được nhiễu này** — nó là bản chất của nguồn dữ liệu tin đăng. Hệ quả: R² có trần trên; R² > 0,9 phải bị nghi là rò rỉ nhãn chứ không phải thành tích.

**4.2. Mọi cờ đều do người đăng tự khai, không kiểm chứng.** Bằng chứng mạnh nhất: `co_so_hong` mang dấu **âm** sau khi khống chế loại hình (−8,8% trong nhóm Nhà riêng, mục 3.9). Biến này đo *cách viết tin quảng cáo* — người bán nhà vùng ven nhấn mạnh "sổ hồng riêng" để bù điểm yếu vị trí — chứ không đo tình trạng pháp lý thật.

**4.3. Thiếu ba nhóm biến có sức giải thích lớn:** thời gian đăng (không tách được xu hướng thị trường), tọa độ (không tính được khoảng cách tới trung tâm/tiện ích), chất lượng công trình (năm xây, hướng, tình trạng thật).

**4.4. Lệch hệ thống giữa hai nguồn.** Sau khi khống chế quận × loại hình, batdongsan vẫn thấp hơn CafeLand **6,4%** (mục 3.11) → bắt buộc đưa `nguon_du_lieu` vào mô hình như biến kiểm soát, nếu không hệ số quận và loại hình sẽ hấp thụ nhầm độ lệch này.

---

## 5. Bảng tổng hợp quyết định

| Vấn đề | Quyết định | Số dòng ảnh hưởng | Lý do một dòng |
|---|---|---|---|
| `so_phong_ngu` thiếu | Trung vị theo `loai_hinh` + cờ | 1.950 (26,2%) | Phụ thuộc mạnh vào loại hình; giữ cờ để lọc lại |
| `so_tang` thiếu | Điền 1 | — | Đúng bản chất với căn hộ và đất |
| `so_wc` thiếu | Suy từ `so_phong_ngu` | — | r = 0,727; biến này sẽ bị loại khỏi mô hình |
| `mat_tien_m` thiếu | Mã `−1` + cờ, **không điền** | 5.823 (78,3%) | Việc không ghi là thông tin thật |
| `rong_hem_m` thiếu | Mã `−1` + cờ, **không điền** | 6.558 (88,2%) | Như trên; lưu ý `−1` đang gộp 2 nghĩa |
| `phuong`, `ten_duong` thiếu | `'Khong_ro'` thành mức riêng | 67,3% / 38,8% | Thiếu không ngẫu nhiên (MNAR) |
| Đơn giá ngoại lai | Chặn cứng 15–450 + IQR×1,5 **theo quận** | −420 tin | Quận 5 đắt gấp 4,5 lần Hóc Môn, ngưỡng chung sẽ xóa oan |
| Diện tích ngoại lai | Chặn 15–500 m² | −7 tin | Ngoài dải này là dự án hoặc lỗi nhập |
| Số phòng ngủ cực đoan | Winsorize về 10 | 171 tin dồn vào nhóm 10 | Vẫn là giao dịch thật; nhóm 10 phải đọc là "≥10" |
| Giá bán cao (tới 44 tỷ) | **Giữ nguyên**, dùng `log_gia_ban` | 0 | Sau log không còn cực đoan; là phân khúc cao cấp thật |

---

## 6. Tệp dữ liệu nộp kèm

`df_bt3.csv` — 7.436 dòng × 30 cột = `df_clean.csv` cộng ba cột tạo ở BT3:

| Cột mới | Ý nghĩa | Lưu ý sử dụng |
|---|---|---|
| `don_gia` | `gia_ban / dien_tich_m2` (triệu VNĐ/m²) | **Chỉ dùng cho EDA và gom vùng. Tuyệt đối không đưa vào mô hình — rò rỉ nhãn trực tiếp.** |
| `vung_gia` | 20 quận gom thành 4 vùng theo tứ phân vị đơn giá trung vị quận | Bảng ánh xạ quận → vùng phải được tính lại **chỉ trên tập train** ở BT4 |
| `loai_hinh_gop` | `loai_hinh` sau khi gộp Shophouse (24 tin) vào `Khác` | Dùng cột này để one-hot thay cho `loai_hinh` |
