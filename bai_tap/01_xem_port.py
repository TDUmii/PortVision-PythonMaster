"""Bai 1 - Quan sat 15 socket dang su dung."""
import psutil

danhSach = psutil.net_connections(kind="inet")

for ketNoi in danhSach[:15]:
    print("PID:", ketNoi.pid)
    print("Local:", ketNoi.laddr)
    print("Remote:", ketNoi.raddr or "Chua ket noi")
    print("Trang thai:", ketNoi.status)
    print("-" * 40)

print("Tong so socket:", len(danhSach))
