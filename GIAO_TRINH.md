# PYTHON MASTER – PORTVISION
## Giáo trình 2 buổi: Ứng dụng quản lý port và sơ đồ kết nối

**Đối tượng:** học viên trưởng thành đã biết biến, vòng lặp, điều kiện, danh sách, hàm.
**Hình thức:** học online 1-1 / nhóm nhỏ, mỗi người thực hành trên máy riêng.
**Thời lượng:** 2 buổi × 120 phút (có thể rút xuống 90 phút/buổi bằng cách bỏ bài mở rộng).
**Sản phẩm:** PortVision có 4 màn hình, xem port thật, sơ đồ node, lọc, snapshot và xuất CSV.

### Mục tiêu sau khóa học
- Phân biệt **process** (chương trình), **PID** (mã tiến trình), **socket**, **local port**, **remote endpoint**.
- Biết dùng thư viện `psutil` đọc các kết nối **trên chính máy đang chạy**.
- Dùng `for`, `if`, `list`, `dict`, `function` để phân tích dữ liệu.
- Tạo UI PySide6 có nút bấm, bảng và thanh tìm kiếm.
- Hiểu cách chuyển dữ liệu kỹ thuật thành sơ đồ đồ họa bằng cách **tái sử dụng file có sẵn**.
- Biết lưu snapshot / export CSV mà không làm lộ dữ liệu mạng cá nhân.

## Chuẩn bị trước lớp (10 phút, giáo viên hướng dẫn)
1. Mở VS Code, PyCharm hoặc Antigravity, chọn thư mục `PortVision-PythonMaster`.
2. Mở Terminal tại thư mục vừa chọn.
3. Chạy:
   ```powershell
   python --version
   python -m pip install -r requirements.txt
   python -m unittest -v test_core.py
   ```
4. Kiểm tra có các file: `app.py`, `core.py`, `network_map.py`, `theme.qss`, `bai_tap/`.
5. **Không cần** kết nối LAN giữa giáo viên và học viên. Mỗi học viên quét **máy của chính mình**.
6. Không yêu cầu học viên chia sẻ toàn màn hình nếu có IP riêng tư; ưu tiên chế độ Demo data khi trình chiếu.

**Giải thích dễ hiểu cho học viên:**
- Máy tính là một tòa nhà; **process** là các phòng làm việc.
- **Port** là số cửa giao tiếp của tiến trình, không phải dây mạng vật lý.
- **LISTEN**: chương trình đang chờ yêu cầu đến. **ESTABLISHED**: kết nối TCP đang hoạt động.
- Một ứng dụng có thể dùng **nhiều port**; cổng cao không đồng nghĩa virus.
- **Remote IP** không chắc là một website cụ thể. Đừng đưa kết luận bảo mật chỉ từ số port.

---

# BUỔI 1 – ĐỌC PORT VÀ XÂY GIAO DIỆN CƠ BẢN (120 phút)

## Phần 1 (0–15 phút): Quan sát trước khi viết code
Giáo viên mở trình duyệt, đóng/mở tab, giải thích socket tăng/giảm theo hoạt động.
Cho học viên dự đoán: máy có bao nhiêu port LISTEN, có bao nhiêu kết nối ESTABLISHED?
Chưa cần giải thích sâu về TCP 3-way handshake.

## Phần 2 (15–35 phút): Bài 1 – Lấy danh sách socket
**Tạo file:** `bai_tap/01_xem_port.py`

```python
import psutil

danhSach = psutil.net_connections(kind="inet")

for ketNoi in danhSach[:15]:
    print("PID:", ketNoi.pid)
    print("Local:", ketNoi.laddr)
    print("Remote:", ketNoi.raddr or "Chua ket noi")
    print("Trang thai:", ketNoi.status)
    print("-" * 40)

print("Tong so socket:", len(danhSach))
```

**Giải thích từng dòng:**
- `import psutil`: thư viện có sẵn để lấy số liệu hệ thống, không cần tự viết trình điều khiển.
- `net_connections(kind="inet")`: trả về danh sách socket IPv4/IPv6 dùng TCP/UDP.
- `[:15]`: chỉ lấy 15 dòng để màn hình không quá dài.
- `laddr` / `raddr`: địa chỉ trên máy / địa chỉ bên kia; có thể không có `raddr`.
- `pid`: số định danh tiến trình; một số bản ghi hệ điều hành có thể không cho xem PID.
- `status`: trạng thái socket (UDP thường không có ESTABLISHED như TCP).

**Chạy thử:** `python bai_tap/01_xem_port.py`
**Bài tập nhanh:** đổi 15 thành 30, thử đếm số dòng ESTABLISHED bằng mắt.

## Phần 3 (35–55 phút): Bài 2 – Lọc port bằng if và for
**Tạo file:** `bai_tap/02_loc_port.py`

```python
import psutil

danhSach = psutil.net_connections(kind="inet")
portCanTim = input("Nhap port muon tim (Enter de xem tat ca): ").strip()
soListen = 0
soEstablished = 0

for ketNoi in danhSach:
    if ketNoi.status == "LISTEN":
        soListen += 1
    if ketNoi.status == "ESTABLISHED":
        soEstablished += 1

    if not ketNoi.laddr:
        continue
    if portCanTim and str(ketNoi.laddr.port) != portCanTim:
        continue

    print(f"PID {ketNoi.pid} | Local port: {ketNoi.laddr.port} | {ketNoi.status}")

print("LISTEN:", soListen)
print("ESTABLISHED:", soEstablished)
```

**Điểm mới so với bài 1:** nhập port, so sánh chuỗi và sử dụng `continue` để bỏ qua dòng không khớp.
**Thử nghiệm:** gõ `443`, `5000`, `8000`, sau đó Enter trống. Một port không có kết quả không phải lỗi chương trình.
**Nâng cao tự chọn:** đổi thành chỉ in các kết nối có trạng thái LISTEN.

## Phần 4 (55–65 phút): Nghỉ và giải đáp
Hỏi học viên: cùng một port có thể xuất hiện trên nhiều IP local không? Vì sao?
Câu trả lời: có thể, tùy địa chỉ bind, giao thức và cách hệ điều hành quản lý socket.

## Phần 5 (65–100 phút): Bài 3 – GUI PySide6 không dùng class
**Tạo file:** `bai_tap/03_gui_don_gian.py`.

Từ code đã được cung cấp trong file, học viên làm theo **4 bước** sau:

**Bước A – Tạo cửa sổ và layout:**
```python
app = QApplication([])
cuaSo = QWidget()
cuaSo.setWindowTitle("Port Monitor - Bai 3")
cuaSo.resize(720, 480)
boCuc = QVBoxLayout(cuaSo)
```
Giáo viên giải thích `QWidget` là cửa sổ, `QVBoxLayout` xếp các thành phần từ trên xuống.

**Bước B – Thêm tiêu đề, nút và bảng:**
```python
tieuDe = QLabel("DANH SACH PORT TREN MAY")
nutLamMoi = QPushButton("Lam moi")
bangPort = QTableWidget(0, 3)
bangPort.setHorizontalHeaderLabels(["PID", "Local port", "Trang thai"])
boCuc.addWidget(tieuDe)
boCuc.addWidget(nutLamMoi)
boCuc.addWidget(bangPort)
```

**Bước C – Hàm lấy dữ liệu thật và đưa vào bảng:**
```python
def lamMoi():
    danhSach = psutil.net_connections(kind="inet")[:50]
    bangPort.setRowCount(len(danhSach))
    for dong, ketNoi in enumerate(danhSach):
        port = ketNoi.laddr.port if ketNoi.laddr else ""
        bangPort.setItem(dong, 0, QTableWidgetItem(str(ketNoi.pid or "")))
        bangPort.setItem(dong, 1, QTableWidgetItem(str(port)))
        bangPort.setItem(dong, 2, QTableWidgetItem(str(ketNoi.status)))
```

**Bước D – Gắn nút và chạy:**
```python
nutLamMoi.clicked.connect(lamMoi)
lamMoi()
cuaSo.show()
app.exec()
```
**Nhớ import:** `psutil` và các lớp Qt nằm ngay đầu file mẫu đã cung cấp.

**Chạy thử:** `python bai_tap/03_gui_don_gian.py`
**Đầu ra:** cửa sổ có bảng 50 socket đầu và nút Làm mới; không cần viết bất kỳ class nào.

## Phần 6 (100–120 phút): Thử nghiệm và tổng kết buổi 1
1. Mở app bài 3, xem số port trước và sau khi mở thêm một phần mềm.
2. Bấm Làm mới; xem trạng thái thay đổi.
3. Đổi giới hạn 50 thành 20; giải thích `[:20]`.
4. Bài tập về nhà: thêm 1 cột `Remote IP`, tham khảo `ketNoi.raddr`.

**Checklist đạt:** cài được `psutil`, in được socket, lọc theo port, app mini mở và cập nhật được.

---

# BUỔI 2 – PORTVISION, SƠ ĐỒ NODE VÀ SNAPSHOT (120 phút)

## Phần 1 (0–15 phút): Ôn tập
Học viên tự trả lời: `process` khác `port` thế nào? Chương trình có thể LISTEN trên 127.0.0.1 không?
Mở lại 3 bài tập buổi trước rồi mở `app.py` để giới thiệu sản phẩm cuối.

## Phần 2 (15–35 phút): Tách xử lý dữ liệu ra `core.py`
Giải thích **vì sao tách file**: `core.py` chứa logic, `app.py` chứa nút bấm/UI.
Học viên xem hàm `quet_port()` trong `core.py`:

```python
import psutil

def quet_port_don_gian():
    ketQua = []
    for item in psutil.net_connections(kind="inet"):
        if item.laddr:
            ketQua.append({
                "pid": item.pid,
                "port": item.laddr.port,
                "status": item.status,
            })
    return ketQua

print(quet_port_don_gian()[:3])
```

Đây là **mẫu ngắn để hiểu tư duy**, không thay thế `quet_port()` hoàn chỉnh: bản hoàn chỉnh lấy tên process, TCP/UDP, IP local và remote, đồng thời xử lý quyền truy cập.
Học viên chỉ cần đọc hiểu phần `for`, `if`, `append`, `return`; giáo viên cung cấp sẵn phần xử lý lỗi `AccessDenied`, `NoSuchProcess`.

## Phần 3 (35–55 phút): Ghép giao diện hoàn chỉnh
Giáo viên **cho sẵn** `app.py`, `network_map.py` và `theme.qss`; học viên không phải gõ lại hệ thống đồ họa Qt.

**Thử:** `python app.py`

Các khối để học viên nhận diện trong `app.py`:
- `__init__`: tạo cửa sổ, sidebar, thanh tìm kiếm, 4 màn hình.
- `quet()`: gọi `quet_port()` và cập nhật dữ liệu thực tế.
- `loc()`: duyệt danh sách, so khớp từ khóa và các hộp chọn.
- `cap_nhat()`: cập nhật card, bảng và sơ đồ.
- `chon_node()`: hiển thị chi tiết khi nhấn lên một node.
- `luu_anh()`, `so_sanh_anh()`, `xuat()`: lưu / so sánh / export.

**Thực hành tương tác:** bật Demo data → xem sơ đồ → bấm node `python.exe` → xem port 5000 → chọn node remote → zoom +/-.

## Phần 4 (55–65 phút): Nghỉ

## Phần 5 (65–85 phút): Bộ lọc và sơ đồ mạng
Vẽ trên bảng một kết nối:
`THIS DEVICE → chrome.exe → TCP:51822 → 142.250.4.100:443`.

Mô hình dữ liệu mỗi kết nối **chỉ là một dict**:
```python
ketNoi = {
    "process": "chrome.exe",
    "pid": 4400,
    "protocol": "TCP",
    "local_ip": "192.168.1.20",
    "local_port": 51822,
    "remote_ip": "142.250.4.100",
    "remote_port": 443,
    "status": "ESTABLISHED",
}
```

`network_map.py` **đã vẽ sẵn**, học viên chỉ cần hiểu chương trình đi qua danh sách dict rồi đặt các node và đường nối. Chỉ hiển thị 8 process / 3 connection mỗi process để không bị quá rối; **Port Explorer vẫn chứa toàn bộ dòng đã lọc**.

**Thực nghiệm:** tìm `python`, lọc `TCP`, chọn `Listening only`; khi không có node remote là đúng vì socket chưa có peer cụ thể.

## Phần 6 (85–105 phút): Snapshot và so sánh
Học viên làm **theo thứ tự**:
1. Bỏ Demo data để dùng dữ liệu thật.
2. Bấm **Save snapshot** (lưu vào `local_data/`, chỉ trên máy).
3. Mở hoặc đóng một chương trình bình thường, ví dụ trình duyệt.
4. Bấm **Scan now**.
5. Chọn **History** → chọn snapshot cũ → **Compare selected with current**.
6. Quan sát các nhóm `NEW`, `REMOVED`, `STATUS CHANGES`.

**Giải thích:** snapshot là chụp danh sách socket ở một thời điểm, không lưu mật khẩu, không chặn chương trình, không giám sát gói tin.
Một vài kết nối tồn tại rất ngắn nên `NEW`/`REMOVED` giữa hai lần quét là bình thường.
So sánh Demo và Live bị chặn để tránh hiểu sai kết quả.

## Phần 7 (105–115 phút): Export CSV và an toàn dữ liệu
Chọn `Port Explorer`, lọc `LISTEN`, bấm **Export CSV**, mở CSV bằng bảng tính.

Cảnh báo: ảnh chụp, IP thật, port, PID, tên process có thể tiết lộ môi trường cá nhân; **không gửi những dữ liệu này lên GitHub**. Dự án có `.gitignore` loại trừ CSV, ảnh chụp, snapshot và file môi trường.

## Phần 8 (115–120 phút): Mini challenge
Yêu cầu học viên hoàn thành **2 trong 4 nhiệm vụ**:
1. Tìm 1 process có hơn 1 socket.
2. Tìm 1 socket LISTEN và giải thích vì sao không có remote IP.
3. Chụp 2 snapshot và chỉ ra ít nhất 1 kết nối mới hoặc biến mất.
4. Đổi màu hiển thị LISTEN trong `network_map.py` từ vàng sang xanh nhạt.

**Checklist đạt:** app cuối chạy, có sơ đồ, lọc, click inspector, snapshot compare và xuất CSV.

---

# Phần giáo viên – Mốc phát triển và sửa lỗi thường gặp

| Mốc | Học viên thực sự viết | Giáo viên chuẩn bị |
|---|---|---|
| M1. Đọc port | `01_xem_port.py` | Cài thư viện |
| M2. Lọc port | `02_loc_port.py` | Giải thích local/remote |
| M3. GUI mini | `03_gui_don_gian.py` | PySide6 |
| M4. PortVision | Gọi hàm và sửa bộ lọc trong `app.py` | App hoàn chỉnh + stylesheet |
| M5. Sơ đồ | Sửa màu, số node hiển thị | `network_map.py` dựng sẵn |
| M6. History | Chạy kiểm tra / so sánh | Hàm snapshot và export dựng sẵn |

**Xử lý tình huống:**
- `ModuleNotFoundError: psutil` hoặc `PySide6`: chạy lại `python -m pip install -r requirements.txt` với đúng Python interpreter.
- App báo `AccessDenied`: hệ điều hành giới hạn một số socket; không yêu cầu học viên tự cấp quyền root/admin chỉ để hoàn thành bài; chuyển sang Demo data nếu cần.
- Không thấy port 5000: chưa có chương trình nào thực sự mở port đó. Trong Demo data luôn có mẫu.
- Port biến mất sau refresh: socket ngắn hạn; đây là điều bình thường.
- Mac xem được ít process hơn Windows: hạn chế quyền của macOS, không phải code khác biệt hoàn toàn.
- `TIME_WAIT` trong ảnh cũ nhưng không thấy ở lần mới: trạng thái chuyển nhanh; không phải virus.
- Không tìm được hostname từ IP: ứng dụng cố ý không gọi reverse DNS để đơn giản và giữ riêng tư.

## Chấm sản phẩm (100 điểm)
- 30 điểm: chạy app, quan sát được dữ liệu máy thật hoặc demo.
- 20 điểm: lọc đúng process/port/status và giải thích LISTEN – ESTABLISHED.
- 20 điểm: sử dụng sơ đồ node, nhận diện đường nối hợp lý.
- 20 điểm: snapshot và so sánh, xuất CSV.
- 10 điểm: trình bày rõ ràng, không làm lộ thông tin cá nhân.

## Bài mở rộng cho học viên khá
1. Thêm tùy chọn chỉ hiển thị những process có ít nhất 2 socket.
2. Thêm cột `Remote port` vào bài GUI mini.
3. Thêm nút **Only Python** bằng cách đặt từ khóa search thành `python`.
4. Thêm cảnh báo **port mới xuất hiện** dựa trên snapshot; **không** gán nhãn virus tự động.
5. Thêm tab **Favorites** lưu tên process yêu thích, không lưu IP cá nhân vào GitHub.

**Kết quả kỳ vọng:** một phần mềm có thật, có thể đem ra giới thiệu trong portfolio, nhưng vẫn nằm trong khả năng Python cơ bản–trung cấp. Tập trung dạy xử lý dữ liệu và thiết kế sản phẩm, phần đồ họa chuyên sâu có thể sử dụng file mẫu.
