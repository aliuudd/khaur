

        

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QLineEdit,
    QTableWidgetItem, QMessageBox, QFileDialog, QHBoxLayout, QComboBox, QTabWidget, QWidget,
    QCheckBox, QTextEdit, QGroupBox, QGridLayout, QInputDialog, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from datetime import datetime
from babel.dates import format_datetime
from database import Database
from add_order_dialog import AddOrderDialog
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import os
import sqlite3
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

def fix_arabic(text: str) -> str:
    """إصلاح النص العربي ليُعرض بشكل صحيح في PDF"""
    if text is None:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)


class PasswordDialog(QDialog):
    def __init__(self, parent=None, title="🔐 كلمة المرور", message="🔐 أدخل كلمة المرور للترحيل"):
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
        # button_layout.addWidget(confirm_btn)
        
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.clicked.connect(self.reject)
        # button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_password(self):
        return self.password_input.text()


class OrdersManagementScreen(QDialog):
    
    order_transferred = pyqtSignal(int)  # إشارة عند ترحيل طلب
    order_returned = pyqtSignal(int)     # إشارة عند إرجاع دور

    def __init__(self, db: Database, transferred_orders=None):
        super().__init__()
        self.db = db
        self.transferred_orders = transferred_orders if transferred_orders is not None else self.db.get_transferred_orders()
        self.current_filter = "all"  # all, transferred, not_transferred
        self.setWindowTitle("📦  قاعده البيانات   ")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # عنوان الشاشة
        title = QLabel("📦  النظام الرئيسي وقاعده البيانات  ")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # زر إضافة طلب
        add_btn = QPushButton("➕ إضافة انتساب جديد  ")
        add_btn.setFont(QFont("Amiri", 16))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32; 
                color: white; 
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B5E20;
            }
        """)
        add_btn.clicked.connect(self.open_add_order)
        # layout.addWidget(add_btn)

        # شريط البحث والتصفية المتقدم
        filter_layout = QHBoxLayout()
        
        # حقل البحث العام
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث في جميع الحقول...")
        self.search_input.setFont(QFont("Amiri", 14))
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 5px;")
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        # البحث المتقدم بحقل محدد
        self.search_field = QComboBox()
        self.search_field.addItems([
            "جميع الحقول", "اسم السائق", "رقم القاطرة", "الكمية", "منطقة الوصول",
            "نوع البضاعة", "نوع الشاحنة", "الرقم التسلسلي", "اسم التاجر",
            "رقم المقعدة", "الموديل", "رقم الكرت", "اسم المالك", "الرقم الوطني",
            "رقم الهاتف", "الرخصة", "رقم الرخصة", "رقم النهمة", "الانتساب"
        ])
        self.search_field.setFont(QFont("Amiri", 12))
        filter_layout.addWidget(self.search_field)
        
        # أزرار التصفية
        filter_all_btn = QPushButton("📋 جميع الانتسابات ")
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
        filter_all_btn.clicked.connect(lambda: self.filter_transferred_orders("all"))
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
        filter_transferred_btn.clicked.connect(lambda: self.filter_transferred_orders("transferred"))
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
        filter_not_transferred_btn.clicked.connect(lambda: self.filter_transferred_orders("not_transferred"))
        filter_layout.addWidget(filter_not_transferred_btn)
        
        layout.addLayout(filter_layout)

        # جدول الطلبات
        self.table = QTableWidget()
        self.table.setLayoutDirection(Qt.RightToLeft)
        self.table.setColumnCount(37)
        self.table.setHorizontalHeaderLabels([
            "م", "اسم السائق", "رقم القاطرة", "الكمية", "منطقة الوصول", 
            "نوع البضاعة", "تاريخ الوصول", "نوع الشاحنة", "الرقم التسلسلي", 
            "تأكيد الاستلام", "تاريخ ووقت التأشيرة", "تاريخ ووقت التسجيل", 
            "اسم التاجر", "رقم المقعدة", "الموديل", "رقم الكرت", "النوع",
            "اسم المالك", "الرقم الوطني", "الرقم الوطني للسائق", "رقم الهاتف",
            "الرخصة", "رقم الرخصة", "صور المرفقات", "رقم النهمة", "رقم التاجر",
            "بيانات إضافية", "ملاحظات","الانتساب","التوقيف","المكتب","اللون", "الإجراءات", "إرجاع الدور", "تعديل", "حذف", "تصدير الصف"
        ])
        self.table.setFont(QFont("Amiri", 8))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 8, QFont.Bold))
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # ضبط أبعاد الأعمدة
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # عمود "م"
        self.table.setColumnWidth(0, 40)
        
        layout.addWidget(self.table)

        self.load_data()

        # أزرار التصدير والإرجاع
        export_layout = QHBoxLayout()
        
        # زر تحديث البيانات
        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setFont(QFont("Amiri", 12))
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.load_data)
        export_layout.addWidget(refresh_btn)
        
        layout.addLayout(export_layout)

        self.setLayout(layout)

    def filter_table(self, text):
        """تصفية الجدول بناءً على البحث"""
        search_field = self.search_field.currentText()
        text = text.strip().lower()
        
        for row in range(self.table.rowCount()):
            match = False
            
            if not text:  # إذا كان حقل البحث فارغاً، عرض كل الصفوف
                self.table.setRowHidden(row, False)
                continue
                
            if search_field == "جميع الحقول":
                # البحث في جميع الحقول
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and text in item.text().lower():
                        match = True
                        break
            else:
                # البحث في حقل محدد
                field_mapping = {
                    "اسم السائق": 1,
                    "رقم القاطرة": 2,
                    "الكمية": 3,
                    "منطقة الوصول": 4,
                    "نوع البضاعة": 5,
                    "نوع الشاحنة": 7,
                    "الرقم التسلسلي": 8,
                    "اسم التاجر": 12,
                    "رقم المقعدة": 13,
                    "الموديل": 14,
                    "رقم الكرت": 15,
                    "اسم المالك": 17,
                    "الرقم الوطني": 18,
                    "رقم الهاتف": 20,
                    "الرخصة": 21,
                    "رقم الرخصة": 22,
                    "رقم النهمة": 24,
                    "الانتساب": 28
                }
                
                col_index = field_mapping.get(search_field)
                if col_index is not None:
                    item = self.table.item(row, col_index)
                    if item and text in item.text().lower():
                        match = True
            
            self.table.setRowHidden(row, not match)

    def edit_order(self):
        """تعديل الطلب - الإصدار المحسن"""
        sender = self.sender()
        if not hasattr(sender, 'order_id'):
            QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على معرف الطلب!")
            return

        order_id = sender.order_id

        # طلب كلمة المرور
        password_dialog = PasswordDialog(self, "🔐 كلمة المرور للتعديل", "🔐 أدخل كلمة المرور للتعديل")
        if password_dialog.exec_() != QDialog.Accepted:
            return

        if password_dialog.get_password() != "admin":
            QMessageBox.critical(self, "خطأ", "❌ كلمة المرور غير صحيحة!")
            return

        # جلب بيانات الطلب من قاعدة البيانات
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب!")
                return

            # فتح نافذة التعديل مع تمرير order_id والبيانات
            dialog = AddOrderDialog(self.db, order_id=order_id, order_data=order, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_data()  # إعادة تحميل البيانات بعد التعديل
                QMessageBox.information(self, "نجاح", "✅ تم تعديل البيانات بنجاح!")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في تحميل بيانات الطلب:\n{str(e)}")

  
    def load_data(self):
        orders = self.db.get_all_orders()
        self.table.setRowCount(len(orders))

        # محاذاة رؤوس الأعمدة لليمين
        for i in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(i)
            if header_item:
                header_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for i, order in enumerate(orders):
            try:
                arrival = format_datetime(datetime.fromtimestamp(order[6]), "d MMMM y", locale="ar") if order[6] else ""
            except:
                arrival = str(order[6] or "")
            
            try:
                visa_dt = format_datetime(datetime.fromtimestamp(order[10]), "d MMMM y", locale="ar") if order[10] else ""
            except:
                visa_dt = str(order[10] or "")
            
            try:
                created_dt = format_datetime(datetime.fromtimestamp(order[11]), "d MMMM y", locale="ar") if order[11] else ""
            except:
                created_dt = str(order[11] or "")

            # البيانات الأساسية + الحقول الجديدة
            row_items = [
                str(i + 1),         # م - العمود 0
                order[1] or "",     # اسم السائق - العمود 1
                order[2] or "",     # رقم القاطرة - العمود 2
                order[3] or "",     # الكمية - العمود 3
                order[4] or "",     # منطقة الوصول - العمود 4
                order[5] or "",     # نوع البضاعة - العمود 5
                arrival,            # تاريخ الوصول - العمود 6
                order[7] or "",     # نوع الشاحنة - العمود 7
                order[8] or "",     # الرقم التسلسلي - العمود 8
                order[9] or "",     # تأكيد الاستلام - العمود 9
                visa_dt,            # تاريخ التأشيرة - العمود 10
                created_dt,         # تاريخ التسجيل - العمود 11
                order[12] or "",    # اسم التاجر - العمود 12
                order[13] or "",    # رقم المقعدة - العمود 13
                order[14] or "",    # الموديل - العمود 14
                order[15] or "",    # رقم الكرت - العمود 15
                order[16] or "",    # النوع - العمود 16
                order[17] or "",    # اسم المالك - العمود 17
                order[18] or "",    # الرقم الوطني - العمود 18
                order[19] or "",    # الرقم الوطني للسائق - العمود 19
                order[20] or "",    # رقم الهاتف - العمود 20
                order[21] or "",    # الرخصة - العمود 21
                order[22] or "",    # رقم الرخصة - العمود 22
                "🖼️ " + str(len([img for img in [order[23], order[24], order[25]] if img])) if any([order[23], order[24], order[25]]) else "❌",  # صور المرفقات - العمود 23
                order[26] or "",    # رقم النهمة - العمود 24
                order[27] or "",    # رقم التاجر - العمود 25
                order[28] or "",    # بيانات إضافية - العمود 26
                order[29] or "",    # ملاحظات - العمود 27
                order[30] or "",    # الانتساب - العمود 28
                order[31] or "",    # التوقيف - العمود 29
                order[32] or "",    # المكتب - العمود 30
                order[33] or ""     # اللون - العمود 31
            ]

            for col, val in enumerate(row_items):
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # تلوين الخلية إذا كان الطلب مُرحلاً
                if order[0] in self.transferred_orders:
                    cell.setBackground(QColor(255, 255, 0))  # أصفر
                
                self.table.setItem(i, col, cell)

            # زر التأكيد أو حالة الترحيل - العمود 32
            if order[0] in self.transferred_orders:
                # إذا كان مُرحلاً، نعرض زر "تم الترحيل"
                status_btn = QPushButton("✅ تم الترحيل")
                status_btn.setEnabled(False)
                status_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                """)
                self.table.setCellWidget(i, 32, status_btn)

                # زر إرجاع الدور للطلبات المُرحلة فقط - العمود 33
               

            # زر التعديل - العمود 34
            edit_btn = QPushButton("✏️ تعديل")
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
            edit_btn.order_id = order[0]
            edit_btn.clicked.connect(self.edit_order)
            self.table.setCellWidget(i, 34, edit_btn)

            # زر الحذف - العمود 35
            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.setStyleSheet("""
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
            delete_btn.order_id = order[0]
            delete_btn.clicked.connect(lambda checked, order_id=order[0]: self.delete_order(order_id))
            self.table.setCellWidget(i, 35, delete_btn)

            # زر تصدير الصف - العمود 36
            export_row_btn = QPushButton("📄 تصدير")
            export_row_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7B1FA2;
                }
            """)
            export_row_btn.order_id = order[0]
            export_row_btn.clicked.connect(lambda checked, order_id=order[0]: self.export_row_to_pdf(order_id))
            self.table.setCellWidget(i, 36, export_row_btn)


    def delete_order(self, order_id):
        """حذف الطلب - مع تحقق إضافي"""
        try:
            # الحصول على بيانات الطلب لعرضها في رسالة التأكيد
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب!")
                return
            
            driver_name = order[1] or "غير محدد"
            tractor_number = order[2] or "غير محدد"
            
            # تأكيد الحذف مع عرض معلومات الطلب
            reply = QMessageBox.question(self, "تأكيد الحذف", 
                                    f"""⚠️ هل أنت متأكد من حذف الطلب التالي؟
                                    
    الرقم: {order_id}
    اسم السائق: {driver_name}
    رقم القاطرة: {tractor_number}

    ❌ هذا الإجراء لا يمكن التراجع عنه!""",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = self.db.delete_order(order_id)
                if success:
                    QMessageBox.information(self, "نجاح", "✅ تم حذف الطلب بنجاح")
                    self.load_data()
                    
                    if order_id in self.transferred_orders:
                        self.transferred_orders.remove(order_id)
                        self.order_returned.emit(order_id)
                else:
                    QMessageBox.critical(self, "خطأ", "❌ فشل في حذف الطلب")
                    
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في حذف الطلب: {str(e)}")

    def edit_order(self):
        """تعديل الطلب - الإصدار المصحح"""
        # الحصول على الزر الذي تم النقر عليه
        sender = self.sender()
        if not hasattr(sender, 'order_id'):
            QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على معرف الطلب!")
            return

        order_id = sender.order_id

        # طلب كلمة المرور
        password_dialog = PasswordDialog(self, "🔐 كلمة المرور للتعديل", "🔐 أدخل كلمة المرور للتعديل")
        if password_dialog.exec_() != QDialog.Accepted:
            return

        # if password_dialog.get_password() != "a":
        #     QMessageBox.critical(self, "خطأ", "❌ كلمة المرور غير صحيحة!")
        #     return

        # جلب بيانات الطلب من قاعدة البيانات
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب!")
                return

            # فتح نافذة التعديل مع تمرير order_id والبيانات
            dialog = AddOrderDialog(self.db, order_id=order_id, order_data=order)
            if dialog.exec_() == QDialog.Accepted:
                self.load_data()  # إعادة تحميل البيانات بعد التعديل

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في تحميل بيانات الطلب:\n{str(e)}")

  
    



    # def edit_order(self):
    #     """تعديل الطلب - الإصدار المصحح"""
    #     # الحصول على الزر الذي تم النقر عليه
    #     sender = self.sender()
    #     if not hasattr(sender, 'order_id'):
    #         QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على معرف الطلب!")
    #         return

    #     order_id = sender.order_id

    #     # طلب كلمة المرور
    #     # password_dialog = PasswordDialog(self, "🔐 كلمة المرور للتعديل", "🔐 أدخل كلمة المرور للتعديل")
    #     # if password_dialog.exec_() != QDialog.Accepted:
    #     #     return

    #     # if password_dialog.get_password() != "admin":
    #     #     QMessageBox.critical(self, "خطأ", "❌ كلمة المرور غير صحيحة!")
    #     #     return

    #     # جلب بيانات الطلب من قاعدة البيانات
    #     try:
    #         order = self.db.get_order_by_id(order_id)
    #         if not order:
    #             QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب!")
    #             return

    #         # فتح نافذة التعديل مع تمرير order_id والبيانات
    #         dialog = AddOrderDialog(self.db, order_id=order_id, order_data=order)
    #         if dialog.exec_() == QDialog.Accepted:
    #             self.load_data()  # إعادة تحميل البيانات بعد التعديل

    #     except Exception as e:
    #         QMessageBox.critical(self, "خطأ", f"❌ فشل في تحميل بيانات الطلب:\n{str(e)}")
    def edit_order(self):
        """تعديل الطلب - الإصدار المصحح"""
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

            # فتح نافذة التعديل مع تمرير order_id والبيانات
            dialog = AddOrderDialog(self.db, order_id=order_id, order_data=order)
            if dialog.exec_() == QDialog.Accepted:
                self.load_data()  # إعادة تحميل البيانات بعد التعديل

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في تحميل بيانات الطلب:\n{str(e)}")

       



   
    def export_row_to_pdf(self, order_id):
        """تصدير الصف المحدد إلى PDF مع الصور"""
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب")
                return

            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # تحميل الخطوط
            fonts_dir = "assets/fonts/"
            regular_path = os.path.join(fonts_dir, "Amiri-Regular.ttf")
            bold_path = os.path.join(fonts_dir, "Amiri-Bold.ttf")
            pdf.add_font("Amiri", "", regular_path, uni=True)
            pdf.add_font("Amiri", "B", bold_path if os.path.exists(bold_path) else regular_path, uni=True)

            # أعلى الصفحة
            pdf.set_font("Amiri", size=14)
            pdf.cell(0, 10, fix_arabic("جمهورية اليمن"), ln=1, align="C")
            pdf.cell(0, 10, fix_arabic("شركة ضياء اليمن للنقل والاستيراد"), ln=1, align="C")
            
            # التاريخ
            now = format_datetime(datetime.now(), "EEEE، d MMMM y - h:mm a", locale='ar')
            pdf.set_font("Amiri", size=10)
            pdf.cell(0, 8, fix_arabic(f"التاريخ: {now}"), ln=1, align="L")

            # عنوان التقرير
            pdf.ln(5)
            pdf.set_font("Amiri", "B", 16)
            pdf.cell(0, 10, fix_arabic(f"تقرير تفصيلي للطلب رقم {order_id}"), ln=1, align="C")
            pdf.ln(5)

            # بيانات الطلب في جدول منظم
            pdf.set_font("Amiri", "B", 12)
            
            # معلومات السائق والمركبة
            data = [
                ("اسم السائق", order[1] or ""),
                ("رقم القاطرة", order[2] or ""),
                ("الكمية", order[3] or ""),
                ("منطقة الوصول", order[4] or ""),
                ("نوع البضاعة", order[5] or ""),
                ("تاريخ الوصول ", order[6] or ""),
                # ("تاريخ الوصول", format_datetime(datetime.fromtimestamp(order[6]), "d MMMM y", locale="ar") if order[6] else ""),
                # ("تاريخ الوصول", format_datetime(datetime.fromtimestamp(int(order[6])), "d MMMM y", locale="ar") if order[6] else ""),

                ("نوع الشاحنة", order[7] or ""),
                ("الرقم التسلسلي", order[8] or ""),
                ("اسم التاجر", order[12] or ""),
                ("رقم المقعدة", order[13] or ""),
                ("الموديل", order[14] or ""),
                ("رقم الكرت", order[15] or ""),
                ("النوع", order[16] or ""),
                ("اسم المالك", order[17] or ""),
                ("الرقم الوطني", order[18] or ""),
                ("الرقم الوطني للسائق", order[19] or ""),
                ("رقم الهاتف", order[20] or ""),
                ("الرخصة", order[21] or ""),
                ("رقم الرخصة", order[22] or ""),
                ("رقم النهمة", order[26] or ""),
                ("رقم التاجر", order[27] or ""),
                ("بيانات إضافية", order[28] or ""),
                ("ملاحظات", order[29] or ""),
                ("الانتساب", order[30] or ""),
                ("التوقيف", order[31] or ""),
                ("المكتب", order[32] or ""),
                ("اللون", order[33] or ""),
            ]

            # رسم الجدول
            col_width = 90
            row_height = 8
            
            for label, value in data:
                if pdf.get_y() + row_height > pdf.h - 20:
                    pdf.add_page()
                
                pdf.set_font("Amiri", "B", 10)
                # pdf.cell(col_width, row_height, fix_arabic(label), border=1, align="L")
                pdf.cell(col_width, row_height, fix_arabic(str(value)), border=1, align="R")
                pdf.set_font("Amiri", "", 10)
                # pdf.cell(col_width, row_height, fix_arabic(str(value)), border=1, align="L")
                pdf.cell(col_width, row_height, fix_arabic(label), border=1, align="R")
                pdf.ln(row_height)

            # إضافة الصور إذا كانت موجودة
            pdf.ln(10)
            pdf.set_font("Amiri", "B", 12)
            pdf.cell(0, 10, fix_arabic("المرفقات والصور"), ln=1, align="C")
            
            image_paths = [order[23], order[24], order[25]]  # صور الهوية، البطاقة، الرخصة
            image_labels = ["صورة الهوية", "صورة البطاقة", "صورة الرخصة"]
            valid_images = [(img, label) for img, label in zip(image_paths, image_labels) if img and os.path.exists(str(img))]
            
            if valid_images:
                pdf.ln(5)
                # حساب حجم الصور لتناسب الصفحة
                img_width = 50
                x_positions = [30, 90, 150]
                y_position = pdf.get_y()
                
                for i, (img_path, label) in enumerate(valid_images):
                    if i < 3:  # أقصى 3 صور في الصف
                        try:
                            x = x_positions[i]
                            # إضافة تسمية للصورة
                            pdf.set_xy(x, y_position - 5)
                            pdf.set_font("Amiri", "B", 8)
                            pdf.cell(img_width, 5, fix_arabic(label), align="C")
                            
                            # إضافة الصورة
                            pdf.image(str(img_path), x=x, y=y_position, w=img_width)
                            
                            # تحديث موضع Y للصورة التالية
                            if i == 2:  # إذا كانت الصورة الأخيرة في الصف
                                y_position += img_width + 10
                                pdf.set_y(y_position)
                        except Exception as e:
                            print(f"Error loading image: {e}")
                            continue
                
                pdf.ln(img_width + 5)
            else:
                pdf.set_font("Amiri", "", 10)
                pdf.cell(0, 10, fix_arabic("لا توجد صور مرفقة"), ln=1, align="C")

            # التوقيع
            pdf.ln(15)
            pdf.set_font("Amiri", size=11)
            pdf.cell(0, 6, fix_arabic("توقيع المشرف: ________________"), ln=True, align="L")
            pdf.cell(0, 6, fix_arabic("الاسم: ________________"), ln=True, align="L")
            pdf.cell(0, 6, fix_arabic("التاريخ: ________________"), ln=True, align="L")

            # حفظ الملف
            default_name = f"طلب_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(self, "حفظ تقرير الطلب", default_name, "PDF Files (*.pdf)")
            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "نجاح", f"✅ تم حفظ تقرير الطلب كـ PDF:\n{file_path}")
            else:
                QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ التقرير.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")
            
    def return_transferred_order(self):
        """إرجاع دور الطلب المحدد"""
        current_row = self.table.currentRow()
        if current_row < 0:

            QMessageBox.warning(self, "تحذير", "⚠️ يرجى تحديد طلب من الجدول أولاً!")
            return

        # الحصول على معرف الطلب من الصف المحدد
        widget = self.table.cellWidget(current_row, 33)  # زر الإرجاع في العمود 29
        if not widget or not hasattr(widget, 'order_id'):
            QMessageBox.warning(self, "تحذير", "⚠️ الطلب المحدد غير مرحل!")
            return

        order_id = widget.order_id
        self.return_order(order_id)

    def return_order(self, order_id):
        """إرجاع الطلب (إزالة حالة الترحيل)"""
        # طلب كلمة المرور
        password_dialog = PasswordDialog(self)
        if password_dialog.exec_() == QDialog.Accepted:
            password = password_dialog.get_password()
            
            # التحقق من كلمة المرور
            correct_password = "admin"  # كلمة المرور الافتراضية
            
            if password == correct_password:
                try:
                    # إزالة الطلب من قائمة الطلبات المُرحلة
                    if order_id in self.transferred_orders:
                        self.transferred_orders.remove(order_id)
                    
                    success = True
                    
                    if success:
                        # إرسال إشارة الإرجاع
                        self.order_returned.emit(order_id)
                        # تحديث حالة الطلب في الواجهة
                        self.update_order_return_status(order_id)
                        QMessageBox.information(self, "نجاح", "✅ تم إرجاع الدور بنجاح!")
                    else:
                        QMessageBox.critical(self, "خطأ", "❌ فشل في إرجاع الدور")
                except Exception as e:
                    QMessageBox.critical(self, "خطأ", f"❌ خطأ في إرجاع الدور: {str(e)}")
            else:
                QMessageBox.critical(self, "خطأ", "❌ كلمة المرور غير صحيحة!")

    def update_order_return_status(self, order_id):
        """تحديث حالة الطلب بعد الإرجاع"""
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 33)  # العمود 29 هو عمود الإرجاع
            if (isinstance(widget, QPushButton) and 
                hasattr(widget, 'order_id') and 
                widget.order_id == order_id):
                
                # إزالة التلوين الأصفر من جميع خلايا الصف
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 255, 255))  # أبيض
                
                # إزالة زر الإرجاع
                self.table.removeCellWidget(row, 33)
                empty_widget = QWidget()
                self.table.setCellWidget(row, 33, empty_widget)
                
                # استبدال زر "تم الترحيل" بزار "تأكيد"
                self.table.removeCellWidget(row, 28)
                confirm_btn = QPushButton("✅ تأكيد")
                confirm_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                confirm_btn.order_id = order_id
                confirm_btn.clicked.connect(lambda checked, oid=order_id: self.confirm_order(oid))
                self.table.setCellWidget(row, 28, confirm_btn)
                break

    def confirm_order(self, order_id):
        """تأكيد ترحيل الطلب مع طلب كلمة سر"""
        # طلب كلمة المرور
        password_dialog = PasswordDialog(self)
        if password_dialog.exec_() == QDialog.Accepted:
            password = password_dialog.get_password()
            
            # التحقق من كلمة المرور (يمكن تغييرها حسب الحاجة)
            correct_password = "admin"  # كلمة المرور الافتراضية
            
            if password == correct_password:
                try:
                    # الحصول على بيانات الطلب
                    order = self.db.get_order_by_id(order_id)
                    if order:
                        # نقل البيانات إلى قاعدة البيانات الرئيسية
                        success = self.db.transfer_to_main_database(order)
                        if success:
                            # تحديث حالة الترحيل في قاعدة البيانات
                            self.db.transfer_to_main_database(order_id)
                            # إرسال إشارة الترحيل
                            self.order_transferred.emit(order_id)
                            # تحديث حالة الطلب في الواجهة
                            self.update_order_status(order_id)
                            # فتح نافذة بيانات الترحيل
                            self.open_transfer_data_dialog(order)
                        else:
                            QMessageBox.critical(self, "خطأ", "❌ فشل في ترحيل البيانات")
                    else:
                        QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب")
                except Exception as e:
                    QMessageBox.critical(self, "خطأ", f"❌ خطأ في تأكيد الطلب: {str(e)}")
            else:
                QMessageBox.critical(self, "خطأ", "❌ كلمة المرور غير صحيحة!")

    def update_order_return_status(self, order_id):
        """تحديث حالة الطلب بعد الإرجاع"""
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 33)  # العمود 33 هو عمود الإرجاع
            if (isinstance(widget, QPushButton) and 
                hasattr(widget, 'order_id') and 
                widget.order_id == order_id):
                
                # إزالة التلوين الأصفر من جميع خلايا الصف
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 255, 255))  # أبيض
                
                # إزالة زر الإرجاع
                self.table.removeCellWidget(row, 33)
                empty_widget = QWidget()
                self.table.setCellWidget(row, 33, empty_widget)
                
                # استبدال زر "تم الترحيل" بزار "تأكيد"
                self.table.removeCellWidget(row, 32)
                confirm_btn = QPushButton("✅ تأكيد")
                confirm_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                confirm_btn.order_id = order_id
                confirm_btn.clicked.connect(lambda checked, oid=order_id: self.confirm_order(oid))
                self.table.setCellWidget(row, 32, confirm_btn)
                break           
    def filter_transferred_orders(self, filter_type):
        """تصفية الطلبات حسب حالة الترحيل"""
        self.current_filter = filter_type
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 28)
            is_transferred = isinstance(widget, QPushButton) and not widget.isEnabled()
            
            if filter_type == "all":
                self.table.setRowHidden(row, False)
            elif filter_type == "transferred":
                self.table.setRowHidden(row, not is_transferred)
            elif filter_type == "not_transferred":
                self.table.setRowHidden(row, is_transferred)

    def export_transferred_to_pdf(self):
            """تصدير الطلبات المُرحلة إلى PDF"""
            orders = self.db.get_all_orders()
            transferred_orders = [order for order in orders if order[0] in self.transferred_orders]
            
            if not transferred_orders:
                QMessageBox.critical(self, "خطأ", "❌ لا توجد طلبات مُرحلة لتصديرها!")
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
                pdf.set_font("Amiri", "B", 16)
                pdf.cell(0, 8, fix_arabic("تقرير الطلبات المُرحلة"), ln=2, align="C")
                pdf.ln(6)

                # إحصائية الطلبات المُرحلة
                pdf.set_font("Amiri", "B", 8)
                pdf.cell(0, 8, fix_arabic(f"عدد الطلبات المُرحلة: {len(transferred_orders)}"), ln=2, align="C")
                pdf.ln(10)

                # إعداد الأعمدة
                headers = [
                    "ملاحظات","الانتساب","التوقيف","المكتب","اللون" ,"بيانات إضافية", "رقم التاجر", "رقم النهمة", 
                    "رقم الرخصة", "الرخصة", "رقم الهاتف", "الرقم الوطني للسائق",
                    "الرقم الوطني", "اسم المالك", "النوع", "رقم الكرت", "الموديل",
                    "رقم المقعدة", "اسم التاجر", "تاريخ ووقت التسجيل", "تاريخ ووقت التأشيرة",
                    "تأكيد الاستلام", "الرقم التسلسلي", "نوع الشاحنة", "تاريخ الوصول",
                    "نوع البضاعة", "منطقة الوصول", "الكمية", "رقم القاطرة", "اسم السائق", "م"
                ]
                
                page_width = pdf.w - pdf.l_margin - pdf.r_margin
                col_ratios = [2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 0.5]
                total_ratio = sum(col_ratios)
                col_widths = [page_width * (r / total_ratio) for r in col_ratios]
                line_height = pdf.font_size * 1.5

                # رؤوس الجدول
                pdf.set_fill_color(144, 238, 144)
                pdf.set_font("Amiri", "B", 6)

                # كتابة الرؤوس في سطر واحد
                x_position = pdf.get_x()
                y_position = pdf.get_y()
                
                for i, h in enumerate(headers):
                    pdf.set_xy(x_position, y_position)
                    pdf.cell(col_widths[i], line_height, fix_arabic(h), border=1, align="C", fill=True)
                    x_position += col_widths[i]
                
                pdf.ln(line_height)

                # بيانات الجدول
                pdf.set_font("Amiri", "", 6)
                for idx, order in enumerate(transferred_orders):
                    try:
                        arrival = format_datetime(datetime.fromtimestamp(order[6]), "d MMMM y", locale="ar") if order[6] else ""
                    except:
                        arrival = str(order[6] or "")
                    try:
                        visa_dt = format_datetime(datetime.fromtimestamp(order[10]), "d MMMM y", locale="ar") if order[10] else ""
                    except:
                        visa_dt = str(order[10] or "")
                    try:
                        created_dt = format_datetime(datetime.fromtimestamp(order[11]), "d MMMM y", locale='ar') if order[11] else ""
                    except:
                        created_dt = str(order[11] or "")

                    row = [
                        order[33] or "", # اللون
                        order[32] or "", #  المكتب
                        order[31] or "",   #   التوقيف 
                        order[30] or "",   #  الانتساب 
                        order[29] or "",    # ملاحظات
                        order[28] or "",    # بيانات إضافية
                        order[27] or "",    # رقم التاجر
                        order[26] or "",    # رقم النهمة
                        order[22] or "",    # رقم الرخصة
                        order[21] or "",    # الرخصة
                        order[20] or "",    # رقم الهاتف
                        order[19] or "",    # الرقم الوطني للسائق
                        order[18] or "",    # الرقم الوطني
                        order[17] or "",    # اسم المالك
                        order[16] or "",    # النوع
                        order[15] or "",    # رقم الكرت
                        order[14] or "",    # الموديل
                        order[13] or "",    # رقم المقعدة
                        order[12] or "",    # اسم التاجر
                        created_dt,         # تاريخ التسجيل
                        visa_dt,            # تاريخ التأشيرة
                        order[9] or "",     # تأكيد الاستلام
                        order[8] or "",     # الرقم التسلسلي
                        order[7] or "",     # نوع الشاحنة
                        arrival,            # تاريخ الوصول
                        order[5] or "",     # نوع البضاعة
                        order[4] or "",     # منطقة الوصول
                        order[3] or "",     # الكمية
                        order[2] or "",     # رقم القاطرة
                        order[1] or "",     # اسم السائق
                        str(idx + 1)        # م
                    ]

                    # كتابة البيانات في سطر واحد
                    x_position = pdf.get_x()
                    y_position = pdf.get_y()
                    
                    for j, cell in enumerate(row):
                        pdf.set_xy(x_position, y_position)
                        # تقليم النص الطويل
                        text = str(cell)
                        if len(text) > 20:
                            text = text[:17] + '...'
                        pdf.cell(col_widths[j], line_height, fix_arabic(text), border=1, align="C", fill=False)
                        x_position += col_widths[j]
                    
                    pdf.ln(line_height)

                # التوقيع
                pdf.ln(10)
                pdf.set_font("Amiri", size=11)
                pdf.cell(0, 6, fix_arabic("توقيع المشرف: ________________"), ln=True, align="L")
                pdf.cell(0, 6, fix_arabic("الاسم: ________________"), ln=True, align="L")
                pdf.cell(0, 6, fix_arabic("التاريخ: ________________"), ln=True, align="L")

                # حفظ الملف
                default_name = f"الطلبات_المُرحلة_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path, _ = QFileDialog.getSaveFileName(self, "حفظ تقرير الطلبات المُرحلة", default_name, "PDF Files (*.pdf)")
                if file_path:
                    pdf.output(file_path)
                    QMessageBox.information(self, "نجاح", f"✅ تم حفظ تقرير الطلبات المُرحلة كـ PDF:\n{file_path}")
                else:
                    QMessageBox.warning(self, "تحذير", "❌ لم يتم حفظ التقرير.")

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"❌ خطأ في تصدير PDF:\n{str(e)}")
    

    def open_transfer_data_dialog(self, order_data):
        """فتح نافذة بيانات الترحيل"""
        dialog = TransferDataDialog(order_data, self)
        dialog.exec_()

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

    def open_add_order(self):
        dialog = AddOrderDialog(self.db)
        dialog.finished.connect(self.load_data)
        dialog.exec_()

    def export_to_pdf(self):
        """تصدير جميع الطلبات إلى PDF"""
        orders = self.db.get_all_orders()
        if not orders:
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
                "ملاحظات","الانتساب","التوقيف","المكتب","اللون", "بيانات إضافية", "رقم التاجر", "رقم النهمة", 
                "رقم الرخصة", "الرخصة", "رقم الهاتف", "الرقم الوطني للسائق",
                "الرقم الوطني", "اسم المالك", "النوع", "رقم الكرت", "الموديل",
                "رقم المقعدة", "اسم التاجر", "تاريخ ووقت التسجيل", "تاريخ ووقت التأشيرة",
                "تأكيد الاستلام", "الرقم التسلسلي", "نوع الشاحنة", "تاريخ الوصول",
                "نوع البضاعة", "منطقة الوصول", "الكمية", "رقم القاطرة", "اسم السائق", "م"
            ]
            
            page_width = pdf.w - pdf.l_margin - pdf.r_margin
            col_ratios = [2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 0.5]
            total_ratio = sum(col_ratios)
            col_widths = [page_width * (r / total_ratio) for r in col_ratios]
            line_height = pdf.font_size * 1.5

            # رؤوس الجدول
            pdf.set_fill_color(144, 238, 144)
            pdf.set_font("Amiri", "B", 6)

            # كتابة الرؤوس في سطر واحد
            x_position = pdf.get_x()
            y_position = pdf.get_y()
            
            for i, h in enumerate(headers):
                pdf.set_xy(x_position, y_position)
                pdf.cell(col_widths[i], line_height, fix_arabic(h), border=1, align="C", fill=True)
                x_position += col_widths[i]
            
            pdf.ln(line_height)

            # بيانات الجدول
            pdf.set_font("Amiri", "", 6)
            for idx, order in enumerate(orders):
                try:
                    arrival = format_datetime(datetime.fromtimestamp(order[6]), "d MMMM y", locale="ar") if order[6] else ""
                except:
                    arrival = str(order[6] or "")
                try:
                    visa_dt = format_datetime(datetime.fromtimestamp(order[10]), "d MMMM y", locale="ar") if order[10] else ""
                except:
                    visa_dt = str(order[10] or "")
                try:
                    created_dt = format_datetime(datetime.fromtimestamp(order[11]), "d MMMM y", locale='ar') if order[11] else ""
                except:
                    created_dt = str(order[11] or "")

                row = [
                    order[33] or "", # اللون
                    order[32] or "", #  المكتب
                    order[31] or "",   #   التوقيف 
                    order[30] or "",    # الانتساب
                    order[29] or "",    # ملاحظات
                    order[28] or "",    # بيانات إضافية
                    order[27] or "",    # رقم التاجر
                    order[26] or "",    # رقم النهمة
                    order[22] or "",    # رقم الرخصة
                    order[21] or "",    # الرخصة
                    order[20] or "",    # رقم الهاتف
                    order[19] or "",    # الرقم الوطني للسائق
                    order[18] or "",    # الرقم الوطني
                    order[17] or "",    # اسم المالك
                    order[16] or "",    # النوع
                    order[15] or "",    # رقم الكرت
                    order[14] or "",    # الموديل
                    order[13] or "",    # رقم المقعدة
                    order[12] or "",    # اسم التاجر
                    created_dt,         # تاريخ التسجيل
                    visa_dt,            # تاريخ التأشيرة
                    order[9] or "",     # تأكيد الاستلام
                    order[8] or "",     # الرقم التسلسلي
                    order[7] or "",     # نوع الشاحنة
                    arrival,            # تاريخ الوصول
                    order[5] or "",     # نوع البضاعة
                    order[4] or "",     # منطقة الوصول
                    order[3] or "",     # الكمية
                    order[2] or "",     # رقم القاطرة
                    order[1] or "",     # اسم السائق
                    str(idx + 1)        # م
                ]

                # كتابة البيانات في سطر واحد
                x_position = pdf.get_x()
                y_position = pdf.get_y()
                
                for j, cell in enumerate(row):
                    pdf.set_xy(x_position, y_position)
                    # تقليم النص الطويل
                    text = str(cell)
                    if len(text) > 20:
                        text = text[:17] + '...'
                    pdf.cell(col_widths[j], line_height, fix_arabic(text), border=1, align="C", fill=False)
                    x_position += col_widths[j]
                
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


class TransferDataDialog(QDialog):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle("📊 بيانات الترحيل")
        self.setGeometry(150, 150, 800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # عنوان النافذة
        title = QLabel("📊 بيانات الترحيل - الطلب المؤكد")
        title.setFont(QFont("Amiri", 18, QFont.Bold))
        title.setStyleSheet("color: #FF9800; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # إنشاء تبويبات
        tabs = QTabWidget()
        
        # تبويب البيانات الأساسية
        basic_tab = self.create_basic_info_tab()
        tabs.addTab(basic_tab, "البيانات الأساسية")
        
        # تبويب بيانات المركبة
        vehicle_tab = self.create_vehicle_info_tab()
        tabs.addTab(vehicle_tab, "بيانات المركبة")
        
        # تبويب بيانات السائق
        driver_tab = self.create_driver_info_tab()
        tabs.addTab(driver_tab, "بيانات السائق")

        layout.addWidget(tabs)

        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ طباعة البيانات")
        print_btn.setFont(QFont("Amiri", 14))
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        print_btn.clicked.connect(self.print_data)
        button_layout.addWidget(print_btn)

        close_btn = QPushButton("❌ إغلاق")
        close_btn.setFont(QFont("Amiri", 14))
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_basic_info_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        # البيانات الأساسية
        layout.addWidget(QLabel("اسم السائق:"), 0, 0)
        layout.addWidget(QLabel(str(self.order_data[1] or "")), 0, 1)
        
        layout.addWidget(QLabel("رقم القاطرة:"), 1, 0)
        layout.addWidget(QLabel(str(self.order_data[2] or "")), 1, 1)
        
        layout.addWidget(QLabel("الكمية:"), 2, 0)
        layout.addWidget(QLabel(str(self.order_data[3] or "")), 2, 1)
        
        layout.addWidget(QLabel("منطقة الوصول:"), 3, 0)
        layout.addWidget(QLabel(str(self.order_data[4] or "")), 3, 1)
        
        layout.addWidget(QLabel("نوع البضاعة:"), 4, 0)
        layout.addWidget(QLabel(str(self.order_data[5] or "")), 4, 1)

        widget.setLayout(layout)
        return widget

    def create_vehicle_info_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        # بيانات المركبة
        layout.addWidget(QLabel("نوع الشاحنة:"), 0, 0)
        layout.addWidget(QLabel(str(self.order_data[7] or "")), 0, 1)
        
        layout.addWidget(QLabel("الرقم التسلسلي:"), 1, 0)
        layout.addWidget(QLabel(str(self.order_data[8] or "")), 1, 1)
        
        layout.addWidget(QLabel("رقم المقعدة:"), 2, 0)
        layout.addWidget(QLabel(str(self.order_data[13] or "")), 2, 1)
        
        layout.addWidget(QLabel("الموديل:"), 3, 0)
        layout.addWidget(QLabel(str(self.order_data[14] or "")), 3, 1)
        
        layout.addWidget(QLabel("رقم الكرت:"), 4, 0)
        layout.addWidget(QLabel(str(self.order_data[15] or "")), 4, 1)

        ###  من هنا 
        layout.addWidget(QLabel(" الانتساب:"), 5, 0)
        layout.addWidget(QLabel(str(self.order_data[30] or "")), 5, 1)

        # 
        layout.addWidget(QLabel(" التوقيف:"), 6, 0)
        layout.addWidget(QLabel(str(self.order_data[31] or "")), 6, 1)

        layout.addWidget(QLabel(" المكتب:"), 7, 0)
        layout.addWidget(QLabel(str(self.order_data[32] or "")), 7, 1)


        layout.addWidget(QLabel(" اللون:"), 8, 0)
        layout.addWidget(QLabel(str(self.order_data[33] or "")), 8, 1)

        


        widget.setLayout(layout)
        return widget

    def create_driver_info_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        # بيانات السائق
        layout.addWidget(QLabel("الرقم الوطني للسائق:"), 0, 0)
        layout.addWidget(QLabel(str(self.order_data[19] or "")), 0, 1)
        
        layout.addWidget(QLabel("رقم الهاتف:"), 1, 0)
        layout.addWidget(QLabel(str(self.order_data[20] or "")), 1, 1)
        
        layout.addWidget(QLabel("الرخصة:"), 2, 0)
        layout.addWidget(QLabel(str(self.order_data[21] or "")), 2, 1)
        
        layout.addWidget(QLabel("رقم الرخصة:"), 3, 0)
        layout.addWidget(QLabel(str(self.order_data[22] or "")), 3, 1)
        
        layout.addWidget(QLabel("اسم المالك:"), 4, 0)
        layout.addWidget(QLabel(str(self.order_data[17] or "")), 4, 1)

        widget.setLayout(layout)
        return widget

    def print_data(self):
        """طباعة بيانات الترحيل"""
        try:
            # هنا يمكنك إضافة كود الطباعة الفعلي
            QMessageBox.information(self, "نجاح", "✅ تم تجهيز البيانات للطباعة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في الطباعة: {str(e)}")


