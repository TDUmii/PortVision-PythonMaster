"""PortVision - Python Master. Chay: python app.py"""
from collections import Counter
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton,
    QStackedWidget, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout,
    QWidget, QHeaderView,
)

from core import (
    quet_port, du_lieu_demo, luu_snapshot, danh_sach_snapshot,
    doc_snapshot, so_sanh, xuat_csv,
)
from network_map import SoDoMang


def chu(text, size=12, mau="#e7eefb", dam=False):
    label = QLabel(text)
    label.setStyleSheet(f"font-size:{size}px;color:{mau};font-weight:{700 if dam else 400};")
    return label


def nut(text, callback, secondary=False):
    button = QPushButton(text)
    button.setCursor(Qt.PointingHandCursor)
    button.setProperty("secondary", secondary)
    button.clicked.connect(callback)
    return button


def khung(layout=None):
    w = QFrame()
    w.setObjectName("panel")
    if layout:
        w.setLayout(layout)
    return w


class PortVision(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortVision | Visual Port Manager")
        self.resize(1480, 875)
        self.setMinimumSize(1090, 690)
        self.toan_bo = []
        self.da_loc = []
        self.lan_quet = 0

        qss = Path(__file__).with_name("theme.qss")
        self.setStyleSheet(qss.read_text(encoding="utf-8"))

        vung_chinh = QWidget()
        self.setCentralWidget(vung_chinh)
        outer = QHBoxLayout(vung_chinh)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 1. Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 28, 18, 22)
        side.setSpacing(12)
        side.addWidget(chu("◈  PortVision", 21, "#f5f8ff", True))
        side.addWidget(chu("VISUAL PORT MANAGER", 9, "#71869e", True))
        side.addSpacing(34)
        self.nav = []
        for i, title in enumerate(["Overview", "Network Map", "Port Explorer", "History"]):
            b = nut(title, lambda checked=False, j=i: self.chuyen_tab(j), True)
            b.setObjectName("navButton")
            self.nav.append(b)
            side.addWidget(b)
        side.addStretch()
        side.addWidget(chu("LOCAL-ONLY MONITORING", 10, "#46c9b8", True))
        side.addWidget(chu("Read only  •  No port changes", 9, "#879bb2"))
        outer.addWidget(sidebar)

        # 2. Content area
        right = QWidget()
        content = QVBoxLayout(right)
        content.setContentsMargins(26, 22, 26, 22)
        content.setSpacing(17)
        outer.addWidget(right, 1)
        top = QHBoxLayout()
        heading = QVBoxLayout()
        heading.addWidget(chu("Network activity", 24, "#f3f7ff", True))
        heading.addWidget(chu("Visualize processes, ports and remote endpoints", 11, "#91a5bf"))
        top.addLayout(heading)
        top.addStretch()
        self.demo = QCheckBox("Demo data")
        self.demo.toggled.connect(self.quet)
        top.addWidget(self.demo)
        top.addWidget(nut("Save snapshot", self.luu_anh))
        top.addWidget(nut("Export CSV", self.xuat))
        top.addWidget(nut("↻  Scan now", self.quet))
        content.addLayout(top)

        stats = QHBoxLayout()
        self.thong_ke = []
        for t in ["SOCKET CONNECTIONS", "LISTENING", "ESTABLISHED", "REMOTE HOSTS"]:
            col = QVBoxLayout()
            col.setContentsMargins(16, 12, 16, 12)
            col.addWidget(chu(t, 10, "#8aa0b9", True))
            value = chu("0", 29, "#f2f7ff", True)
            self.thong_ke.append(value)
            col.addWidget(value)
            stats.addWidget(khung(col), 1)
        content.addLayout(stats)

        # 3. Toolbar filter
        filters = QHBoxLayout()
        self.tim = QLineEdit()
        self.tim.setPlaceholderText("Search app, IP, PID or port...")
        self.tim.textChanged.connect(self.loc)
        filters.addWidget(self.tim, 2)
        self.trang_thai = QComboBox()
        self.trang_thai.addItems(["All states", "LISTEN", "ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT", "Other"])
        self.trang_thai.currentIndexChanged.connect(self.loc)
        filters.addWidget(self.trang_thai, 1)
        self.giao_thuc = QComboBox()
        self.giao_thuc.addItems(["TCP + UDP", "TCP", "UDP"])
        self.giao_thuc.currentIndexChanged.connect(self.loc)
        filters.addWidget(self.giao_thuc, 1)
        self.pham_vi = QComboBox()
        self.pham_vi.addItems(["All endpoints", "With remote", "Listening only"])
        self.pham_vi.currentIndexChanged.connect(self.loc)
        filters.addWidget(self.pham_vi, 1)
        content.addLayout(filters)

        # 4. Four tabs
        self.pages = QStackedWidget()
        content.addWidget(self.pages, 1)
        self.lap_overview()
        self.lap_map()
        self.lap_table()
        self.lap_history()

        bottom = QHBoxLayout()
        self.trang = chu("Ready", 10, "#8aa0b9")
        bottom.addWidget(self.trang)
        bottom.addStretch()
        bottom.addWidget(chu("Local data stays on this computer", 10, "#71869e"))
        content.addLayout(bottom)

        self.chuyen_tab(1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.quet)
        self.timer.start(15000)
        self.quet()

    def lap_overview(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(15)
        lay.addWidget(chu("System overview", 18, "#f3f7ff", True))
        lay.addWidget(chu("Which apps own sockets? The counts below update when scanning.", 11, "#91a5bf"))
        block = QVBoxLayout()
        block.setContentsMargins(22, 20, 22, 20)
        block.addWidget(chu("TOP PROCESSES", 11, "#7c94b2", True))
        self.top_process = QTextEdit()
        self.top_process.setReadOnly(True)
        self.top_process.setMinimumHeight(240)
        block.addWidget(self.top_process)
        lay.addWidget(khung(block))
        guide = QVBoxLayout()
        guide.setContentsMargins(22, 20, 22, 20)
        guide.addWidget(chu("HOW TO EXPLORE", 11, "#7c94b2", True))
        guide.addWidget(chu("1. Open a browser, game, editor or local Python server."))
        guide.addWidget(chu("2. Click Scan now and switch to Network Map."))
        guide.addWidget(chu("3. Select a port, save a snapshot, then compare it later."))
        guide.addWidget(chu("A LISTEN socket waits for clients. An ESTABLISHED socket has an active peer.", 10, "#91a5bf"))
        lay.addWidget(khung(guide))
        lay.addStretch()
        self.pages.addWidget(page)

    def lap_map(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        bar = QHBoxLayout()
        bar.addWidget(chu("NETWORK MAP", 12, "#8da9c8", True))
        bar.addStretch()
        bar.addWidget(chu("Up to 8 processes · 3 ports each", 10, "#7890aa"))
        bar.addWidget(nut("−", lambda: self.so_do.zoom(0.83), True))
        bar.addWidget(nut("+", lambda: self.so_do.zoom(1.2), True))
        lay.addLayout(bar)
        middle = QHBoxLayout()
        middle.setSpacing(14)
        self.so_do = SoDoMang(self.chon_node)
        middle.addWidget(khung(self.wrap_map()), 1)
        detail_box = QVBoxLayout()
        detail_box.setContentsMargins(20, 20, 20, 20)
        detail_box.setSpacing(12)
        detail_box.addWidget(chu("INSPECTOR", 11, "#7e9db7", True))
        detail_box.addWidget(chu("Node details", 19, "#f3f7ff", True))
        self.chi_tiet = QTextEdit()
        self.chi_tiet.setReadOnly(True)
        self.chi_tiet.setText("Click a node on the network map to inspect its data.")
        detail_box.addWidget(self.chi_tiet, 1)
        detail_box.addWidget(chu("Addresses are local observations, not a verified physical network topology.",
                                 10, "#8aa0b9"))
        inspector = khung(detail_box)
        inspector.setFixedWidth(270)
        middle.addWidget(inspector)
        lay.addLayout(middle, 1)
        self.pages.addWidget(page)

    def wrap_map(self):
        box = QVBoxLayout()
        box.setContentsMargins(2, 2, 2, 2)
        box.addWidget(self.so_do)
        return box

    def lap_table(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(chu("PORT EXPLORER", 12, "#8da9c8", True))
        self.bang = QTableWidget(0, 8)
        self.bang.setHorizontalHeaderLabels([
            "Process", "PID", "Protocol", "Local IP", "Local Port",
            "Remote IP", "Remote Port", "State"
        ])
        self.bang.setAlternatingRowColors(True)
        self.bang.setSelectionBehavior(QTableWidget.SelectRows)
        self.bang.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bang.verticalHeader().setVisible(False)
        self.bang.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bang.cellClicked.connect(self.chon_dong)
        lay.addWidget(self.bang)
        self.pages.addWidget(page)

    def lap_history(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        left.addWidget(chu("SNAPSHOT HISTORY", 12, "#8da9c8", True))
        left.addWidget(chu("Stored only on this computer", 10, "#91a5bf"))
        self.lich_su = QListWidget()
        left.addWidget(self.lich_su)
        left.addWidget(nut("Compare selected with current", self.so_sanh_anh))
        lay.addLayout(left, 1)
        comparison = QVBoxLayout()
        comparison.addWidget(chu("DIFFERENCE REPORT", 12, "#8da9c8", True))
        self.so_sanh_text = QTextEdit()
        self.so_sanh_text.setReadOnly(True)
        self.so_sanh_text.setText("Save a snapshot, open or close an app, then compare.")
        comparison.addWidget(self.so_sanh_text)
        lay.addLayout(comparison, 2)
        self.pages.addWidget(page)
        self.tai_lich_su()

    def chuyen_tab(self, i):
        self.pages.setCurrentIndex(i)
        for j, b in enumerate(self.nav):
            b.setProperty("active", j == i)
            b.style().unpolish(b)
            b.style().polish(b)
        if i == 3:
            self.tai_lich_su()

    def quet(self):
        try:
            self.toan_bo = du_lieu_demo() if self.demo.isChecked() else quet_port()
            self.lan_quet += 1
            self.trang.setText(
                ("DEMO DATA • " if self.demo.isChecked() else "LIVE LOCAL • ") +
                f"{len(self.toan_bo)} sockets • scan #{self.lan_quet}"
            )
            self.loc()
        except Exception as loi:
            self.trang.setText("Scan error")
            QMessageBox.warning(self, "Port scan error", str(loi))

    def loc(self):
        search = self.tim.text().strip().lower()
        state = self.trang_thai.currentText()
        protocol = self.giao_thuc.currentText()
        scope = self.pham_vi.currentText()
        results = []
        for item in self.toan_bo:
            haystack = " ".join(str(v) for v in item.values()).lower()
            if search and search not in haystack:
                continue
            s = item["status"].upper()
            if state != "All states":
                if state == "Other" and s in ("LISTEN", "ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT"):
                    continue
                if state != "Other" and s != state:
                    continue
            if protocol != "TCP + UDP" and item["protocol"] != protocol:
                continue
            if scope == "With remote" and not item["remote_ip"]:
                continue
            if scope == "Listening only" and s not in ("LISTEN", "LISTENING"):
                continue
            results.append(item)
        self.da_loc = results
        self.cap_nhat()

    def cap_nhat(self):
        self.thong_ke[0].setText(str(len(self.da_loc)))
        self.thong_ke[1].setText(str(sum(item["status"].upper() in ("LISTEN", "LISTENING") for item in self.da_loc)))
        self.thong_ke[2].setText(str(sum(item["status"].upper() == "ESTABLISHED" for item in self.da_loc)))
        self.thong_ke[3].setText(str(len({i["remote_ip"] for i in self.da_loc if i["remote_ip"]})))
        counts = Counter(i["process"] for i in self.da_loc)
        self.top_process.setText("\n".join(f"{name:32}  {count:>4} sockets"
                                             for name, count in counts.most_common(12))
                                 or "No matching processes")
        self.so_do.ve(self.da_loc)
        self.bang.setRowCount(len(self.da_loc))
        fields = ["process", "pid", "protocol", "local_ip", "local_port",
                  "remote_ip", "remote_port", "status"]
        for row, item in enumerate(self.da_loc):
            for col, field in enumerate(fields):
                self.bang.setItem(row, col, QTableWidgetItem(str(item[field] or "")))

    def chon_dong(self, row, col):
        self.chon_node(self.da_loc[row])

    def chon_node(self, info):
        if info.get("type") == "machine":
            self.chi_tiet.setPlainText("LOCAL MACHINE\n\n" + info["message"])
        elif info.get("type") == "process":
            self.chi_tiet.setPlainText(
                f"PROCESS\n\nName: {info['process']}\nPID: {info['pid']}\n"
                f"Visible connections: {info['count']}"
            )
        else:
            details = "\n\n".join(f"{k.replace('_', ' ').upper()}\n{v or '—'}"
                                   for k, v in info.items())
            self.chi_tiet.setPlainText(details)

    def luu_anh(self):
        try:
            file = luu_snapshot(self.toan_bo, self.demo.isChecked())
            self.tai_lich_su()
            self.trang.setText("Saved locally: " + file.name)
        except OSError as loi:
            QMessageBox.warning(self, "Save failed", str(loi))

    def tai_lich_su(self):
        self.tep_lich_su = danh_sach_snapshot()
        self.lich_su.clear()
        for tep in self.tep_lich_su:
            self.lich_su.addItem(tep.stem.replace("snapshot_", "").replace("_", " "))

    def so_sanh_anh(self):
        idx = self.lich_su.currentRow()
        if idx < 0:
            self.so_sanh_text.setText("Select a snapshot first.")
            return
        try:
            old = doc_snapshot(self.tep_lich_su[idx])
            if old.get("demo", False) != self.demo.isChecked():
                self.so_sanh_text.setText(
                    "Cannot compare DEMO with LIVE data. Select matching mode."
                )
                return
            moi, mat, doi = so_sanh(old["connections"], self.toan_bo)
            lines = [
                f"SNAPSHOT: {old['created']}",
                f"CURRENT SOCKETS: {len(self.toan_bo)}",
                "",
                f"NEW CONNECTIONS: {len(moi)}",
                f"REMOVED CONNECTIONS: {len(mat)}",
                f"STATE CHANGES: {len(doi)}", "",
            ]
            for title, items in [("NEW", moi), ("REMOVED", mat)]:
                lines.append("--- " + title + " ---")
                for item in items[:40]:
                    lines.append(
                        f"{item['process']}  {item['local_port']}  "
                        f"→ {item['remote_ip']}:{item['remote_port']}  [{item['status']}]")
                lines.append("")
            lines.append("--- STATUS CHANGES ---")
            for a, b in doi[:40]:
                lines.append(f"{a['process']} :{a['local_port']}   {a['status']} → {b['status']}")
            self.so_sanh_text.setText("\n".join(lines))
        except (OSError, ValueError, KeyError) as loi:
            QMessageBox.warning(self, "Compare failed", str(loi))

    def xuat(self):
        file, _ = QFileDialog.getSaveFileName(
            self, "Export filtered connections", "portvision_connections.csv", "CSV files (*.csv)"
        )
        if file:
            try:
                xuat_csv(self.da_loc, file)
                self.trang.setText("CSV exported")
            except OSError as loi:
                QMessageBox.warning(self, "Export failed", str(loi))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PortVision()
    window.show()
    sys.exit(app.exec())
