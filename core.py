"""Phan xu ly port, khong phu thuoc giao dien."""
import csv
import json
import socket
from datetime import datetime
from pathlib import Path

import psutil

DATA_DIR = Path(__file__).parent / "local_data"


def dia_chi(addr):
    if not addr:
        return "", ""
    return str(addr.ip), str(addr.port)


def quet_port():
    """Doc ket noi cua may hien tai. Khong quet may khac."""
    ket_qua = []
    ten_da_doc = {}
    try:
        ket_noi = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, OSError) as loi:
        raise RuntimeError("Khong doc duoc ket noi. Thu chay voi quyen phu hop.") from loi

    for item in ket_noi:
        pid = item.pid
        if pid not in ten_da_doc:
            try:
                ten_da_doc[pid] = psutil.Process(pid).name() if pid is not None else "System / Unknown"
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                ten_da_doc[pid] = f"PID {pid}" if pid else "System / Unknown"

        ip_local, port_local = dia_chi(item.laddr)
        ip_remote, port_remote = dia_chi(item.raddr)
        ket_qua.append({
            "process": ten_da_doc[pid],
            "pid": pid,
            "protocol": "TCP" if item.type == socket.SOCK_STREAM else "UDP",
            "local_ip": ip_local,
            "local_port": port_local,
            "remote_ip": ip_remote,
            "remote_port": port_remote,
            "status": str(item.status),
        })
    return sorted(ket_qua, key=lambda x: (x["process"].lower(), x["local_port"]))


def du_lieu_demo():
    """Du lieu gia lap, tuyet doi khong phai ket noi that."""
    mau = [
        ("chrome.exe", 4400, 51822, "142.250.4.100", 443, "ESTABLISHED"),
        ("chrome.exe", 4400, 51825, "104.18.1.2", 443, "ESTABLISHED"),
        ("chrome.exe", 4400, 51830, "151.101.1.69", 443, "TIME_WAIT"),
        ("python.exe", 7212, 5000, "", "", "LISTEN"),
        ("python.exe", 7212, 8000, "", "", "LISTEN"),
        ("Code.exe", 6308, 52133, "140.82.112.3", 443, "ESTABLISHED"),
        ("Code.exe", 6308, 52144, "20.42.65.90", 443, "ESTABLISHED"),
        ("Discord.exe", 8104, 53321, "162.159.130.234", 443, "ESTABLISHED"),
        ("Spotify.exe", 9120, 53455, "35.186.224.25", 443, "ESTABLISHED"),
        ("nginx.exe", 1002, 8080, "", "", "LISTEN"),
        ("postgres.exe", 4202, 5432, "", "", "LISTEN"),
        ("python.exe", 7212, 55001, "127.0.0.1", 5432, "ESTABLISHED"),
    ]
    return [
        dict(process=ten, pid=pid, protocol="TCP", local_ip="127.0.0.1" if not host else "192.168.1.20",
             local_port=port, remote_ip=host, remote_port=dich, status=trang_thai)
        for ten, pid, port, host, dich, trang_thai in mau
    ]


def ma_ket_noi(item):
    """Khong dua trang thai vao khoa de phat hien thay doi trang thai."""
    return "|".join(str(item[k]) for k in (
        "pid", "protocol", "local_ip", "local_port", "remote_ip", "remote_port"
    ))


def so_sanh(truoc, sau):
    a = {ma_ket_noi(item): item for item in truoc}
    b = {ma_ket_noi(item): item for item in sau}
    moi = [b[k] for k in b.keys() - a.keys()]
    mat = [a[k] for k in a.keys() - b.keys()]
    doi = [(a[k], b[k]) for k in a.keys() & b.keys() if a[k]["status"] != b[k]["status"]]
    return moi, mat, doi


def luu_snapshot(ket_noi, demo=False):
    DATA_DIR.mkdir(exist_ok=True)
    du_lieu = {"created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "demo": demo, "connections": ket_noi}
    ten_file = datetime.now().strftime("snapshot_%Y%m%d_%H%M%S_%f.json")
    tep = DATA_DIR / ten_file
    tep.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=2), encoding="utf-8")
    return tep


def danh_sach_snapshot():
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("snapshot_*.json"), reverse=True)


def doc_snapshot(tep):
    return json.loads(Path(tep).read_text(encoding="utf-8"))


def xuat_csv(du_lieu, tep):
    cot = ["process", "pid", "protocol", "local_ip", "local_port",
           "remote_ip", "remote_port", "status"]
    with open(tep, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=cot)
        writer.writeheader()
        writer.writerows(du_lieu)
