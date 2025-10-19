



from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from database import Database
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import os
from babel.dates import format_datetime
import sqlite3

def fix_arabic(text):
    if isinstance(text, str) and any('\u0600' <= c <= '\u06FF' for c in text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text

class AddmarScreen(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.transferred_orders = self.db.get_transferred_orders()
        self.setWindowTitle("كشف ادارة الطلبات")
        self.setGeometry(100, 100, 1500, 700)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان الشاشة
        title = QLabel("ادارة الطلبات")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: #9C27B0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # جدول ادارة الطلبات
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "رقم القاطرة", "اسم السائق", "رقم الجوال", 
            "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", 
            "المكتب", "التأكيد", "ملاحظات", "إرجاع إلى النهمة",""
        ])

        self.table.setFont(QFont("Amiri", 9))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        
        # ضبط أبعاد الأعمدة
        self.table.setColumnWidth(1, 100)  # رقم القاطرة
        self.table.setColumnWidth(2, 150)  # اسم السائق
        self.table.setColumnWidth(3, 120)  # رقم الجوال
        self.table.setColumnWidth(4, 80)   # الكمية
        self.table.setColumnWidth(5, 120)  # نوع البضاعة
        self.table.setColumnWidth(6, 120)  # منطقة الوصول
        self.table.setColumnWidth(7, 120)  # التاجر
        self.table.setColumnWidth(8, 100)  # المكتب
        self.table.setColumnWidth(9, 80)   # التأكيد
        self.table.setColumnWidth(10, 150) # ملاحظات
        self.table.setColumnWidth(11, 120) # إرجاع إلى النهمة
        self.table.setColumnWidth(12, 120) # إرجاع إلى النهمة
        
        
        layout.addWidget(self.table)

        # أزرار التصدير
        export_layout = QHBoxLayout()
        
        export_btn = QPushButton("📸 تصدير كشف ادارة الطلبات PDF")
        export_btn.setFont(QFont("Amiri", 14))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0; 
                color: white; 
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        export_btn.clicked.connect(self.export_to_pdf)
        export_layout.addWidget(export_btn)
        
        layout.addLayout(export_layout)
        self.setLayout(layout)
        
        self.load_data()

    def return_to_nihma(self, order_id):
        """إرجاع الطلب من إدارة الطلبات إلى كشف النهمة"""
        try:
            # تحديث حالة الطلب
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET is_transferred = 0 WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()

            # إعادة تحميل الجدول
            self.load_data()

            QMessageBox.information(self, "تم الإرجاع", f"✅ تم إرجاع الطلب رقم {order_id} إلى كشف النهمة بنجاح.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ حدث خطأ أثناء الإرجاع:\n{str(e)}")

    def mark_as_completed(self, order_id):
        """تشطيب الطلب من إدارة الطلبات ونقله إلى كشف التشطيب"""
        reply = QMessageBox.question(
            self,
            "تأكيد التشطيب",
            "هل أنت متأكد أنك تريد تشطيب هذا الطلب؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # تحديث حالة الطلب إلى مشطوب
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE orders SET is_completed = 1 WHERE id = ?", (order_id,))
                conn.commit()
                conn.close()

                # إعادة تحميل الجدول لإخفاء الطلب المشطوب
                self.load_data()

                QMessageBox.information(self, "تم التشطيب", "✅ تم تشطيب الطلب ونقله إلى كشف التشطيب.")

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"❌ فشل في تشطيب الطلب:\n{str(e)}")

    def load_data(self):
        """تحميل الطلبات التي تم ترحيلها من كشف النهمة فقط"""
        import sqlite3

        # جلب الطلبات المرحّلة فقط
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            WHERE is_transferred = 1 
            ORDER BY created_datetime ASC
        """)
        records = cursor.fetchall()
        conn.close()

        # إذا لم توجد أي طلبات مرحّلة
        if not records:
            self.table.clearContents()
            self.table.setRowCount(0)
            QMessageBox.information(self, "تنبيه", "لا توجد طلبات تم ترحيلها من كشف النهمة بعد.")
            return

        # تجهيز الجدول
        self.table.clearContents()
        self.table.setRowCount(len(records))

        for i, record in enumerate(records):
            order_id = record[0]

            # عرض الأعمدة الرئيسية فقط
            row_data = [
                record[2] or "",     # رقم القاطرة
                record[1] or "",     # اسم السائق
                record[20] or "",    # رقم الجوال
                record[3] or "",     # الكمية
                record[5] or "",     # نوع البضاعة
                record[4] or "",     # منطقة الوصول
                record[12] or "",    # التاجر
                record[32] or "",    # المكتب
                record[9] or "",     # التأكيد
                record[29] or "",    # ملاحظات
            ]

            # تعبئة الخلايا
            for col, val in enumerate(row_data):
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                cell.setBackground(QColor(200, 255, 200))
                self.table.setItem(i, col, cell)

            # 🔹 زر الإرجاع إلى النهمة
            return_btn = QPushButton("↩️ إرجاع إلى النهمة")
            return_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            return_btn.clicked.connect(lambda checked, oid=order_id: self.return_to_nihma(oid))
            self.table.setCellWidget(i, 11, return_btn)



    def transfer_order(self, order_id):
        """ترحيل طلب - نفس الدالة المستخدمة في main_window.py"""
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب")
                return

            success = self.db.transfer_to_main_database(order)
            if success:
                self.transferred_orders.add(order_id)
                self.load_data()  # إعادة تحميل البيانات بعد الترحيل
                QMessageBox.information(self, "نجاح", f"✅ تم ترحيل الطلب رقم {order_id} بنجاح")
            else:
                QMessageBox.critical(self, "خطأ", "❌ فشل في ترحيل البيانات")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في الترحيل: {str(e)}")
   
    def export_to_pdf(self):
        """تصدير كشف ادارة الطلبات إلى PDF"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            WHERE is_transferred = 1 AND is_completed = 0
            ORDER BY created_datetime ASC
        """)
        records = cursor.fetchall()
        conn.close()

        if not records:
            QMessageBox.critical(self, "خطأ", "❌ لا توجد طلبات لتصديرها!")
            return

        try:
            pdf = FPDF(orientation="L", unit="mm", format="A4")
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # تحميل الخطوط
            fonts_dir = "assets/fonts/"
            regular_path = os.path.join(fonts_dir, "Amiri-Regular.ttf")
            bold_path = os.path.join(fonts_dir, "Amiri-Bold.ttf")
            pdf.add_font("Amiri", "", regular_path, uni=True)
            pdf.add_font("Amiri", "B", bold_path if os.path.exists(bold_path) else regular_path, uni=True)

            # أعلى الصفحة
            pdf.set_xy(10, 10)
            pdf.set_font("Amiri", size=11)
            pdf.cell(0, 6, fix_arabic("Republic of Yemen"), ln=1, align="R")
            pdf.cell(0, 6, fix_arabic("الجمهورية اليمنية"), ln=1, align="R")
            pdf.cell(0, 6, fix_arabic("ضياء اليمن للنقل والاستيراد"), ln=1, align="R")

            # التاريخ
            now = format_datetime(datetime.now(), "EEEE، d MMMM y - h:mm a", locale='ar')
            pdf.set_xy(10, 10) 
            pdf.cell(80, 6, fix_arabic(f"التاريخ: {now}"), ln=True, align="L")

            pdf.ln(10)

            # شعار في الوسط
            logo_path = "assets/images/logo.png"
            if os.path.exists(logo_path):
                pdf.set_xy(10, 10) 
                pdf.image(logo_path, x=(pdf.w - 30)/2, w=30)
                pdf.ln(15)

            # عنوان التقرير
            pdf.set_font("Amiri", "B", 14)
            pdf.cell(0, 8, fix_arabic("تقرير إدارة الطلبات"), ln=2, align="C")
            pdf.ln(6)

            # إعداد الأعمدة
            headers = [
                "المسلسل", "رقم القاطرة", "اسم السائق", "رقم الجوال",
                "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر",
                "المكتب", "التأكيد", "ملاحظات"
            ]

            headers = headers[::-1]

            page_width = pdf.w - pdf.l_margin - pdf.r_margin
            col_ratios = [2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2]
            total_ratio = sum(col_ratios)
            col_widths = [page_width * (r / total_ratio) for r in col_ratios]
            line_height = pdf.font_size * 1.5

            # رأس الجدول
            pdf.set_fill_color(144, 238, 144)
            pdf.set_font("Amiri", "B", 8)

            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], line_height, fix_arabic(h), border=1, align="C", fill=True)
            pdf.ln(line_height)

            # بيانات الجدول
            pdf.set_font("Amiri", "", 8)
            for record in records:
                row = [
                    record[8] or "",    # المسلسل
                    record[2] or "",    # رقم القاطرة
                    record[1] or "",    # اسم السائق
                    record[20] or "",   # رقم الجوال
                    record[3] or "",    # الكمية
                    record[5] or "",    # نوع البضاعة
                    record[4] or "",    # منطقة الوصول
                    record[12] or "",   # التاجر
                    record[32] or "",   # المكتب
                    record[9] or "",    # التأكيد
                    record[29] or "",   # ملاحظات
                ]
                row = row[::-1]

                y_start = pdf.get_y()
                for j, cell in enumerate(row):
                    x = pdf.get_x()
                    pdf.multi_cell(col_widths[j], line_height, fix_arabic(str(cell)), border=1, align="C", fill=False)
                    pdf.set_xy(x + col_widths[j], y_start)
                pdf.ln(line_height)

            # التوقيع
            pdf.ln(10)
            pdf.set_font("Amiri", size=11)
            pdf.cell(0, 6, fix_arabic("توقيع المشرف: ________________"), ln=True, align="L")
            pdf.cell(0, 6, fix_arabic("الاسم: ________________"), ln=True, align="L")
            pdf.cell(0, 6, fix_arabic("التاريخ: ________________"), ln=True, align="L")

            # حفظ الملف
            default_name = f"تقرير_الطلبات_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(self, "حفظ تقرير الطلبات", default_name, "PDF Files (*.pdf)")
            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "نجاح", f"✅ تم حفظ تقرير الطلبات كـ PDF:\n{file_path}")
            else:
                QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ التقرير.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")