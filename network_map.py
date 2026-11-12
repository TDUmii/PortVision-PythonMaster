"""So do ket noi. File ve san: hoc vien khong can hoc ve do hoa nang cao."""
from collections import defaultdict

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView


class Nut(QGraphicsItem):
    def __init__(self, x, y, rong, cao, tieu_de, mo_ta, mau, thong_tin, khi_chon):
        super().__init__()
        self.setPos(x, y)
        self.rong, self.cao = rong, cao
        self.tieu_de, self.mo_ta = tieu_de, mo_ta
        self.mau = QColor(mau)
        self.thong_tin, self.khi_chon = thong_tin, khi_chon
        self.setAcceptHoverEvents(True)
        self.dang_hover = False
        self.setToolTip(tieu_de + "\n" + mo_ta)

    def boundingRect(self):
        return QRectF(0, 0, self.rong, self.cao)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        nen = QColor("#1a263b" if self.dang_hover else "#131e30")
        painter.setBrush(QBrush(nen))
        painter.setPen(QPen(self.mau if self.dang_hover else QColor("#304056"), 1.5))
        painter.drawRoundedRect(self.boundingRect(), 12, 12)
        painter.setPen(self.mau)
        painter.setBrush(self.mau)
        painter.drawEllipse(12, 18, 7, 7)
        painter.setPen(QColor("#f3f7ff"))
        painter.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        painter.drawText(QRectF(27, 8, self.rong - 34, 22),
                         Qt.AlignLeft | Qt.AlignVCenter, self.tieu_de)
        painter.setPen(QColor("#91a5bf"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(QRectF(13, 32, self.rong - 22, 18),
                         Qt.AlignLeft | Qt.AlignVCenter, self.mo_ta)

    def hoverEnterEvent(self, event):
        self.dang_hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.dang_hover = False
        self.update()

    def mousePressEvent(self, event):
        self.khi_chon(self.thong_tin)
        super().mousePressEvent(event)


class SoDoMang(QGraphicsView):
    def __init__(self, khi_chon):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.khi_chon = khi_chon
        self.setBackgroundBrush(QColor("#0d1727"))
        self.setRenderHint(QPainter.Antialiasing)
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(0.87, 0.87)
        self.setMinimumHeight(470)

    def zoom(self, he_so):
        if 0.45 <= self.transform().m11() * he_so <= 1.8:
            self.scale(he_so, he_so)

    def duong_noi(self, x1, y1, x2, y2, mau="#34506a"):
        self.scene.addLine(x1, y1, x2, y2, QPen(QColor(mau), 1.7))

    def nut(self, x, y, rong, title, sub, mau, item):
        self.scene.addItem(Nut(x, y, rong, 60, title, sub, mau, item, self.khi_chon))

    def ve(self, danh_sach):
        self.scene.clear()
        nhom = defaultdict(list)
        for item in danh_sach:
            nhom[(item["process"], item["pid"])].append(item)

        # Hien thi nhieu nhat 8 ung dung va 3 ket noi moi ung dung
        ung_dung = sorted(nhom, key=lambda k: -len(nhom[k]))[:8]
        chieu_cao = 190
        for key in ung_dung:
            chieu_cao += max(1, min(len(nhom[key]), 3)) * 76 + 24
        chieu_cao = max(580, chieu_cao)
        self.scene.setSceneRect(0, 0, 1050, chieu_cao)

        self.scene.addText("LOCAL MACHINE  /  PROCESS  /  LOCAL PORT  /  REMOTE ENDPOINT",
                           QFont("Segoe UI", 10, QFont.DemiBold)).setDefaultTextColor(QColor("#68839d"))

        # Ghim nut may tinh o dau ban do de luon nhin thay khi mo ung dung
        root_y = 205
        self.nut(32, root_y, 160, "THIS DEVICE", "local machine", "#38bdf8", {
            "type": "machine", "message": "This computer. The map shows local socket connections."
        })
        y = 75
        for ten, pid in ung_dung:
            ket_noi = nhom[(ten, pid)][:3]
            giua = y + (len(ket_noi) - 1) * 38
            self.duong_noi(192, root_y + 30, 240, giua + 30)
            self.nut(240, giua, 180, ten[:23], "PID " + str(pid or "?"), "#a78bfa", {
                "type": "process", "process": ten, "pid": pid,
                "count": len(nhom[(ten, pid)])
            })
            for i, item in enumerate(ket_noi):
                port_y = y + i * 76
                status = item["status"].upper()
                color = "#fbbf24" if status in ("LISTEN", "LISTENING") else (
                    "#34d399" if status == "ESTABLISHED" else "#94a3b8")
                self.duong_noi(420, giua + 30, 460, port_y + 30)
                self.nut(460, port_y, 180, str(item["protocol"]) + " : " +
                         str(item["local_port"]), status, color, dict(item))
                if item["remote_ip"]:
                    self.duong_noi(640, port_y + 30, 675, port_y + 30, "#395b73")
                    remote = item["remote_ip"]
                    if len(remote) > 22:
                        remote = remote[:20] + "..."
                    self.nut(675, port_y, 235, remote,
                             "Remote port " + str(item["remote_port"]), "#60a5fa", dict(item))
            y += len(ket_noi) * 76 + 24

        if not danh_sach:
            t = self.scene.addText("No connections match the current filters",
                                   QFont("Segoe UI", 14))
            t.setDefaultTextColor(QColor("#91a5bf"))
            t.setPos(300, 200)
        else:
            t = self.scene.addText(
                f"Showing {len(ung_dung)} processes / up to 3 connections each  •  Select a node for details",
                QFont("Segoe UI", 9))
            t.setDefaultTextColor(QColor("#66839e"))
            t.setPos(28, chieu_cao - 40)
