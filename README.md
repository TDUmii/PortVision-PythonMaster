# PortVision – Visual Port Manager

Ứng dụng Python quản lý và trực quan hóa **các socket TCP/UDP trên máy đang chạy**: máy tính → tiến trình → cổng cục bộ → địa chỉ đích. Dự án giáo dục, không can thiệp hệ thống.

## Chạy ứng dụng

Yêu cầu Python 3.10+ và Windows, macOS hoặc Linux.

```bash
python -m pip install -r requirements.txt
python app.py
```

Nếu trên macOS không thấy đầy đủ tiến trình hoặc socket, đó có thể là giới hạn quyền truy cập của hệ điều hành. Không bắt buộc học viên cấp quyền quản trị.

## Chức năng

- Network Map: click node để xem chi tiết, phóng to/thu nhỏ, giới hạn tối đa 8 ứng dụng và 3 kết nối/ứng dụng để giữ sơ đồ gọn.
- Port Explorer: tìm kiếm tiến trình, PID, địa chỉ IP và port, lọc theo trạng thái/giao thức/địa chỉ remote.
- Overview: thống kê các socket và các tiến trình nổi bật.
- History: lưu snapshot trên máy, so sánh với lần quét hiện tại.
- Export CSV: xuất những dòng đang lọc (chứa địa chỉ thật, giữ riêng tư).
- Demo data: dữ liệu **mô phỏng**, không phải hoạt động thật của máy.

**Lưu ý:** LISTEN là socket chờ kết nối, ESTABLISHED là kết nối đang thiết lập; local port cao không đồng nghĩa nguy hiểm. Không phải mọi kết nối đến Internet đều có thể xác định website từ địa chỉ IP. Đồ thị là **sơ đồ quan hệ socket**, không phải sơ đồ vật lý của LAN.

## Cấu trúc

- `app.py`: giao diện chính và các nút bấm.
- `core.py`: quét port, lọc dữ liệu đầu vào, snapshot và CSV.
- `network_map.py`: đồ họa node có sẵn cho học viên.
- `theme.qss`: giao diện tối có sẵn cho học viên.
- `bai_tap/`: 3 bài thực hành ngắn, làm theo từng bước.
- `GIAO_TRINH.md`: giáo án 2 buổi đầy đủ.
- `test_core.py`: kiểm tra logic.

## Bảo vệ thông tin

Ứng dụng **không gửi dữ liệu mạng đi đâu**, không gọi API ngoài, không đóng port, không chặn kết nối. Snapshot lưu trong `local_data/`, CSV do người dùng chọn nơi lưu. Các file đó cùng ảnh chụp, token, `.env`, file build đều nằm trong `.gitignore` và không được đưa lên GitHub. Không tải lên ảnh chụp phiên làm việc có IP hoặc tên máy thật.

## Kiểm thử

```bash
python -m unittest -v test_core.py
```
