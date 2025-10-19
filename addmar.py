# from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
#                              QPushButton, QTableWidget, QTableWidgetItem, 
#                              QMessageBox, QFileDialog, QInputDialog)
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QFont, QColor
# from datetime import datetime
# from database import Database
# from fpdf import FPDF
# import arabic_reshaper
# from bidi.algorithm import get_display
# import os

# def fix_arabic(text):
#     if isinstance(text, str) and any('\u0600' <= c <= '\u06FF' for c in text):
#         reshaped = arabic_reshaper.reshape(text)
#         return get_display(reshaped)
#     return text

# class AddmarScreen(QDialog):
#     def __init__(self, db: Database):
#         super().__init__()
#         self.db = db

        
#         self.completion_reasons = {}  # لتخزين أسباب التشطيب
#         self.setWindowTitle("كشف التشطيب")
#         self.setGeometry(100, 100, 1500, 700)
#         self.setStyleSheet("background-color: white;")
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()
#         layout.setAlignment(Qt.AlignCenter)

#         # عنوان الشاشة
#         title = QLabel("كشف التشطيب")
#         title.setFont(QFont("Amiri", 24, QFont.Bold))
#         title.setStyleSheet("color: #9C27B0;")
#         title.setAlignment(Qt.AlignCenter)
#         layout.addWidget(title)

#         # جدول كشف التشطيب
#         self.table = QTableWidget()
#         self.table.setColumnCount(13)  # زيادة عمود لسبب التشطيب وزر التشطيب
#         self.table.setHorizontalHeaderLabels([
#             "المسلسل", "رقم القاطرة", "اسم السائق", "رقم الجوال", 
#             "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", 
#             "المكتب", "التأكيد", "ملاحظات", "سبب التشطيب", "إجراء التشطيب"
#         ])
#         self.table.setFont(QFont("Amiri", 10))
#         self.table.setEditTriggers(QTableWidget.NoEditTriggers)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
#         self.table.setLayoutDirection(Qt.RightToLeft)
        
#         # ضبط أبعاد الأعمدة
#         self.table.setColumnWidth(0, 80)   # المسلسل
#         self.table.setColumnWidth(1, 100)  # رقم القاطرة
#         self.table.setColumnWidth(2, 150)  # اسم السائق
#         self.table.setColumnWidth(3, 120)  # رقم الجوال
#         self.table.setColumnWidth(4, 80)   # الكمية
#         self.table.setColumnWidth(5, 120)  # نوع البضاعة
#         self.table.setColumnWidth(6, 120)  # منطقة الوصول
#         self.table.setColumnWidth(7, 120)  # التاجر
#         self.table.setColumnWidth(8, 100)  # المكتب
#         self.table.setColumnWidth(9, 80)   # التأكيد
#         self.table.setColumnWidth(10, 150) # ملاحظات
#         self.table.setColumnWidth(11, 200) # سبب التشطيب
#         self.table.setColumnWidth(12, 100) # إجراء التشطيب
        
#         layout.addWidget(self.table)

#         # أزرار التصدير
#         export_layout = QHBoxLayout()
        
#         export_btn = QPushButton("📸 تصدير كشف التشطيب PDF")
#         export_btn.setFont(QFont("Amiri", 14))
#         export_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #9C27B0; 
#                 color: white; 
#                 padding: 10px;
#                 border-radius: 6px;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background-color: #7B1FA2;
#             }
#         """)
#         export_btn.clicked.connect(self.export_to_pdf)
#         export_layout.addWidget(export_btn)
        
#         layout.addLayout(export_layout)
#         self.setLayout(layout)
        
#         self.load_data()

#     def load_data(self):
     
#         """تحميل الطلبات المُرحلة فقط مع أزرار الإرجاع والتشطيب"""
#         import sqlite3

#         # 🔹 جلب الطلبات المرحّلة فقط (غير المشطوبة)
#         conn = sqlite3.connect(self.db.db_path)
#         cursor = conn.cursor()
#         # cursor.execute("SELECT * FROM orders WHERE is_completed = 1 ORDER BY created_datetime ASC")

#         cursor.execute("""
#            SELECT * FROM orders 
#             WHERE is_transferred = 1 AND is_completed = 0
#             ORDER BY created_datetime ASC
#         """)
#         records = cursor.fetchall()
#         conn.close()

#         # تجهيز الجدول
#         self.table.clearContents()
#         self.table.setRowCount(len(records))

#         # تجهيز الجدول
#         self.table.clearContents()
#         self.table.setRowCount(len(records))

#         for i, record in enumerate(records):
#             order_id = record[0]

#             # عرض الأعمدة الرئيسية فقط
#             row_data = [
#                 record[8] or "",     # المسلسل
#                 record[2] or "",     # رقم القاطرة
#                 record[1] or "",     # اسم السائق
#                 record[20] or "",    # رقم الجوال
#                 record[3] or "",     # الكمية
#                 record[5] or "",     # نوع البضاعة
#                 record[4] or "",     # منطقة الوصول
#                 record[12] or "",    # التاجر
#                 record[32] or "",    # المكتب
#                 record[9] or "",     # التأكيد
#                 record[29] or "",    # ملاحظات
#             ]

#             # تعبئة الخلايا
#             for col, val in enumerate(row_data):
#                 cell = QTableWidgetItem(str(val))
#                 cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
#                 cell.setBackground(QColor(200, 255, 200))
#                 self.table.setItem(i, col, cell)

#             # 🔹 زر الإرجاع إلى النهمة
#             return_btn = QPushButton("↩️ إرجاع إلى النهمة")
#             return_btn.setStyleSheet("""
#                 QPushButton {
#                     background-color: #f44336;
#                     color: white;
#                     padding: 5px;
#                     border-radius: 3px;
#                     font-weight: bold;
#                 }
#                 QPushButton:hover {
#                     background-color: #d32f2f;
#                 }
#             """)
#             return_btn.clicked.connect(lambda checked, oid=order_id: self.return_to_nihma(oid))
#             self.table.setCellWidget(i, 11, return_btn)

#     # def load_data(self):
#     #     import sqlite3

#     #     # 🔹 جلب الطلبات غير المُرحلة فقط
#     #     conn = sqlite3.connect(self.db.db_path)
#     #     cursor = conn.cursor()
#     #     cursor.execute("SELECT * FROM orders WHERE is_completed = 1 ORDER BY created_datetime ASC")


#     #     # cursor.execute('SELECT * FROM orders WHERE is_transferred = 0 AND is_completed = 0 ORDER BY created_datetime ASC')

#     #     records = cursor.fetchall()
#     #     conn.close()

#     #     # 🔹 إعادة تحميل حالة الطلبات المُرحلة لتجنب تلوينها خطأً

#     #     records = self.db.get_all_orders()
#     #     self.table.setRowCount(len(records))
        
#     #     for i, record in enumerate(records):
#     #         order_id = record[0]  # الحصول على معرف الطلب

#     #         # البيانات المطلوبة لكشف التشطيب
#     #         row_data = [
#     #             record[8] or "",    # المسلسل (الرقم التسلسلي)
#     #             record[2] or "",    # رقم القاطرة
#     #             record[1] or "",    # اسم السائق
#     #             record[20] or "",   # رقم الجوال
#     #             record[3] or "",    # الكمية
#     #             record[5] or "",    # نوع البضاعة
#     #             record[4] or "",    # منطقة الوصول
#     #             record[12] or "",   # التاجر (اسم التاجر)
#     #             record[32] or "",   # المكتب
#     #             record[9] or "",    # التأكيد (تأكيد الاستلام)
#     #             record[29] or "",   # ملاحظات
#     #         ]
            
#     #         # إضافة البيانات إلى الجدول
#     #         for col, val in enumerate(row_data):
#     #             cell = QTableWidgetItem(str(val))
#     #             cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
#     #             # تلوين الصف إذا كان الطلب مُرحلاً
#     #             if record[0] in self.db.get_transferred_orders():
#     #                 cell.setBackground(QColor(255, 255, 0))  # أصفر
                
#     #             self.table.setItem(i, col, cell)

#     #         # عمود سبب التشطيب
#     #         reason_item = QTableWidgetItem(self.completion_reasons.get(order_id, ""))
#     #         reason_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
#     #         self.table.setItem(i, 11, reason_item)

#     #         # زر التشطيب - العمود 12
#     #         complete_btn = QPushButton("🛑 تشطيب")
#     #         complete_btn.setStyleSheet("""
#     #             QPushButton {
#     #                 background-color: #f44336;
#     #                 color: white;
#     #                 padding: 8px;
#     #                 border-radius: 5px;
#     #                 font-weight: bold;
#     #                 border: 2px solid #d32f2f;
#     #             }
#     #             QPushButton:hover {
#     #                 background-color: #d32f2f;
#     #                 border: 2px solid #b71c1c;
#     #             }
#     #             QPushButton:pressed {
#     #                 background-color: #b71c1c;
#     #             }
#     #         """)
#     #         complete_btn.setFont(QFont("Amiri", 10, QFont.Bold))
#     #         complete_btn.order_id = order_id
#     #         complete_btn.clicked.connect(self.add_completion_reason)
#     #         self.table.setCellWidget(i, 12, complete_btn)

#     def add_completion_reason(self):
#         """إضافة سبب التشطيب"""
#         sender = self.sender()
#         order_id = sender.order_id
        
#         # الحصول على السبب الحالي إذا موجود
#         current_reason = self.completion_reasons.get(order_id, "")
        
#         # فتح نافذة إدخال السبب
#         reason, ok = QInputDialog.getText(
#             self, 
#             "سبب التشطيب", 
#             "أدخل سبب التشطيب:", 
#             text=current_reason
#         )
        
#         if ok and reason:
#             # حفظ السبب
#             self.completion_reasons[order_id] = reason
            
#             # تحديث الجدول
#             self.update_completion_reason(order_id, reason)
            
#             QMessageBox.information(self, "تم الحفظ", "✅ تم حفظ سبب التشطيب بنجاح!")

#     def update_completion_reason(self, order_id, reason):
#         """تحديث سبب التشطيب في الجدول"""
#         for row in range(self.table.rowCount()):
#             widget = self.table.cellWidget(row, 12)  # زر التشطيب
#             if widget and hasattr(widget, 'order_id') and widget.order_id == order_id:
#                 # تحديث خلية سبب التشطيب
#                 reason_item = QTableWidgetItem(reason)
#                 reason_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
#                 self.table.setItem(row, 11, reason_item)
                
#                 # تلوين الصف باللون الأحمر الفاتح للإشارة إلى وجود تشطيب
#                 for col in range(self.table.columnCount()):
#                     item = self.table.item(row, col)
#                     if item:
#                         item.setBackground(QColor(255, 200, 200))  # أحمر فاتح
#                 break

#     def export_to_pdf(self):
#         """تصدير كشف التشطيب إلى PDF"""
#         records = self.db.get_all_orders()
#         if not records:
#             QMessageBox.critical(self, "خطأ", "❌ لا توجد سجلات لتصديرها!")
#             return

#         try:
#             pdf = FPDF()
#             pdf.add_page()
#             pdf.set_auto_page_break(auto=True, margin=15)

#             # إضافة الخط العربي
#             font_path = "assets/fonts/Amiri-Regular.ttf"
#             if not os.path.exists(font_path):
#                 QMessageBox.critical(self, "خطأ", f"❌ لم يتم العثور على الخط:\n{font_path}")
#                 return

#             pdf.add_font("Amiri", "", font_path, uni=True)
#             pdf.set_font("Amiri", size=12)

#             # الهيدر العلوي
#             pdf.set_xy(10, 10)
#             pdf.cell(0, 10, fix_arabic("التاريخ: ________________"), ln=0, align="R")

#             pdf.set_xy(10, 20)
#             pdf.cell(0, 10, fix_arabic("المحترمون"), ln=0, align="L")
#             pdf.cell(0, 10, fix_arabic("الإخوة / الهيئة العامة للنقل"), ln=1, align="R")

#             pdf.ln(5)
#             pdf.cell(0, 10, fix_arabic("فاكس"), ln=True, align="C")

#             # العنوان الرئيسي
#             title = fix_arabic("كشف التشطيب - ضياء اليمن للنقل والاستيراد")
#             pdf.set_font("Amiri", size=14, style='B')
#             pdf.cell(0, 10, title, ln=True, align="C")

#             # إحصائية الطلبات
#             transferred_count = len([r for r in records if r[0] in self.db.get_transferred_orders()])
#             completion_count = len(self.completion_reasons)
#             pdf.set_font("Amiri", size=10)
#             pdf.cell(0, 8, fix_arabic(f"عدد الطلبات: {len(records)} - المُرحلة: {transferred_count} - المشطوبة: {completion_count}"), ln=True, align="C")

#             # فاصل خط
#             pdf.set_line_width(0.5)
#             pdf.line(10, pdf.get_y(), 200, pdf.get_y())
#             pdf.ln(10)

#             # رأس الجدول
#             pdf.set_font("Amiri", size=9, style='B')
#             headers = [
#                 "المسلسل", "رقم القاطرة", "اسم السائق", "رقم الجوال", 
#                 "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", 
#                 "المكتب", "التأكيد", "ملاحظات", "سبب التشطيب"
#             ]
            
#             col_widths = [12, 18, 22, 18, 12, 18, 18, 18, 15, 12, 20, 25]
            
#             # رسم رأس الجدول
#             for width, header in zip(col_widths, headers):
#                 pdf.cell(width, 10, fix_arabic(header), border=1, align="C")
#             pdf.ln()

#             # بيانات الجدول
#             pdf.set_font("Amiri", size=7)
#             for record in records:
#                 order_id = record[0]
#                 completion_reason = self.completion_reasons.get(order_id, "")
                
#                 row_data = [
#                     str(record[8] or ""),    # المسلسل
#                     str(record[2] or ""),    # رقم القاطرة
#                     str(record[1] or ""),    # اسم السائق
#                     str(record[20] or ""),   # رقم الجوال
#                     str(record[3] or ""),    # الكمية
#                     str(record[5] or ""),    # نوع البضاعة
#                     str(record[4] or ""),    # منطقة الوصول
#                     str(record[12] or ""),   # التاجر
#                     str(record[32] or ""),   # المكتب
#                     str(record[9] or ""),    # التأكيد
#                     str(record[29] or ""),   # ملاحظات
#                     completion_reason        # سبب التشطيب
#                 ]
                
#                 for width, cell in zip(col_widths, row_data):
#                     # تقليم النص إذا كان طويلاً
#                     text = str(cell)
#                     if len(text) > 20:
#                         text = text[:17] + '...'
#                     pdf.cell(width, 10, fix_arabic(text), border=1, align="C")
#                 pdf.ln()

#             # التوقيع
#             pdf.ln(15)
#             pdf.set_font("Amiri", size=11)
#             pdf.cell(0, 10, fix_arabic("وتقبلوا خالص تحياتنا"), ln=True, align="C")
#             pdf.cell(0, 10, fix_arabic("مكتب ضياء اليمن"), ln=True, align="L")

#             # حفظ الملف
#             default_name = f"كشف_التشطيب_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#             file_path, _ = QFileDialog.getSaveFileName(
#                 self, "حفظ كشف التشطيب", default_name, "PDF Files (*.pdf)"
#             )

#             if file_path:
#                 pdf.output(file_path)
#                 QMessageBox.information(self, "نجاح", f"✅ تم حفظ كشف التشطيب كـ PDF:\n{file_path}")
#             else:
#                 QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ كشف التشطيب.")

#         except Exception as e:
#             QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")


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
        self.completion_reasons = {}  # لتخزين أسباب التشطيب
        self.setWindowTitle("كشف التشطيب")
        self.setGeometry(100, 100, 1500, 700)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان الشاشة
        title = QLabel("كشف التشطيب")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: #9C27B0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # جدول كشف التشطيب
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "المسلسل", "رقم القاطرة", "اسم السائق", "رقم الجوال", 
            "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", 
            "المكتب", "التأكيد", "ملاحظات", "سبب التشطيب", "إرجاع للإدارة"
        ])
        self.table.setFont(QFont("Amiri", 10))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        
        # ضبط أبعاد الأعمدة
        self.table.setColumnWidth(0, 80)   # المسلسل
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
        self.table.setColumnWidth(11, 200) # سبب التشطيب
        self.table.setColumnWidth(12, 120) # إرجاع للإدارة
        
        layout.addWidget(self.table)

        # أزرار التصدير
        export_layout = QHBoxLayout()
        
        export_btn = QPushButton("📸 تصدير كشف التشطيب PDF")
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
        # export_btn.clicked.connect(self.export_to_pdf)
        # export_layout.addWidget(export_btn)
        
        layout.addLayout(export_layout)
        self.setLayout(layout)
        
        self.load_data()

    def load_data(self):
        """تحميل الطلبات المشطوبة فقط"""
        import sqlite3

        # 🔹 جلب الطلبات المشطوبة فقط
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            WHERE is_completed = 1
            ORDER BY created_datetime ASC
        """)
        records = cursor.fetchall()
        conn.close()

        # تجهيز الجدول
        self.table.clearContents()
        self.table.setRowCount(len(records))

        for i, record in enumerate(records):
            order_id = record[0]

            # عرض الأعمدة الرئيسية فقط
            row_data = [
                record[8] or "",     # المسلسل
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
                cell.setBackground(QColor(255, 200, 200))  # لون أحمر فاتح للطلبات المشطوبة
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

    def return_to_nihma(self, order_id):
        """إرجاع الطلب من كشف التشطيب إلى كشف النهمة"""
        try:
            # تحديث حالة الطلب
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET is_completed = 0 WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()

            # إعادة تحميل الجدول
            self.load_data()

            QMessageBox.information(self, "تم الإرجاع", f"✅ تم إرجاع الطلب رقم {order_id} إلى كشف النهمة بنجاح.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ حدث خطأ أثناء الإرجاع:\n{str(e)}")

    def return_to_management(self, order_id):
        """إرجاع الطلب من كشف التشطيب إلى إدارة الطلبات"""
        try:
            # تحديث حالة الطلب
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET is_completed = 0 WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()

            # إعادة تحميل الجدول
            self.load_data()

            QMessageBox.information(self, "تم الإرجاع", f"✅ تم إرجاع الطلب رقم {order_id} إلى إدارة الطلبات بنجاح.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ حدث خطأ أثناء الإرجاع:\n{str(e)}")

    def add_completion_reason(self):
        """إضافة سبب التشطيب"""
        sender = self.sender()
        order_id = sender.order_id
        
        # الحصول على السبب الحالي إذا موجود
        current_reason = self.completion_reasons.get(order_id, "")
        
        # فتح نافذة إدخال السبب
        reason, ok = QInputDialog.getText(
            self, 
            "سبب التشطيب", 
            "أدخل سبب التشطيب:", 
            text=current_reason
        )
        
        if ok and reason:
            # حفظ السبب
            self.completion_reasons[order_id] = reason
            
            # تحديث الجدول
            self.update_completion_reason(order_id, reason)
            
            QMessageBox.information(self, "تم الحفظ", "✅ تم حفظ سبب التشطيب بنجاح!")

    def update_completion_reason(self, order_id, reason):
        """تحديث سبب التشطيب في الجدول"""
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 12)  # زر الإرجاع
            if widget and hasattr(widget, 'order_id') and widget.order_id == order_id:
                # تحديث خلية سبب التشطيب
                reason_item = QTableWidgetItem(reason)
                reason_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                reason_item.setBackground(QColor(255, 200, 200))
                self.table.setItem(row, 11, reason_item)
                break

    def export_to_pdf(self):
        """تصدير كشف التشطيب إلى PDF"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE is_completed = 1 ORDER BY created_datetime ASC")
        records = cursor.fetchall()
        conn.close()

        if not records:
            QMessageBox.critical(self, "خطأ", "❌ لا توجد سجلات مشطوبة لتصديرها!")
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # إضافة الخط العربي
            font_path = "assets/fonts/Amiri-Regular.ttf"
            if not os.path.exists(font_path):
                QMessageBox.critical(self, "خطأ", f"❌ لم يتم العثور على الخط:\n{font_path}")
                return

            pdf.add_font("Amiri", "", font_path, uni=True)
            pdf.set_font("Amiri", size=12)

            # الهيدر العلوي
            pdf.set_xy(10, 10)
            pdf.cell(0, 10, fix_arabic("التاريخ: ________________"), ln=0, align="R")

            pdf.set_xy(10, 20)
            pdf.cell(0, 10, fix_arabic("المحترمون"), ln=0, align="L")
            pdf.cell(0, 10, fix_arabic("الإخوة / الهيئة العامة للنقل"), ln=1, align="R")

            pdf.ln(5)
            pdf.cell(0, 10, fix_arabic("فاكس"), ln=True, align="C")

            # العنوان الرئيسي
            title = fix_arabic("كشف التشطيب - ضياء اليمن للنقل والاستيراد")
            pdf.set_font("Amiri", size=14, style='B')
            pdf.cell(0, 10, title, ln=True, align="C")

            # إحصائية الطلبات
            completion_count = len(records)
            pdf.set_font("Amiri", size=10)
            pdf.cell(0, 8, fix_arabic(f"عدد الطلبات المشطوبة: {completion_count}"), ln=True, align="C")

            # فاصل خط
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(10)

            # رأس الجدول
            pdf.set_font("Amiri", size=9, style='B')
            headers = [
                "المسلسل", "رقم القاطرة", "اسم السائق", "رقم الجوال", 
                "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", 
                "المكتب", "التأكيد", "ملاحظات", "سبب التشطيب"
            ]
            
            col_widths = [12, 18, 22, 18, 12, 18, 18, 18, 15, 12, 20, 25]
            
            # رسم رأس الجدول
            for width, header in zip(col_widths, headers):
                pdf.cell(width, 10, fix_arabic(header), border=1, align="C")
            pdf.ln()

            # بيانات الجدول
            pdf.set_font("Amiri", size=7)
            for record in records:
                order_id = record[0]
                completion_reason = self.completion_reasons.get(order_id, "")
                
                row_data = [
                    str(record[8] or ""),    # المسلسل
                    str(record[2] or ""),    # رقم القاطرة
                    str(record[1] or ""),    # اسم السائق
                    str(record[20] or ""),   # رقم الجوال
                    str(record[3] or ""),    # الكمية
                    str(record[5] or ""),    # نوع البضاعة
                    str(record[4] or ""),    # منطقة الوصول
                    str(record[12] or ""),   # التاجر
                    str(record[32] or ""),   # المكتب
                    str(record[9] or ""),    # التأكيد
                    str(record[29] or ""),   # ملاحظات
                    completion_reason        # سبب التشطيب
                ]
                
                for width, cell in zip(col_widths, row_data):
                    # تقليم النص إذا كان طويلاً
                    text = str(cell)
                    if len(text) > 20:
                        text = text[:17] + '...'
                    pdf.cell(width, 10, fix_arabic(text), border=1, align="C")
                pdf.ln()

            # التوقيع
            pdf.ln(15)
            pdf.set_font("Amiri", size=11)
            pdf.cell(0, 10, fix_arabic("وتقبلوا خالص تحياتنا"), ln=True, align="C")
            pdf.cell(0, 10, fix_arabic("مكتب ضياء اليمن"), ln=True, align="L")

            # حفظ الملف
            default_name = f"كشف_التشطيب_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ كشف التشطيب", default_name, "PDF Files (*.pdf)"
            )

            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "نجاح", f"✅ تم حفظ كشف التشطيب كـ PDF:\n{file_path}")
            else:
                QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ كشف التشطيب.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")