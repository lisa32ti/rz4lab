import sys
import os
import shutil
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QDialog,
                             QTableWidgetItem, QMessageBox, QFileDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import db

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("register.ui", self)
        self.btnRegister.clicked.connect(self.register)
        self.btnBack.clicked.connect(self.close)

    def register(self):
        login = self.editRegLogin.text()
        pwd = self.editRegPassword.text()
        if not login or not pwd:
            QMessageBox.warning(self, "Error", "Fill all fields!")
            return
        
        if db.register_user(login, pwd):
            QMessageBox.information(self, "Success", "User registered! You can now login.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "This login is already taken!")

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)
        self.btnLogin.clicked.connect(self.login)
        self.btnGoReg.clicked.connect(self.open_register)
        self.reg_window = None

    def login(self):
        login = self.editLogin.text()
        pwd = self.editPassword.text()
        if db.check_user(login, pwd):
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Wrong login or password!")

    def open_register(self):
        self.reg_window = RegisterWindow()
        self.reg_window.show()

class EditBookWindow(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        uic.loadUi("editbook.ui", self)
        
        self.image_path = ""
        self.book_data = book_data

        self.btnSelectImage.clicked.connect(self.select_image)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if book_data:
            self.editTitle.setText(book_data[1])
            self.editAuthor.setText(book_data[2])
            self.editYear.setText(str(book_data[3]))
            self.editGenre.setText(book_data[4])
            
            if book_data[5]:
                self.image_path = book_data[5]
                self.labelImagePath.setText(os.path.basename(self.image_path))
                full_path = os.path.join(os.path.dirname(__file__), "images", book_data[5])
                pix = QPixmap(full_path)
                if not pix.isNull():
                    self.labelImagePath.setPixmap(pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def select_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.image_path = file
            self.labelImagePath.setText(os.path.basename(file))
            pix = QPixmap(file)
            # Задаем размер превью
            self.labelImagePath.setFixedSize(100, 100)
            self.labelImagePath.setScaledContents(True)
            self.labelImagePath.setPixmap(pix)

    def get_data(self):
        return {
            "title": self.editTitle.text(),
            "author": self.editAuthor.text(),
            "year": self.editYear.text(),
            "genre": self.editGenre.text(),
            "image_path": self.image_path
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        
        self.img_dir = os.path.join(os.path.dirname(__file__), "images")
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        self.btnSearch.clicked.connect(self.load_books)
        self.btnReset.clicked.connect(self.reset_search)
        self.btnAdd.clicked.connect(self.add_book)
        self.btnEdit.clicked.connect(self.edit_book)
        self.btnDelete.clicked.connect(self.delete_book)
        
        self.tableBooks.itemSelectionChanged.connect(self.show_preview)

        self.load_books()

    def load_books(self):
        search_title = self.editSearchTitle.text().strip()
        search_author = self.editSearchAuthor.text().strip()

        query = "SELECT id, title, author, year, genre, image_path FROM books WHERE 1=1"
        params = []
        if search_title:
            query += " AND title LIKE ?"
            params.append(f"%{search_title}%")
        if search_author:
            query += " AND author LIKE ?"
            params.append(f"%{search_author}%")

        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()

        self.tableBooks.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            self.tableBooks.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                if col_idx == 0 or col_idx == 5:
                    item = QTableWidgetItem(str(data) if data is not None else "")
                    self.tableBooks.setItem(row_idx, col_idx, item)
                else:
                    self.tableBooks.setItem(row_idx, col_idx, QTableWidgetItem(str(data) if data is not None else ""))
        
        self.tableBooks.setColumnHidden(0, True)
        self.tableBooks.setColumnHidden(5, True)
        self.tableBooks.setHorizontalHeaderLabels(["ID", "Title", "Author", "Year", "Genre", "Path"])

    def reset_search(self):
        self.editSearchTitle.clear()
        self.editSearchAuthor.clear()
        self.load_books()

    def add_book(self):
        dialog = EditBookWindow()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["title"] or not data["author"]:
                QMessageBox.warning(self, "Error", "Title and Author are required!")
                return
            
            img_name = ""
            if data["image_path"]:
                img_name = os.path.basename(data["image_path"])
                shutil.copy(data["image_path"], os.path.join(self.img_dir, img_name))
            
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO books (title, author, year, genre, image_path) VALUES (?, ?, ?, ?, ?)",
                            (data["title"], data["author"], data["year"], data["genre"], img_name))
                conn.commit()
            self.load_books()

    def edit_book(self):
        selected = self.tableBooks.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a book to edit!")
            return
        
        row = selected[0].row()
        book_id = int(self.tableBooks.item(row, 0).text())
        
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, title, author, year, genre, image_path FROM books WHERE id=?", (book_id,))
            book_data = cur.fetchone()

        dialog = EditBookWindow(book_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            img_name = book_data[5] if book_data[5] else ""
            if data["image_path"] and os.path.basename(data["image_path"]) != img_name:
                img_name = os.path.basename(data["image_path"])
                shutil.copy(data["image_path"], os.path.join(self.img_dir, img_name))

            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""UPDATE books SET title=?, author=?, year=?, genre=?, image_path=? WHERE id=?""",
                            (data["title"], data["author"], data["year"], data["genre"], img_name, book_id))
                conn.commit()
            self.load_books()

    def delete_book(self):
        selected = self.tableBooks.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a book to delete!")
            return
        
        reply = QMessageBox.question(self, 'Delete', 'Are you sure?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected[0].row()
            book_id = int(self.tableBooks.item(row, 0).text())
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM books WHERE id=?", (book_id,))
                conn.commit()
            self.load_books()

    def show_preview(self):
        selected = self.tableBooks.selectedItems()
        if not selected:
            self.imagePreview.clear()
            return
        
        row = selected[0].row()
        img_name = self.tableBooks.item(row, 5).text() if self.tableBooks.item(row, 5) else ""
        
        if img_name:
            full_path = os.path.join(self.img_dir, img_name)
            pix = QPixmap(full_path)
            if not pix.isNull():
                self.imagePreview.setText("") 
                
                self.imagePreview.setPixmap(pix)
            else:
                self.imagePreview.clear()
                self.imagePreview.setText("Image not found")
        else:
            self.imagePreview.clear()
            self.imagePreview.setText("No image")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db.init_db()
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())