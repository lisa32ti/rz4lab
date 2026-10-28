import sys
import os
import random
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPolygon
from PyQt5.QtCore import Qt, QPoint

class Shapes(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "task3.ui"), self)
        self.shapes = []

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        size = random.randint(20, 80)
        color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        if event.button() == Qt.LeftButton:
            self.shapes.append(("circle", x, y, size, color))
        elif event.button() == Qt.RightButton:
            self.shapes.append(("square", x, y, size, color))
        
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            pos = self.mapFromGlobal(self.cursor().pos())
            size = random.randint(20, 80)
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.shapes.append(("triangle", pos.x(), pos.y(), size, color))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for shape_type, x, y, size, color in self.shapes:
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            half = size // 2
            if shape_type == "circle":
                painter.drawEllipse(x - half, y - half, size, size)
            elif shape_type == "square":
                painter.drawRect(x - half, y - half, size, size)
            elif shape_type == "triangle":
                points = [
                    QPoint(x, y - half),
                    QPoint(x - half, y + half),
                    QPoint(x + half, y + half)
                ]
                painter.drawPolygon(QPolygon(points))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Shapes()
    w.show()
    sys.exit(app.exec_())