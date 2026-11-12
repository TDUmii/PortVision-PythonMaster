"""Bai 3 - Cua so danh sach port va nut lam moi, khong can class."""
import psutil
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
)

app = QApplication([])
cuaSo = QWidget()
cuaSo.setWindowTitle("Port Monitor - Bai 3")
cuaSo.resize(720, 480)

boCuc = QVBoxLayout(cuaSo)
tieuDe = QLabel("DANH SACH PORT TREN MAY")
nutLamMoi = QPushButton("Lam moi")
bangPort = QTableWidget(0, 3)
bangPort.setHorizontalHeaderLabels(["PID", "Local port", "Trang thai"])

boCuc.addWidget(tieuDe)
boCuc.addWidget(nutLamMoi)
boCuc.addWidget(bangPort)


def lamMoi():
    danhSach = psutil.net_connections(kind="inet")[:50]
    bangPort.setRowCount(len(danhSach))
    for dong, ketNoi in enumerate(danhSach):
        port = ketNoi.laddr.port if ketNoi.laddr else ""
        bangPort.setItem(dong, 0, QTableWidgetItem(str(ketNoi.pid or "")))
        bangPort.setItem(dong, 1, QTableWidgetItem(str(port)))
        bangPort.setItem(dong, 2, QTableWidgetItem(str(ketNoi.status)))


nutLamMoi.clicked.connect(lamMoi)
lamMoi()
cuaSo.show()
app.exec()
