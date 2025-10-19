from PyQt5.QtWidgets import QDialog, QComboBox,QTabWidget, QWidget, QVBoxLayout,  QTextEdit,QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from database import Database
import os
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from add_order_dialog import AddOrderDialog
from addmar import AddmarScreen
from babel.dates import format_datetime
import sqlite3
from members import MembersListDialog

def fix_arabic(text):
    if isinstance(text, str) and any('\u0600' <= c <= '\u06FF' for c in text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text


class PasswordDialog(QDialog):
    def __init__(self, parent=None, title="🔐 كلمة المرور", message="🔐 أدخل كلمة المرور"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 300, 150)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.message = message
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # عنوان النافذة
        title = QLabel(self.message)
        title.setFont(QFont("Amiri", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # حقل كلمة المرور
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("كلمة المرور...")
        layout.addWidget(self.password_input)
        
        # أزرار
        button_layout = QHBoxLayout()
        
        confirm_btn = QPushButton("✅ تأكيد")
        confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(confirm_btn)
        
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_password(self):
        return self.password_input.text()


class NihmeReportScreen(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.transferred_orders = self.db.get_transferred_orders()
        self.setWindowTitle("📄 كشف النهمة")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # عنوان الشاشة
        title = QLabel("📄 كشف النهمة")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

       
       
       

        # أزرار التصفية
        filter_layout = QHBoxLayout()
        
        filter_all_btn = QPushButton("📋 جميع الطلبات")
        filter_all_btn.setFont(QFont("Amiri", 12))
        filter_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        filter_all_btn.clicked.connect(lambda: self.filter_orders("all"))
        filter_layout.addWidget(filter_all_btn)
        
        filter_transferred_btn = QPushButton("✅ المُرحلة")
        filter_transferred_btn.setFont(QFont("Amiri", 12))
        filter_transferred_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        filter_transferred_btn.clicked.connect(lambda: self.filter_orders("transferred"))
        filter_layout.addWidget(filter_transferred_btn)

        
        filter_not_transferred_btn = QPushButton("⏳ غير المُرحلة")
        filter_not_transferred_btn.setFont(QFont("Amiri", 12))
        filter_not_transferred_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        filter_not_transferred_btn.clicked.connect(lambda: self.filter_orders("not_transferred"))
        filter_layout.addWidget(filter_not_transferred_btn)
        
        main_layout.addLayout(filter_layout)

        # جدول كشف النهمة - تم تحديث عدد الأعمدة
        self.table = QTableWidget()
        self.table.setColumnCount(18)  # تم زيادة عدد الأعمدة من 10 إلى 17
        self.table.setHorizontalHeaderLabels([
            "الرقم التسلسلي", "اسم السائق", "رقم القاطرة", "الجوال", 
            "نوع القاطرة", "الانتساب", "التاريخ والوقت", "التوقيف", "الحالة", 
            "نوع البضاعة", "الكمية", "منطقة الوصول", "التاجر", "اسم المكتب", 
            "التاكيد", "الملاحظة", "اضف للتاكيد","تشطيب"
        ])
        self.table.setFont(QFont("Amiri", 8))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        
        # ضبط أبعاد الأعمدة الجديدة
        self.table.setColumnWidth(0, 100)   # الرقم التسلسلي
        self.table.setColumnWidth(1, 150)   # اسم السائق
        self.table.setColumnWidth(2, 120)   # رقم القاطرة
        self.table.setColumnWidth(3, 120)   # الجوال
        self.table.setColumnWidth(4, 120)   # نوع القاطرة
        self.table.setColumnWidth(5, 100)   # الانتساب
        self.table.setColumnWidth(6, 150)   # التاريخ والوقت
        self.table.setColumnWidth(7, 100)   # التوقيف
        self.table.setColumnWidth(8, 120)   # الحالة
        self.table.setColumnWidth(9, 120)   # نوع البضاعة
        self.table.setColumnWidth(10, 80)   # الكمية
        self.table.setColumnWidth(11, 120)  # منطقة الوصول
        self.table.setColumnWidth(12, 120)  # التاجر
        self.table.setColumnWidth(13, 120)  # اسم المكتب
        self.table.setColumnWidth(14, 80)   # التاكيد
        self.table.setColumnWidth(15, 150)  # الملاحظة
        self.table.setColumnWidth(16, 100)  # اضف للتاكيد
        self.table.setColumnWidth(17, 100)  # تشطيب
        main_layout.addWidget(self.table)

        # أزرار التصدير
        export_layout = QHBoxLayout()
        from order import regist
        
        tabs = QTabWidget(self)
       
        main_tabs = regist(self.db)
        ta = main_tabs.create_main_tab()
        tabs.addTab(ta, "التسجيل والبحث")
        
        export_layout.addWidget(tabs)
       
        
        # تبويب التسجيل والبحث
    

    
        # تبويب التسجيل والبحث

        
        export_btn = QPushButton("📸 تصدير جميع الطلبات PDF")
        export_btn.setFont(QFont("Amiri", 14))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F; 
                color: white; 
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        
        # زر فتح كشف التشطيب
        open_addmar_btn = QPushButton("📋 كشف التشطيب")
        open_addmar_btn.setFont(QFont("Amiri", 14))
        open_addmar_btn.setStyleSheet("""
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
        open_addmar_btn.clicked.connect(self.open_addmar_screen)
        export_layout.addWidget(open_addmar_btn)
        export_btn.clicked.connect(self.export_to_pdf)
        export_layout.addWidget(export_btn)


        hh = QPushButton()
        hh.clicked.connect(self.open_search)
        export_layout.addWidget(hh)
        
        export_transferred_btn = QPushButton("📋 تصدير الطلبات المُرحلة PDF")
        export_transferred_btn.setFont(QFont("Amiri", 14))
        export_transferred_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        export_transferred_btn.clicked.connect(self.export_transferred_to_pdf)
        export_layout.addWidget(export_transferred_btn)
        
        main_layout.addLayout(export_layout)
        self.setLayout(main_layout)
        
        self.load_data()
    def open_search(self):
        from order import  regist
        m = regist(self.db)
        m.create_main_tab()
                
      

    def open_addmar_screen(self):
        """فتح شاشة كشف التشطيب"""
        dialog = AddmarScreen(self.db)
        dialog.exec_()
        
    def mark_as_completed(self):
        """تشطيب الطلب (إلغاؤه ونقله إلى كشف التشطيب)"""
        sender = self.sender()
        if not hasattr(sender, "order_id"):
            QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على رقم الطلب!")
            return

        order_id = sender.order_id

        reply = QMessageBox.question(
            self,
            "تأكيد التشطيب",
            "هل أنت متأكد أنك تريد تشطيب هذا الطلب؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE orders SET is_completed = 1 WHERE id = ?", (order_id,))
                conn.commit()
                conn.close()

                # تحديث الجدول لإخفاء الطلب المشطوب
                self.load_data()

                QMessageBox.information(self, "تم التشطيب", "✅ تم تشطيب الطلب ونقله إلى كشف التشطيب.")

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"❌ فشل في تشطيب الطلب:\n{str(e)}")

    def load_data(self):
        """تحميل الطلبات غير المُرحلة وغير المشطوبة فقط إلى جدول كشف النهمة"""
        import sqlite3

        # 🔹 جلب الطلبات غير المُرحلة وغير المشطوبة فقط
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE is_transferred = 0 AND is_completed = 0 ORDER BY created_datetime ASC')

        records = cursor.fetchall()
        conn.close()

        # 🔹 إعادة تحميل حالة الطلبات المُرحلة لتجنب تلوينها خطأً
        self.transferred_orders = self.db.get_transferred_orders()

        # 🔹 مسح الجدول قبل إعادة تعبئته
        self.table.clearContents()
        self.table.setRowCount(len(records))

        for i, record in enumerate(records):
            # معالجة التاريخ
            try:
     
                arrival_date = datetime.fromtimestamp(record[6]).strftime("%Y-%m-%d %H:%M") if record[6] else ""
            except:
                arrival_date = str(record[6] or "")
                ###
              
                ##

            # البيانات الأساسية
            row_data = [
                record[8] if len(record) > 8 else "",    # الرقم التسلسلي
                record[1] if len(record) > 1 else "",    # اسم السائق
                record[2] if len(record) > 2 else "",    # رقم القاطرة
                record[20] if len(record) > 20 else "",  # الجوال
                record[7] if len(record) > 7 else "",    # نوع القاطرة
                record[30] if len(record) > 30 else "",  # الانتساب
                arrival_date,                            # التاريخ والوقت
                record[31] if len(record) > 31 else "",  # التوقيف
            ]

            # --- تعبئة البيانات الأساسية ---
            for col, val in enumerate(row_data):
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, col, cell)

            # --- عمود حالة الترحيل ---
            status_item = QTableWidgetItem("⏳ بانتظار الترحيل")
            status_item.setBackground(QColor(255, 255, 255))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 8, status_item)

            # --- الأعمدة الإضافية (9–15) ---
            new_data = [
                record[5] if len(record) > 5 else "",    # نوع البضاعة
                record[3] if len(record) > 3 else "",    # الكمية
                record[4] if len(record) > 4 else "",    # منطقة الوصول
                record[12] if len(record) > 12 else "",  # التاجر
                record[32] if len(record) > 32 else "",  # المكتب
                record[9] if len(record) > 9 else "",    # التأكيد
                record[29] if len(record) > 29 else "",  # الملاحظات
            ]

            for col, val in enumerate(new_data, start=9):
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, col, cell)

            # --- زر التعديل ---
            edit_btn = QPushButton("تعديل")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            edit_btn.order_id = record[0]
            edit_btn.clicked.connect(self.edit_order)
            self.table.setCellWidget(i, 16, edit_btn)

            # زر التشطيب - العمود 17
            complete_btn = QPushButton("🛑 تشطيب")
            complete_btn.setStyleSheet("""
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
            complete_btn.order_id = record[0]
            complete_btn.clicked.connect(self.mark_as_completed)
            self.table.setCellWidget(i, 17, complete_btn)

            
    def edit_orders(self):
        """عند الضغط على زر تعديل يتم فتح شاشة إدارة الطلبات وإخفاء جدول النهمة"""
        sender = self.sender()
        if not hasattr(sender, 'order_id'):
            QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على معرف الطلب!")
            return

        order_id = sender.order_id

        # جلب بيانات الطلب من قاعدة البيانات
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب!")
                return

            # 🟡 إخفاء الجدول مؤقتاً
            self.table.setVisible(False)

            # 🟢 فتح شاشة إدارة الطلبات managem.py
            from managem import AddmarScreen
            dialog = AddmarScreen(self.db)
            dialog.exec_()

            # بعد إغلاق شاشة الإدارة، أعد إظهار الجدول وتحديث البيانات
            self.table.setVisible(True)
            self.load_data()
            QMessageBox.information(self, "نجاح", "✅ تم تحديث البيانات بنجاح!")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في تحميل بيانات الطلب:\n{str(e)}")

    def edit_order(self):
        """تعديل الطلب - الإصدار المبسط"""
        # الحصول على الزر الذي تم النقر عليه
        sender = self.sender()
        if not hasattr(sender, 'order_id'):
            QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على معرف الطلب!")
            return

        order_id = sender.order_id

        # جلب بيانات الطلب من قاعدة البيانات
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب!")
                return

            # فتح نافذة التعديل المبسطة
            dialog = SimpleEditDialog(self.db, order_id, order, self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_data()  # إعادة تحميل البيانات بعد التعديل
                QMessageBox.information(self, "نجاح", "✅ تم تعديل البيانات بنجاح!")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في تحميل بيانات الطلب:\n{str(e)}")

    def filter_orders(self, filter_type):
        """تصفية الطلبات حسب حالة الترحيل"""
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 8)  # عمود الحالة
            is_transferred = status_item and status_item.text() == "✅ مُرحل"
            
            if filter_type == "all":
                self.table.setRowHidden(row, False)
            elif filter_type == "transferred":
                self.table.setRowHidden(row, not is_transferred)
            elif filter_type == "not_transferred":
                self.table.setRowHidden(row, is_transferred)

    def export_to_pdfa(self):
        """تصدير الطلبات الخاصة بكشف النهمة فقط (غير المُرحلة وغير المشطوبة) إلى PDF"""
        import sqlite3

        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            WHERE is_transferred = 0 AND is_completed = 0
            ORDER BY created_datetime ASC
        """)
        records = cursor.fetchall()
        conn.close()

        if not records:
            QMessageBox.critical(self, "خطأ", "❌ لا توجد طلبات في كشف النهمة لتصديرها!")
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # إعداد الخط العربي
            font_path = "assets/fonts/Amiri-Regular.ttf"
            if not os.path.exists(font_path):
                QMessageBox.critical(self, "خطأ", f"❌ لم يتم العثور على الخط:\n{font_path}")
                return

            pdf.add_font("Amiri", "", font_path, uni=True)
            pdf.set_font("Amiri", size=14)

            # العنوان والهيدر
            pdf.cell(0, 10, fix_arabic("📄 ضياء اليمن للنقل والاستيراد - كشف النهمة"), ln=True, align="C")
            pdf.ln(5)

            # رؤوس الأعمدة
            headers = ["الرقم التسلسلي", "اسم السائق", "رقم القاطرة", "الجوال", "نوع القاطرة", "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", "اسم المكتب"]
            col_widths = [15, 25, 25, 25, 25, 20, 25, 25, 25, 25]
            headers = headers[::-1]
            col_widths = col_widths[::-1]

                        # حساب عرض الجدول الكامل لتوسيطه
            table_width = sum(col_widths)
            page_width = pdf.w - 2 * pdf.l_margin
            start_x = (page_width - table_width) / 2 + pdf.l_margin

                        # --- رسم رأس الجدول ---
            pdf.set_x(start_x)
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, fix_arabic(header), border=1, align="C")
            pdf.ln()


            # البيانات
            for record in records:
                row_data = [
                    str(record[8] if len(record) > 8 else ""),   # الرقم التسلسلي
                    str(record[1] if len(record) > 1 else ""),   # اسم السائق
                    str(record[2] if len(record) > 2 else ""),   # رقم القاطرة
                    str(record[20] if len(record) > 20 else ""), # الجوال
                    str(record[7] if len(record) > 7 else ""),   # نوع القاطرة
                    str(record[3] if len(record) > 3 else ""),   # الكمية
                    str(record[5] if len(record) > 5 else ""),   # نوع البضاعة
                    str(record[4] if len(record) > 4 else ""),   # منطقة الوصول
                    str(record[12] if len(record) > 12 else ""), # التاجر
                    str(record[32] if len(record) > 32 else ""), # المكتب
                ]
                row_data = row_data[::-1]
                pdf.set_x(start_x)
                for j, cell in enumerate(row_data):
                    pdf.cell(col_widths[j], 10, fix_arabic(cell), border=1, align="C")
                pdf.ln()

            pdf.ln(10)
            pdf.set_font("Amiri", size=11)
            pdf.cell(0, 10, fix_arabic("توقيع المشرف: ____________________"), ln=True, align="L")

            # حفظ الملف
            default_name = f"كشف_النهمة_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(self, "حفظ كشف النهمة", default_name, "PDF Files (*.pdf)")
            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "نجاح", f"✅ تم حفظ كشف النهمة بنجاح:\n{file_path}")
            else:
                QMessageBox.warning(self, "إلغاء", "❌ لم يتم حفظ الملف.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في تصدير PDF:\n{str(e)}")

    def export_to_pdf(self):
        import sqlite3

        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            WHERE is_transferred = 0 AND is_completed = 0
            ORDER BY created_datetime ASC
        """)
        records = cursor.fetchall()
        conn.close()

        # if not records:
        #     QMessageBox.critical(self, "خطأ", "❌ لا توجد طلبات في كشف النهمة لتصديرها!")
        #     return
        # records = self.db.get_all_orders()
        # if not records:
        #     QMessageBox.critical(self, "خطأ", "❌ لا توجد سجلات لتصديرها!")
        #     return

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
            pdf.set_font("Amiri", size=14)

            # --- الهيدر العلوي ---
            pdf.set_xy(10, 10)
            pdf.cell(0, 10, fix_arabic("التاريخ: ________________"), ln=0, align="R")

            pdf.set_xy(10, 20)
            pdf.cell(0, 10, fix_arabic("المحترمون"), ln=0, align="L")
            pdf.cell(0, 10, fix_arabic("الإخوة / الهيئة العامة للنقل"), ln=1, align="R")

            pdf.ln(5)
            pdf.cell(0, 10, fix_arabic("فاكس"), ln=True, align="C")

            title = fix_arabic("📄 ضياء اليمن للنقل والاستيراد - كشف النهمة")
            pdf.set_font("Amiri", size=16)
            pdf.cell(0, 10, title, ln=True, align="C")

            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

            # --- رأس الجدول ---
            pdf.set_font("Amiri", size=7)

            # تحديث الرؤوس لتشمل الأعمدة الجديدة
            headers = ["الرقم التسلسلي", "اسم السائق", "رقم القاطرة", "الجوال", "نوع القاطرة", "الكمية", "نوع البضاعة", "منطقة الوصول", "التاجر", "اسم المكتب"]
            col_widths = [15, 20, 20, 20, 20, 20, 20, 20, 20, 20]
            headers = headers[::-1]
            col_widths = col_widths[::-1]

            # حساب عرض الجدول الكامل لتوسيطه
            table_width = sum(col_widths)
            page_width = pdf.w - 2 * pdf.l_margin
            start_x = (page_width - table_width) / 2 + pdf.l_margin

            # --- رسم رأس الجدول ---
            pdf.set_x(start_x)
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, fix_arabic(header), border=1, align="C")
            pdf.ln()

            # --- بيانات الجدول ---
            for record in records:
                try:
                    arrival_date = datetime.fromtimestamp(record[6]).strftime("%Y-%m-%d %H:%M") if record[6] else ""
                except:
                    arrival_date = str(record[6] or "")

                # تحديث البيانات لتشمل الأعمدة الجديدة مع فحص الطول
                row_data = [
                  
                    str(record[8] if len(record) > 8 else ""),   # الرقم التسلسلي
                    str(record[1] if len(record) > 1 else ""),   # اسم السائق
                    str(record[2] if len(record) > 2 else ""),   # رقم القاطرة
                    str(record[20] if len(record) > 20 else ""), # الجوال
                    str(record[7] if len(record) > 7 else ""),   # نوع القاطرة
                    str(record[3] if len(record) > 3 else ""),   # الكمية
                    str(record[5] if len(record) > 5 else ""),   # نوع البضاعة
                    str(record[4] if len(record) > 4 else ""),   # منطقة الوصول
                    str(record[12] if len(record) > 12 else ""), # التاجر
                    str(record[32] if len(record) > 32 else ""), # المكتب
                ]

                row_data = row_data[::-1]

                # توسيط الصفوف أيضا
                pdf.set_x(start_x)
                for j, cell in enumerate(row_data):
                    pdf.cell(col_widths[j], 10, fix_arabic(cell), border=1, align="C")
                pdf.ln()

            # --- التوقيع ---
            pdf.ln(15)
            pdf.cell(0, 10, fix_arabic("وتقبلوا خالص تحياتنا"), ln=True, align="C")
            pdf.cell(0, 10, fix_arabic("مكتب ضياء اليمن"), ln=True, align="L")

            # --- حفظ الملف ---
            default_name = f"كشف_النهمة_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ كشف النهمة", default_name, "PDF Files (*.pdf)"
            )

            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "نجاح", f"✅ تم حفظ كشف النهمة كـ PDF:\n{file_path}")
            else:
                QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ كشف النهمة.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")

    def export_transferred_to_pdf(self):
        """تصدير الطلبات المُرحلة إلى PDF مع البيانات الجديدة"""
        records = self.db.get_all_orders()
        transferred_records = [record for record in records if record[0] in self.transferred_orders]

        if not transferred_records:
            QMessageBox.critical(self, "خطأ", "❌ لا توجد طلبات مُرحلة لتصديرها!")
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
            pdf.set_font("Amiri", size=14)

            # --- الهيدر العلوي ---
            pdf.set_xy(10, 10)
            pdf.cell(0, 10, fix_arabic("التاريخ: ________________"), ln=0, align="R")

            pdf.set_xy(10, 20)
            pdf.cell(0, 10, fix_arabic("المحترمون"), ln=0, align="L")
            pdf.cell(0, 10, fix_arabic("الإخوة / الهيئة العامة للنقل"), ln=1, align="R")

            pdf.ln(5)
            pdf.cell(0, 10, fix_arabic("فاكس"), ln=True, align="C")

            title = fix_arabic("📄 ضياء اليمن للنقل والاستيراد - كشف النهمة (الطلبات المُرحلة)")
            pdf.set_font("Amiri", size=16)
            pdf.cell(0, 10, title, ln=True, align="C")

            # فاصل خط
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

            # --- رأس الجدول ---
            pdf.set_font("Amiri", size=8)
            
            # تحديث الرؤوس لتشمل الأعمدة الجديدة
            headers = ["الرقم التسلسلي", "اسم السائق", "رقم القاطرة", "الجوال", "نوع القاطرة", "الانتساب", "التاريخ والوقت", "التوقيف", "نوع البضاعة", "الكمية", "منطقة الوصول", "التاجر", "اسم المكتب"]
            col_widths = [15, 20, 20, 20, 20, 20, 20, 20, 20, 15, 20, 20, 20]

            # قلب الأعمدة (من اليمين إلى اليسار)
            headers = headers[::-1]
            col_widths = col_widths[::-1]

            # حساب عرض الجدول لتوسيطه
            table_width = sum(col_widths)
            page_width = pdf.w - 2 * pdf.l_margin
            start_x = (page_width - table_width) / 2 + pdf.l_margin

            # --- رسم رأس الجدول ---
            pdf.set_x(start_x)
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, fix_arabic(header), border=1, align="C")
            pdf.ln()

            # --- بيانات الجدول ---
            for record in transferred_records:
                try:
                    arrival_date = datetime.fromtimestamp(record[6]).strftime("%Y-%m-%d %H:%M") if record[6] else ""
                except:
                    arrival_date = str(record[6] or "")

                # تحديث البيانات لتشمل الأعمدة الجديدة مع فحص الطول
                row_data = [
                    str(record[8] if len(record) > 8 else ""),   # الرقم التسلسلي
                    str(record[1] if len(record) > 1 else ""),   # اسم السائق
                    str(record[2] if len(record) > 2 else ""),   # رقم القاطرة
                    str(record[20] if len(record) > 20 else ""),  # الجوال
                    str(record[7] if len(record) > 7 else ""),   # نوع القاطرة
                    str(record[30] if len(record) > 30 else ""),  # الانتساب
                    arrival_date,           # التاريخ والوقت
                    str(record[31] if len(record) > 31 else ""),  # التوقيف
                    str(record[32] if len(record) > 32 else ""),  # نوع البضاعة
                    str(record[33] if len(record) > 33 else ""),  # الكمية
                    str(record[34] if len(record) > 34 else ""),  # منطقة الوصول
                    str(record[35] if len(record) > 35 else ""),  # التاجر
                    str(record[36] if len(record) > 36 else ""),  # اسم المكتب
                ]

                # قلب الصف لتتوافق مع الأعمدة
                row_data = row_data[::-1]

                pdf.set_x(start_x)
                for j, cell in enumerate(row_data):
                    pdf.cell(col_widths[j], 10, fix_arabic(cell), border=1, align="C")
                pdf.ln()

            # --- التوقيع ---
            pdf.ln(15)
            pdf.cell(0, 10, fix_arabic("وتقبلوا خالص تحياتنا"), ln=True, align="C")
            pdf.cell(0, 10, fix_arabic("مكتب ضياء اليمن"), ln=True, align="L")

            # --- حفظ الملف ---
            default_name = f"كشف_النهمة_المُرحلة_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ كشف النهمة المُرحلة", default_name, "PDF Files (*.pdf)"
            )

            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "نجاح", f"✅ تم حفظ كشف النهمة المُرحلة كـ PDF:\n{file_path}")
            else:
                QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ كشف النهمة المُرحلة.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")

class SimpleEditDialog(QDialog):
    def __init__(self, db, order_id, order_data, parent=None):
        super().__init__(parent)
        self.db = db
        self.order_id = order_id
        self.order_data = order_data
        self.setWindowTitle("تعديل بيانات الطلب")
        self.setGeometry(150, 150, 600, 500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # عنوان النافذة
        title = QLabel("تعديل بيانات الطلب - كشف النهمة")
        title.setFont(QFont("Amiri", 16, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # الحقول المطلوبة فقط
        form_layout = QGridLayout()

        # نوع البضاعة
        form_layout.addWidget(QLabel("نوع البضاعة:"), 0, 0)
        self.cargo_type = QLineEdit()
        form_layout.addWidget(self.cargo_type, 0, 1)

        # الكمية
        form_layout.addWidget(QLabel("الكمية:"), 1, 0)
        self.quantity = QLineEdit()
        form_layout.addWidget(self.quantity, 1, 1)

        # منطقة الوصول
        form_layout.addWidget(QLabel("منطقة الوصول:"), 2, 0)
        self.arrival_area = QLineEdit()
        form_layout.addWidget(self.arrival_area, 2, 1)

        # التاجر
        form_layout.addWidget(QLabel("التاجر:"), 3, 0)
        self.merchant_name = QLineEdit()
        form_layout.addWidget(self.merchant_name, 3, 1)

        # اسم المكتب
        form_layout.addWidget(QLabel("اسم المكتب:"), 4, 0)
        self.office = QLineEdit()
        form_layout.addWidget(self.office, 4, 1)

        # التاكيد
        form_layout.addWidget(QLabel("التاكيد:"), 5, 0)
        self.receipt_confirmation = QComboBox()
        self.receipt_confirmation.addItems(["مؤكد", "في الانتظار", "ملغى"])
        form_layout.addWidget(self.receipt_confirmation, 5, 1)

        # الملاحظة
        form_layout.addWidget(QLabel("الملاحظة:"), 6, 0)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        form_layout.addWidget(self.notes, 6, 1)

        layout.addLayout(form_layout)

        # أزرار الحفظ والإلغاء
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 حفظ التعديلات")
        save_btn.setFont(QFont("Amiri", 14))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.setFont(QFont("Amiri", 14))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_current_data()

    def load_current_data(self):
        """تحميل البيانات الحالية في الحقول"""
        # استخدام الفهرس الصحيح بناءً على هيكل قاعدة البيانات
        self.cargo_type.setText(str(self.order_data[5] or ""))  # نوع البضاعة
        self.quantity.setText(str(self.order_data[3] or ""))           # الكمية
        self.arrival_area.setText(str(self.order_data[4] or ""))       # منطقة الوصول
        self.merchant_name.setText(str(self.order_data[12] or ""))     # التاجر
        self.office.setText(str(self.order_data[32] or ""))            # اسم المكتب
        self.receipt_confirmation.setCurrentText(str(self.order_data[9] or ""))  # التاكيد
        self.notes.setPlainText(str(self.order_data[29] or ""))        # الملاحظة
    def save_changes(self):
        """حفظ التعديلات في قاعدة البيانات وإخفاء الصف من كشف النهمة"""
        try:
            updated_data = (
                self.quantity.text(),           # الكمية
                self.arrival_area.text(),       # منطقة الوصول
                self.cargo_type.text(),         # نوع البضاعة
                self.merchant_name.text(),      # التاجر
                self.receipt_confirmation.currentText(),  # التاكيد
                self.notes.toPlainText(),       # الملاحظة
                self.office.text(),             # اسم المكتب
                self.order_id                   # معرف الطلب للتحديث
            )

            if self.update_order_in_db(updated_data):
                # ✅ تم الحفظ بنجاح
                QMessageBox.information(self, "نجاح", "✅ تم تعديل البيانات بنجاح!")

                # 🔹 إخفاء الصف المعدل من جدول النهمة
                if self.parent() and hasattr(self.parent(), "table"):
                    table = self.parent().table
                    for row in range(table.rowCount()):
                        item = table.cellWidget(row, 16)
                        if hasattr(item, "order_id") and item.order_id == self.order_id:
                            table.setRowHidden(row, True)
                            break

                # 🔹 فتح شاشة إدارة الطلبات مع الطلب المعدل فقط
                from managem import AddmarScreen
                dialog = AddmarScreen(self.db)
                dialog.transfer_order(self.order_id)
                dialog.exec_()

                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "❌ فشل في تعديل البيانات!")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ حدث خطأ أثناء الحفظ:\n{str(e)}")

    def save_changess(self):
        """حفظ التعديلات في قاعدة البيانات"""
        try:
            # جمع البيانات من الحقول
            updated_data = (
                self.quantity.text(),           # الكمية
                self.arrival_area.text(),       # منطقة الوصول
                self.cargo_type.text(),  # نوع البضاعة
                self.merchant_name.text(),      # التاجر
                self.receipt_confirmation.currentText(),  # التاكيد
                self.notes.toPlainText(),       # الملاحظة
                self.office.text(),             # اسم المكتب
                self.order_id                   # معرف الطلب للتحديث
            )

            # تحديث قاعدة البيانات
            if self.update_order_in_db(updated_data):
                QMessageBox.information(self, "نجاح", "✅ تم تعديل البيانات بنجاح!")
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "❌ فشل في تعديل البيانات!")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ حدث خطأ أثناء الحفظ:\n{str(e)}")

    def update_order_in_db(self, data):
        """تحديث الطلب في قاعدة البيانات بالبيانات الجديدة"""
        try:
            # اتصال بقاعدة البيانات وتنفيذ تحديث جزئي
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE orders SET 
                    quantity = ?,
                    arrival_area = ?,
                    cargo_type = ?,
                    merchant_name = ?,
                    receipt_confirmation = ?,
                    notes = ?,
                    office = ?
                WHERE id = ?
            ''', data)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating order: {e}")
            return False
  