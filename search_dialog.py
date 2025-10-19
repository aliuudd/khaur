# search_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SearchDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("🔍 البحث المتقدم")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان الشاشة
        title = QLabel("🔍 البحث المتقدم")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # حقل البحث
        self.search_input = QLineEdit()
        self.search_input.setFont(QFont("Amiri", 18))
        self.search_input.setAlignment(Qt.AlignRight)
        self.search_input.setPlaceholderText("ابحث برقم القاطرة أو اسم السائق أو تاريخ...")
        layout.addWidget(self.search_input)

        # زر البحث
        search_btn = QPushButton("🔎 بحث الآن")
        search_btn.setFont(QFont("Amiri", 18))
        search_btn.setStyleSheet("background-color: blue; color: white; padding: 10px;")
        search_btn.clicked.connect(self.perform_search)
        layout.addWidget(search_btn)

        # جدول النتائج
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["م", "رقم القاطرة", "اسم السائق", "رقم السائق", "تاريخ الوصول"])
        self.table.setFont(QFont("Amiri", 12))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 12, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.critical(self, "خطأ", "يرجى إدخال نص البحث!")
            return

        records = self.db.search_records(query)
        self.table.setRowCount(len(records))
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(record[4]))
            self.table.setItem(i, 2, QTableWidgetItem(record[3]))
            self.table.setItem(i, 3, QTableWidgetItem(record[2]))
            self.table.setItem(i, 4, QTableWidgetItem(str(record[1])))