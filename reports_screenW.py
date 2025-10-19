# lib/screens/reports_screen.py
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from datetime import datetime
from database import Database
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ========== استيرادات PDF ==========
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from add_order_dialog import AddOrderDialog
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import os
from PIL import Image
from PyQt5.QtWidgets import QInputDialog

class ReportsScreen(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("📊 التقارير الكاملة")
        self.setGeometry(100, 100, 1000, 600)
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

        # شعار واسم المؤسسة
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        # مسار نسبي للشعار (يجب أن يكون في مجلد المشروع)
        logo_path = os.path.join("assets", "images", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
        else:
            logo_label.setText("🖼️")
            logo_label.setStyleSheet("font-size: 60px;")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        org_name = QLabel("🚛 ضياء اليمن للشحن والاستيراد")
        org_name.setFont(QFont("Amiri", 28, QFont.Bold))
        org_name.setStyleSheet("color: green;")
        org_name.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(org_name)

        layout.addLayout(logo_layout)

        # تاريخ التقرير
        date_label = QLabel(f"التاريخ: {datetime.now().strftime('%d/%m/%Y')}")
        date_label.setFont(QFont("Amiri", 18))
        date_label.setStyleSheet("color: grey;")
        date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(date_label)
  #البحث
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث هنا...")
        self.search_input.setFont(QFont("Amiri", 14))
        self.search_input.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_input)
      
        # جدول التقارير
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
    "الرقم المسلسل", "رقم القاطرة", "اسم السائق", "رقم السائق", "تاريخ الوصول", "نوع الطلب", "اسم التاجر"
])

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)

        # زر تصدير كـ PDF
        export_btn = QPushButton("📸 تصدير كـ PDF")
        export_btn.setFont(QFont("Amiri", 18))
        export_btn.setStyleSheet("background-color: red; color: white; padding: 10px;")
        export_btn.clicked.connect(self.export_to_pdf)
        layout.addWidget(export_btn)

        # زر رجوع
        back_btn = QPushButton("⬅️ رجوع")
        back_btn.setFont(QFont("Amiri", 18))
        back_btn.setStyleSheet("background-color: grey; color: white; padding: 10px;")
        back_btn.clicked.connect(self.reject)
        layout.addWidget(back_btn)


        # button return for the system of status 
        return_btn = QPushButton("🔒 إرجاع إلى نظام الدور")
        return_btn.setFont(QFont("Amiri", 18))
        return_btn.setStyleSheet("background-color: orange; color: black; padding: 10px;")
        return_btn.clicked.connect(self.return_to_queue)
        # layout.addWidget(return_btn)


        self.setLayout(layout)
        self.load_data()
    #def of the secret word 
    def return_to_queue(self):
            password, ok = QInputDialog.getText(self, "التحقق", "أدخل الرقم السري:", QLineEdit.Password)
            if password == "ali":  # يمكنك تغيير الرقم السري
                QMessageBox.information(self, "نجاح", "✅ تم إرجاع الطلبات إلى نظام الدور.")
                # نفّذ هنا منطق الإرجاع الحقيقي
            else:
                QMessageBox.warning(self, "خطأ", "❌ الرقم السري غير صحيح.")
    # search def 
    def filter_table(self, text):
        text = text.strip().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def load_data(self):
        records = self.db.get_all_orders()
        self.table.setRowCount(len(records))
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(str(record[8])))     # 🆔 إدخال من قاعدة البيانات
            self.table.setItem(i, 1, QTableWidgetItem(str(record[2])))     # رقم القاطرة
            self.table.setItem(i, 2, QTableWidgetItem(str(record[1])))     # اسم السائق
            self.table.setItem(i, 3, QTableWidgetItem(str(record[20])))     # رقم السائق
            self.table.setItem(i, 4, QTableWidgetItem(str(record[6])))     # تاريخ الوصول (قد تحتاج تنسيقه)
            self.table.setItem(i, 5, QTableWidgetItem(str(record[16])))     # نوع الطلب
            self.table.setItem(i, 6, QTableWidgetItem(str(record[12])))     # اسم التاجر

            # تلوين الصف إذا كان مؤشَّر عليه
            for col in range(self.table.columnCount()):
                item = self.table.item(i, col)
                if item:
                    if len(record) > 7 and record[7]:
                        item.setBackground(Qt.green)
                    else:
                        item.setBackground(Qt.white)

    # اسم التاجر ✅

          
               
        # تلوين الصف إذا تم التأشير
            for col in range(self.table.columnCount()):
                    item = self.table.item(i, col)
                    if not item:
                        continue
                    if len(record) > 7 and record[7]:  # record[7] يشير إلى حالة التأشيرة (1 أو True)
                        item.setBackground(Qt.green)
                    else:
                        item.setBackground(Qt.white)
    

    def export_to_pdf(self):
        records = self.db.get_all_orders()
        if not records:
            QMessageBox.critical(self, "خطأ", "❌ لا توجد سجلات لتصديرها!")
            return

        try:
            # إنشاء اسم ملف
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "حفظ تقرير ضياء اليمن للنقل والاستيراد",
                f"تقرير ضياء اليمن للنقل والاسيراد_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return
            
            # معالجة النص العربي
            def fix(text):
                if not text or text == "None":
                    return ""
                try:
                    reshaped = arabic_reshaper.reshape(str(text))
                    return get_display(reshaped)
                except:
                    return str(text)

            # مسار الخط النسبي
            font_path = os.path.join("assets", "fonts", "Amiri-Regular.ttf")
            font_name = "ArabicFont"  # افتراضي
            
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                    font_name = 'ArabicFont'
                except:
                    pass  # استخدام الخط الافتراضي إذا فشل التسجيل

            # إنشاء PDF
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            y = height - 50

           
            image_path = "assets/images/logo.png"

            if os.path.exists(image_path):
                from PIL import Image

                img = Image.open(image_path)
                img_width, img_height = img.size

                max_width = width - 500
                aspect_ratio = img_height / img_width
                new_width = min(max_width, img_width)
                new_height = new_width * aspect_ratio

                c.drawImage(image_path, (width - new_width) / 2, height - new_height - 10,
                            width=new_width, height=new_height, mask='auto')  # ← إزالة الخلفية البيضاء تلقائيًا

                y -= new_height + 10

            # العنوان
            c.setFont(font_name, 20)
            c.drawCentredString(width / 2, y, fix("ضياء اليمن للنقل والاستيراد - تقرير السجلات"))
            y -= 40

            # التاريخ والوقت
            current_date = datetime.now().strftime('%d/%m/%Y')
            current_time = datetime.now().strftime('%H:%M')  # التنسيق بتنسيق 24 ساعة
            c.setFont(font_name, 12)
            c.drawString(50, y, fix(f"التاريخ: {current_date}"))
            c.drawString(width - 200, y, fix(f"الوقت: {current_time}"))
            y -= 30

            # خط فاصل
            c.line(50, y, width - 50, y)
            y -= 20
            styles = getSampleStyleSheet()
            styleN = styles['Normal']
            styleN.fontName = font_name
            styleN.fontSize = 10
            styleN.alignment = 2  # 2 = Right

            # إعداد بيانات الجدول مع عكس الأعمدة
            # table_data = [
            #     [fix("تاريخ الوصول"), fix("رقم السائق"), fix("اسم السائق"), fix("رقم القاطرة"), fix("الرقم المسلسل")]
            # ]
            table_data = [
    [
        Paragraph(fix("تاريخ الوصول"), styleN),
        Paragraph(fix("رقم السائق"), styleN),
        Paragraph(fix("اسم السائق"), styleN),
        Paragraph(fix("رقم القاطرة"), styleN),
        Paragraph(fix("الرقم المسلسل"), styleN)
    ]
            ]


            for record in records:
                arrival_date = record[6]
                if isinstance(arrival_date, int):
                  arrival_date = datetime.fromtimestamp(arrival_date).strftime('%d/%m/%Y')
                table_data.append([
                Paragraph(fix(arrival_date), styleN),
                Paragraph(fix(record[20]), styleN),
                Paragraph(fix(record[1]), styleN),
                Paragraph(fix(record[2]), styleN),
                Paragraph(fix(str(record[8])), styleN),
                ])
            # إنشاء الجدول
            table = Table(table_data, colWidths=[120, 120, 120, 120, 50])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # يمنع التفاف  النص في الجدول 
                ('WORDWRAP', (0, 0), (-1, -1), None),
            ]))

            # رسم الجدول
            w, h = table.wrapOn(c, width, height)
            table.drawOn(c, (width - w) / 2, y - h +30)
            y -= h + 40
            # التوقيع
            c.setFont(font_name, 12)
            c.drawRightString(width - 50, y,fix("توقيع المشرف: ________________"))
            y -= 20
            c.drawRightString(width - 50, y, fix("الاسم: ________________"))
            y -= 20
            c.drawRightString(width - 50, y, fix("التاريخ: ________________"))

            c.save()
            QMessageBox.information(self, "نجاح", f"✅ تم حفظ التقرير كـ PDF:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في التصدير إلى PDF:\n{str(e)}")