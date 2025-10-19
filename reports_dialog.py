# reports_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from database import Database



class ReportsDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("📊 التقارير الكاملة")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان الشاشة
        title = QLabel("📊 التقارير الكاملة")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # زر تصدير كـ PDF
        export_btn = QPushButton("📸 تصدير كصورة")
        export_btn.setFont(QFont("Amiri", 18))
        export_btn.setStyleSheet("background-color: red; color: white; padding: 10px;")
        export_btn.clicked.connect(self.export_as_pdf)
        layout.addWidget(export_btn)

        # جدول التقارير
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        # 
        self.table.setHorizontalHeaderLabels([
    "م", "رقم القاطرة", "اسم السائق", "رقم السائق", "تاريخ الوصول", "نوع الطلب", "اسم التاجر"
])

        self.table.setFont(QFont("Amiri", 12))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 12, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)

        self.load_data()
        self.setLayout(layout)

    # def load_data(self):
    #     records = self.db.get_all_records()
    #     self.table.setRowCount(len(records))
    #     for i, record in enumerate(records):
    #         self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
    #         self.table.setItem(i, 1, QTableWidgetItem(record[1]))
    #         self.table.setItem(i, 2, QTableWidgetItem(record[2]))
    #         self.table.setItem(i, 3, QTableWidgetItem(record[3]))
    #         self.table.setItem(i, 4, QTableWidgetItem(str(record[4])))
    def load_data(self):
        records = self.db.get_all_records()
        self.table.setRowCount(len(records))
        for i, record in enumerate(records):
            # record هو tuple — لذلك نستخدم record[0], record[1], ... بدلاً من record.id, record.truck_number, ...
            self.table.setItem(i, 0, QTableWidgetItem(record[8]))
            self.table.setItem(i, 1, QTableWidgetItem(record[2]))  # ← record[1] = truck_number
            self.table.setItem(i, 2, QTableWidgetItem(record[1]))  # ← record[2] = driver_name
            self.table.setItem(i, 3, QTableWidgetItem(record[20]))  # ← record[3] = driver_phone
            self.table.setItem(i, 4, QTableWidgetItem(str(record[6]))) 
            self.table.setItem(i, 5, QTableWidgetItem(str(record[16])))
            self.table.setItem(i, 6, QTableWidgetItem(str(record[12])))
        
            
             # ← record[4] = arrival_date (timestamp)
    def export_as_pdf(self):
        records = self.db.get_all_orders()
        if not records:
            QMessageBox.critical(self, "خطأ", "❌ لا توجد سجلات لتصديرها!")
            return

        try:
            # تسجيل الخط العربي
            pdfmetrics.registerFont(TTFont('Amiri', 'assets/fonts/Amiri-Regular.ttf'))

            # إنشاء ملف PDF
            c = canvas.Canvas("reports_export.pdf", pagesize=letter)
            width, height = letter

            # العنوان
            c.setFont("Amiri", 24)
            c.drawString(100, height - 50, "🚛 ضياء اليمن للنقل والاستيراد")
            c.setFont("Amiri", 18)
            c.drawString(100, height - 80, "📊 تقرير السجلات")
            c.setFont("Amiri", 14)
            c.drawString(100, height - 110, f"التاريخ: {Qt.currentDate().toString('dd/MM/yyyy')}")

            # الجدول
            y = height - 150
            c.setFont("Amiri", 12)
            headers = ["م", "رقم القاطرة", "اسم السائق", "رقم السائق", "تاريخ الوصول"]
            for i, header in enumerate(headers):
                c.drawString(100 + i * 100, y, header)
            y -= 20
            c.line(50, y, width - 50, y)
            y -= 20

            for i, record in enumerate(records):
                c.drawString(100, y, record([8]))
                c.drawString(200, y, record[2])
                c.drawString(500, y, record[1])
                c.drawString(300, y, record[20])
                c.drawString(400, y, record[6])
                c.drawString(500, y, record[5])
                c.drawString(500, y, record[12])
                y -= 20

            c.save()
            QMessageBox.information(self, "نجاح", "✅ تم التصدير إلى PDF!")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في التصدير: {e}")