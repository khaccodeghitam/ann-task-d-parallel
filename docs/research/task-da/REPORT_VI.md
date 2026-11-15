# Kết quả triển khai Task D × Task A — 15/11/2026

Đã triển khai phần chuẩn bị P0, loader/audit/tests P1 và baseline một worker
để dùng cho smoke correctness. **Chưa đóng được cổng P0/P1 trên dữ liệu thật;
chưa chạy benchmark, chưa có kết luận về cải tiến hay tính mới.**

## Đã làm

- Đọc hai repo, ba nhánh Task A đúng tên và nhánh E3 của Task D; ghim commit SHA
  và SHA256 của các file nguồn liên quan.
- Đọc đề xuất từ Drive và bản cùng tên trong Downloads (hash trùng nhau).
  Không tìm thấy bản mang đúng hậu tố `(1)` nên chưa xác nhận hai bản đó giống nhau.
- Đọc các tab kết quả, Factor, W(n) và protocol của Google Sheets; lưu trích đoạn
  có nguồn, phân biệt kết quả Task A với thí nghiệm mới của Task D.
- Tạo manifest cho MS-Turing-1M và 9 graph OFF A0/A1/A3; ghi rõ hash do nguồn báo
  cáo, đường dẫn và provenance còn thiếu. Thêm protocol tiền đăng ký và cổng dừng.
- Cài loader trực tiếp PiPNN/NSG, chuyển định dạng giữ nguyên ID/hướng/thứ tự cạnh,
  audit cấu trúc/reachability, digest từng node và kiểm tra round trip đúng byte.
- Cài common baseline một worker, counters ON/OFF, đọc fbin, smoke tối đa 32 query,
  đánh giá Recall@k theo GT dạng IDs block rồi distances block.
- Thêm kiểm thử Release, oracle L2 độc lập, kiểm tra lỗi bộ nhớ và kiểm tra tự động
  trên GitHub. Toàn bộ mã mới nằm ở nhánh nghiên cứu riêng.

## Quyết định theo bằng chứng

| Phần | Trạng thái | Căn cứ |
|---|---|---|
| Audit source và kiểm thử graph tổng hợp | PASS | 18 kiểm thử mục tiêu; Release và ASan/UBSan/LeakSanitizer qua |
| Regression repo | PASS | 509 tests, không skip |
| P0 đầy đủ | HOLD | Chưa có graph/base/query/GT, raw receipts và host benchmark đủ điều kiện |
| P1 đầy đủ | HOLD | Chưa audit A0/A3 thật, chưa smoke Recall trên MS-Turing-1M |
| P2 | Một phần / HOLD | Có baseline một worker; chưa có multi-walker 2/4 worker |
| P3/P4 | HOLD | Chưa đủ điều kiện chạy phép đo tương tác graph × worker |
| P5/P6 | Chưa mở | Chưa có bottleneck hay bằng chứng để xây scheduler mới |
| Đổi tên PiPNN thành NSG rồi đưa vào loader cũ | NO-GO cho cách làm này | Layout và entry point khác nhau |

Chưa có NO-GO khoa học cho hướng A×D. Thiếu dữ liệu chỉ dẫn tới HOLD.
PASS trong Google Sheets là trạng thái nguồn báo cáo; chưa được tái kiểm chứng
từ các graph/log gốc ở phiên này. Các counters W_P/W_A/W_L là BUILD, không phải
SEARCH. QPS Task A là so sánh theo ngưỡng Recall, chưa phải Recall khớp chính xác.

## Việc cần tiếp theo

Ưu tiên nhận đúng graph A0/A1/A3 R1–R3 cùng bộ vector/query/GT đã ghim hash và
receipt build/source/seed. Chạy read-only preflight, audit từng graph và smoke
P1 trước; sau đó mới chốt thiết kế multi-walker và pilot A0/A3 × 1/4 workers.
Không thay graph, không dựng lại graph rồi gán nhãn như artifact lịch sử.

Chi tiết và lệnh tái lập ở [README](README.md),
[audit nguồn](SOURCE_AUDIT.md), [protocol](PRE_REGISTRATION.md) và
[validation](VALIDATION.md).
