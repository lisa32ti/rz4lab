import sys
import os
import random
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt

class RunawayButton(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "task4.ui"), self)

        self.setMouseTracking(True)
        self.btnRun.setMouseTracking(True)
        
        self.btnRun.enterEvent = self.move_button

    def move_button(self, event):
        max_x = self.width() - self.btnRun.width()
        max_y = self.height() - self.btnRun.height()

        new_x = random.randint(0, max_x)
        new_y = random.randint(0, max_y)

        self.btnRun.move(new_x, new_y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = RunawayButton()
    w.show()
    sys.exit(app.exec_())