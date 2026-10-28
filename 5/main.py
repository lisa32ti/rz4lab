import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class UFO(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "task5.ui"), self)

        pix = QPixmap(os.path.join(os.path.dirname(__file__), "ufo.png"))
        if not pix.isNull():
            self.ufoLabel.setPixmap(pix)
            self.ufoLabel.setScaledContents(True)
            self.ufoLabel.resize(60, 60)
        
        self.step = 20

    def keyPressEvent(self, event):
        x = self.ufoLabel.x()
        y = self.ufoLabel.y()
        w = self.ufoLabel.width()
        h = self.ufoLabel.height()
        
        win_w = self.width()
        win_h = self.height()

        if event.key() == Qt.Key_Left:
            x -= self.step
            if x + w < 0:
                x = win_w
        elif event.key() == Qt.Key_Right:
            x += self.step
            if x > win_w:
                x = -w
        elif event.key() == Qt.Key_Up:
            y -= self.step
            if y + h < 0:
                y = win_h 
        elif event.key() == Qt.Key_Down:
            y += self.step
            if y > win_h: 
                y = -h 

        self.ufoLabel.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UFO()
    w.show()
    sys.exit(app.exec_())