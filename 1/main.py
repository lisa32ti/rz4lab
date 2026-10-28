import sys
import os
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem

class Olympiad(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "task1.ui"), self)

        self.data = []
        self.load_data()

        schools = sorted(set(row['school'] for row in self.data))
        classes = sorted(set(row['class'] for row in self.data))
        
        self.comboSchool.addItem("All schools")
        self.comboSchool.addItems(schools)
        self.comboClass.addItem("All classes")
        self.comboClass.addItems(classes)

        self.comboSchool.currentIndexChanged.connect(self.apply_filters)
        self.comboClass.currentIndexChanged.connect(self.apply_filters)

        self.tableResults.setHorizontalHeaderLabels(["Login", "Full name", "Total points"])
        
        self.apply_filters()

    def load_data(self):
        base = os.path.dirname(__file__)
        path = os.path.join(base, "rez.csv")
        
        try:
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    login = row.get('login', '')
                    parts = login.split("-")
                    school = parts[2] if len(parts) > 2 else "?"
                    cls = parts[3] if len(parts) > 3 else "?"
                    
                    self.data.append({
                        'login': login,
                        'name': row.get('user_name', ''),
                        'score': int(row.get('Score', 0)),
                        'school': school,
                        'class': cls
                    })
        except Exception as e:
            print("Error loading file:", e)

    def apply_filters(self):
        sel_school = self.comboSchool.currentText()
        sel_class = self.comboClass.currentText()

        filtered = []
        for row in self.data:
            if sel_school != "All schools" and row['school'] != sel_school:
                continue
            if sel_class != "All classes" and row['class'] != sel_class:
                continue
            filtered.append(row)

        filtered.sort(key=lambda x: x['score'], reverse=True)

        for i, row in enumerate(filtered):
            if i == 0:
                row['place'] = 1
            elif row['score'] == filtered[i-1]['score']:
                row['place'] = filtered[i-1]['place']
            else:
                row['place'] = i + 1

        self.tableResults.setRowCount(len(filtered))
        self.labelCount.setText(f"Found: {len(filtered)}")

        for i, row in enumerate(filtered):
            self.tableResults.setItem(i, 0, QTableWidgetItem(row['login']))
            self.tableResults.setItem(i, 1, QTableWidgetItem(row['name']))
            self.tableResults.setItem(i, 2, QTableWidgetItem(str(row['score'])))

            place = row['place']
            if place == 1:
                color = QColor(255, 215, 0)
            elif place == 2:
                color = QColor(192, 192, 192)
            elif place == 3:
                color = QColor(205, 127, 50)
            else:
                continue

            for col in range(3):
                self.tableResults.item(i, col).setBackground(color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Olympiad()
    w.show()
    sys.exit(app.exec_())