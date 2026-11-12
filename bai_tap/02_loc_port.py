"""Bai 2 - Loc ket noi theo port va thong ke trang thai."""
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
