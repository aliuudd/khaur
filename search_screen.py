# lib/screens/search_screen.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
from database import Database

class SearchScreen(QDialog):
    def __init__(self, db: Database):
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

    # search_screen.py - التحديث
    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        # البحث في الطلبات
        orders = self.db.search_orders(query)
        self.table.setRowCount(len(orders))
        
        for i, order in enumerate(orders):
            try:
                reg_date = datetime.fromtimestamp(order[11]).strftime("%d/%m/%Y %H:%M")
            except:
                reg_date = str(order[11])
                
            row_items = [
                str(i + 1),         # م
                order[1] or "",     # اسم السائق
                order[2] or "",     # رقم القاطرة
                order[20] or "",    # رقم الهاتف
                order[5] or "",     # نوع البضاعة
                order[4] or "",     # منطقة الوصول
                order[12] or "",    # اسم التاجر
                reg_date            # تاريخ التسجيل
            ]

            for col, val in enumerate(row_items):
                self.table.setItem(i, col, QTableWidgetItem(str(val)))

        if not orders:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("❌ لا توجد نتائج مطابقة."))
            self.table.setSpan(0, 0, 1, 8)