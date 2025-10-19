# from PyQt5.QtWidgets import (
#     QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
#     QComboBox, QTextEdit, QDateEdit, QTimeEdit, QGroupBox, QGridLayout,
#     QFileDialog, QMessageBox, QCheckBox, QTabWidget, QWidget
# )
# from PyQt5.QtCore import QDateTime, Qt
# from PyQt5.QtGui import QFont, QPixmap
# import os
# import sqlite3
# from datetime import datetime
# from database import Database


# class AddOrderDialog(QDialog):
#     # def __init__(self, db):
#     def __init__(self, db: Database,order_id=None,  parent=None,order_data=None):
#         super().__init__()
#         self.order_id = order_id
#         self.db = db
#         self.order_data = order_data
       
#         self.setWindowTitle("➕ إضافة طلب جديد")
#         self.setGeometry(100, 100, 900, 800)
#         self.setStyleSheet("background-color: white;")
        
#         # مسارات الصور
#         self.id_card_image = None
#         self.card_image = None
#         self.license_image = None
        
#         self.init_ui()
#         if self.order_id is not None and self.order_data is not None:
#             self.load_data_for_edit()

#     def init_ui(self):
#         layout = QVBoxLayout()
        
#         # إنشاء تبويبات
#         tabs = QTabWidget()
        
#         # تبويب البيانات الأساسية
#         basic_tab = QWidget()
#         basic_layout = QVBoxLayout()
#         basic_layout.addWidget(self.create_basic_info_group())
#         basic_layout.addWidget(self.create_arrival_info_group())
#         basic_tab.setLayout(basic_layout)
#         tabs.addTab(basic_tab, "البيانات الأساسية")
        
#         # تبويب بيانات المركبة
#         vehicle_tab = QWidget()
#         vehicle_layout = QVBoxLayout()
#         vehicle_layout.addWidget(self.create_vehicle_info_group())
#         vehicle_tab.setLayout(vehicle_layout)
#         tabs.addTab(vehicle_tab, "بيانات المركبة")
        
#         # تبويب بيانات السائق
#         driver_tab = QWidget()
#         driver_layout = QVBoxLayout()
#         driver_layout.addWidget(self.create_driver_info_group())
#         driver_tab.setLayout(driver_layout)
#         # tabs.addTab(driver_tab, "بيانات السائق")
        
#         # تبويب المرفقات
#         attachments_tab = QWidget()
#         attachments_layout = QVBoxLayout()
#         attachments_layout.addWidget(self.create_attachments_group())
#         attachments_tab.setLayout(attachments_layout)
#         tabs.addTab(attachments_tab, "المرفقات")
        
#         layout.addWidget(tabs)
        
#         # زر الحفظ
#         save_btn = QPushButton("💾 حفظ الطلب")
#         save_btn.setFont(QFont("Amiri", 16))
#         save_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: #2196F3;
#                 color: white;
#                 padding: 12px;
#                 border-radius: 8px;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background-color: #1976D2;
#             }
#         """)
#         save_btn.clicked.connect(self.save_order)
#         layout.addWidget(save_btn)
        
#         self.setLayout(layout)
#     def load_data_for_edit(self):
#         """ملء حقول النموذج بالبيانات الحالية عند التعديل"""
#         order = self.order_data

#         # الحقول النصية البسيطة
#         self.driver_name.setText(str(order[1] or ""))
#         self.tractor_number.setText(str(order[2] or ""))
#         self.quantity.setText(str(order[3] or ""))
#         self.arrival_area.setText(str(order[4] or ""))
#         self.cargo_type.setEditText(str(order[5] or ""))
#         self.truck_type.setEditText(str(order[7] or ""))
#         self.serial_number.setText(str(order[8] or ""))
#         self.receipt_confirmation.setEditText(str(order[9] or ""))
#         self.merchant_name.setText(str(order[12] or ""))
#         self.seat_number.setText(str(order[13] or ""))
#         self.model.setText(str(order[14] or ""))
#         self.card_number.setText(str(order[15] or ""))
#         self.vehicle_type.setText(str(order[16] or ""))  # تأكد من أن الاسم ليس "type"
#         self.owner_name.setText(str(order[17] or ""))
#         self.national_id.setText(str(order[18] or ""))
#         self.driver_national_id.setText(str(order[19] or ""))
#         self.phone.setText(str(order[20] or ""))
#         self.license_type.setText(str(order[21] or ""))
#         self.license_number.setText(str(order[22] or ""))
#         self.nahma_number.setText(str(order[26] or ""))
#         self.merchant_name.setText(str(order[27] or ""))

#         # الحقول النصية الطويلة (إذا كانت QTextEdit)
#         if hasattr(self.extra_data, 'setPlainText'):
#             self.extra_data.setPlainText(str(order[28] or ""))
#         else:
#             self.extra_data.setText(str(order[28] or ""))

#         if hasattr(self.notes, 'setPlainText'):
#             self.notes.setPlainText(str(order[29] or ""))
#         else:
#             self.notes.setText(str(order[29] or ""))

#         # معالجة التواريخ (من timestamp إلى نص قابل للعرض)
#         from datetime import datetime
#         try:
#             if order[6]:  # arrival_date
#                 dt = datetime.fromtimestamp(order[6])
#                 self.arrival_date.setTime(dt.strftime("%Y-%m-%d"))
#             else:
#                 self.arrival_date.clear()
#         except:
#             self.arrival_date.clear()

#         try:
#             if order[10]:  # visa_datetime
#                 dt = datetime.fromtimestamp(order[10])
#                 self.visa_dt.setTime(dt.strftime("%Y-%m-%d %H:%M"))
#             else:
#                 self.visa_dt.clear()
#         except:
#             self.visa_dt.clear()

#         # ملاحظة: إذا كنت تستخدم QDateEdit أو QDateTimeEdit، فاستخدم setDate/setDateTime بدل setText
#         # ... وهكذا لكل حقل
#     def create_basic_info_group(self):
#         group = QGroupBox("البيانات الأساسية")
#         layout = QGridLayout()
        
#         # الصف 1
#         layout.addWidget(QLabel("اسم السائق:"), 0, 0)
#         self.driver_name = QLineEdit()
#         layout.addWidget(self.driver_name, 0, 1)
        
#         layout.addWidget(QLabel("الرقم الوطني للسائق:"), 0, 2)
#         self.driver_national_id = QLineEdit()
#         layout.addWidget(self.driver_national_id, 0, 3)
        
#         # الصف 2
#         layout.addWidget(QLabel("رقم السائق:"), 1, 0)
#         self.phone = QLineEdit()
#         layout.addWidget(self.phone, 1, 1)
        
#         layout.addWidget(QLabel("الرخصة:"), 1, 2)
#         self.license_type = QLineEdit()
#         layout.addWidget(self.license_type, 1, 3)
        
#         # الصف 3
#         layout.addWidget(QLabel("رقم الرخصة:"), 2, 0)
#         self.license_number = QLineEdit()
#         layout.addWidget(self.license_number, 2, 1)
        
#         layout.addWidget(QLabel("اسم المالك:"), 2, 2)
#         self.owner_name = QLineEdit()
#         layout.addWidget(self.owner_name, 2, 3)
        
#         # الصف 4
#         layout.addWidget(QLabel("الرقم الوطني:"), 3, 0)
#         self.national_id = QLineEdit()
#         layout.addWidget(self.national_id, 3, 1)
        
#         layout.addWidget(QLabel("نوع الطلب "), 3, 2)
#         self.vehicle_type = QLineEdit()
#         layout.addWidget(self.vehicle_type, 3, 3)
        
#         group.setLayout(layout)
#         return group

#     def create_vehicle_info_group(self):
#         group = QGroupBox("بيانات المركبة")
#         layout = QGridLayout()
        
#         # الصف 1
#         layout.addWidget(QLabel("رقم القاطرة:"), 0, 0)
#         self.tractor_number = QLineEdit()
#         layout.addWidget(self.tractor_number, 0, 1)
        
#         layout.addWidget(QLabel("رقم المقعدة:"), 0, 2)
#         self.seat_number = QLineEdit()
#         layout.addWidget(self.seat_number, 0, 3)
        
#         # الصف 2
#         layout.addWidget(QLabel("الموديل:"), 1, 0)
#         self.model = QLineEdit()
#         layout.addWidget(self.model, 1, 1)
        
#         layout.addWidget(QLabel("رقم الكرت:"), 1, 2)
#         self.card_number = QLineEdit()
#         layout.addWidget(self.card_number, 1, 3)
        
#         # الصف 3
#         layout.addWidget(QLabel("نوع الشاحنة:"), 2, 0)
#         self.truck_type = QComboBox()
#         self.truck_type.addItems(["عادي", "سكس"])
#         layout.addWidget(self.truck_type, 2, 1)
        
#         layout.addWidget(QLabel("الرقم التسلسلي:"), 2, 2)
#         self.serial_number = QLineEdit()
#         layout.addWidget(self.serial_number, 2, 3)
        
#         group.setLayout(layout)
#         return group
#     def create_arrival_info_group(self):
#         group = QGroupBox("بيانات الوصول والشحن")
#         layout = QGridLayout()
        
#         # الصف 0
#         layout.addWidget(QLabel("الكمية:"), 0, 0)
#         self.quantity = QLineEdit()
#         layout.addWidget(self.quantity, 0, 1)
        
#         layout.addWidget(QLabel("منطقة الوصول:"), 0, 2)
#         self.arrival_area = QLineEdit()
#         layout.addWidget(self.arrival_area, 0, 3)
        
#         # الصف 1
#         layout.addWidget(QLabel("نوع البضاعة:"), 1, 0)
#         self.cargo_type = QComboBox()
#         self.cargo_type.addItems(["بضاعة جافة", "بضاعة سائلة", "مواد غذائية", "أدوية"," الكترونيات ","ادوات  زراعية ", "ادوات كهربائية","ملابس","أخرى"])
#         layout.addWidget(self.cargo_type, 1, 1)
        
#         layout.addWidget(QLabel("تاريخ الوصول:"), 1, 2)
#         self.arrival_date = QDateEdit()
#         self.arrival_date.setDate(QDateTime.currentDateTime().date())
#         self.arrival_date.setCalendarPopup(True)
#         layout.addWidget(self.arrival_date, 1, 3)
        
#         # الصف 2 - تاريخ التأشيرة
#         layout.addWidget(QLabel("تاريخ ووقت التاشيرة:"), 2, 0)
#         self.visa_dt =  QDateEdit()  # تغيير إلى QDateTimeEdit لإضافة الوقت
#         self.visa_dt.setDateTime(QDateTime.currentDateTime())
#         self.visa_dt.setCalendarPopup(True)
#         layout.addWidget(self.visa_dt, 2, 1)
        
#         # الصف 3 - تاريخ التسجيل
#         layout.addWidget(QLabel("تاريخ ووقت التسجيل:"), 3, 0)
#         self.created_dt =  QDateEdit()  # تغيير إلى QDateTimeEdit لإضافة الوقت
#         self.visa_dt.setDateTime(QDateTime.currentDateTime())
#         self.created_dt.setCalendarPopup(True)
#         layout.addWidget(self.created_dt, 3, 1)
        
#         # الصف 4
#         layout.addWidget(QLabel("رقم النهمة:"), 4, 0)
#         self.nahma_number = QLineEdit()
#         layout.addWidget(self.nahma_number, 4, 1)
        
#         layout.addWidget(QLabel("رقم التاجر:"), 4, 2)
#         self.merchant_number = QLineEdit()
#         layout.addWidget(self.merchant_number, 4, 3)
        
#         # الصف 5
#         layout.addWidget(QLabel("اسم التاجر:"), 5, 0)
#         self.merchant_name = QLineEdit()
#         layout.addWidget(self.merchant_name, 5, 1)
        
#         layout.addWidget(QLabel("تأكيد الاستلام:"), 5, 2)
#         self.receipt_confirmation = QComboBox()
#         self.receipt_confirmation.addItems(["مؤكد", "في الانتظار", "ملغى"])
#         layout.addWidget(self.receipt_confirmation, 5, 3)
        
#         # الصف 6
#         layout.addWidget(QLabel("بيانات إضافية:"), 6, 0)
#         self.extra_data = QTextEdit()
#         self.extra_data.setMaximumHeight(80)
#         layout.addWidget(self.extra_data, 6, 1, 1, 3)
        
#         # الصف 7
#         layout.addWidget(QLabel("  ملاحظة /الانتساب:"), 7, 0)
#         self.notes = QTextEdit()
#         self.notes.setMaximumHeight(80)
#         layout.addWidget(self.notes, 7, 1, 1, 3)


#         #  من هنا اضفناء 

#                 # الصف 8 - الانتساب
#         layout.addWidget(QLabel("الانتساب:"), 8, 0)
#         self.intsap = QLineEdit()
#         layout.addWidget(self.intsap, 8, 1)

#         # الصف 9 - التوقيف
#         layout.addWidget(QLabel("التوقيف:"), 9, 0)
#         self.stop = QLineEdit()
#         layout.addWidget(self.stop, 9, 1)

#         # الصف 10 - المكتب
#         layout.addWidget(QLabel("المكتب:"), 10, 0)
#         self.office = QLineEdit()
#         layout.addWidget(self.office, 10, 1)

#         # الصف 11 - اللون
#         layout.addWidget(QLabel("اللون:"), 11, 0)
#         self.color = QLineEdit()
#         layout.addWidget(self.color, 11, 1)
        
#         group.setLayout(layout)
#         return group
  
#     def create_driver_info_group(self):
#         group = QGroupBox("بيانات السائق الإضافية")
#         layout = QGridLayout()
        
#         # يمكن إضافة المزيد من حقول السائق هنا إذا لزم الأمر
#         layout.addWidget(QLabel("سيتم إضافة المزيد من الحقول الخاصة بالسائق هنا"), 0, 0)
        
#         group.setLayout(layout)
#         return group

#     def create_attachments_group(self):
#         group = QGroupBox("المرفقات")
#         layout = QGridLayout()
        
#         # بطاقة الهوية
#         layout.addWidget(QLabel("صورة البطاقة:"), 0, 0)
#         self.id_card_btn = QPushButton("📷 اختيار صورة البطاقة")
#         self.id_card_btn.clicked.connect(lambda: self.select_image("id_card"))
#         layout.addWidget(self.id_card_btn, 0, 1)
#         self.id_card_label = QLabel("لم يتم اختيار صورة")
#         layout.addWidget(self.id_card_label, 0, 2)
        
#         # الكرت
#         layout.addWidget(QLabel("صورة الكرت:"), 1, 0)
#         self.card_btn = QPushButton("📷 اختيار صورة الكرت")
#         self.card_btn.clicked.connect(lambda: self.select_image("card"))
#         layout.addWidget(self.card_btn, 1, 1)
#         self.card_label = QLabel("لم يتم اختيار صورة")
#         layout.addWidget(self.card_label, 1, 2)
        
#         # الرخصة
#         layout.addWidget(QLabel("صورة الرخصة:"), 2, 0)
#         self.license_btn = QPushButton("📷 اختيار صورة الرخصة")
#         self.license_btn.clicked.connect(lambda: self.select_image("license"))
#         layout.addWidget(self.license_btn, 2, 1)
#         self.license_label = QLabel("لم يتم اختيار صورة")
#         layout.addWidget(self.license_label, 2, 2)
        
#         group.setLayout(layout)
#         return group

#     def select_image(self, image_type):
#         file_path, _ = QFileDialog.getOpenFileName(
#             self, 
#             f"اختر صورة {image_type}", 
#             "", 
#             "Image Files (*.png *.jpg *.jpeg *.bmp)"
#         )
        
#         if file_path:
#             if image_type == "id_card":
#                 self.id_card_image = file_path
#                 self.id_card_label.setText(os.path.basename(file_path))
#             elif image_type == "card":
#                 self.card_image = file_path
#                 self.card_label.setText(os.path.basename(file_path))
#             elif image_type == "license":
#                 self.license_image = file_path
#                 self.license_label.setText(os.path.basename(file_path))

#     def save_order(self):
#         try:
#             # جمع البيانات من الحقول
#             data = (
#                 self.driver_name.text(),
#                 self.tractor_number.text(),
#                 self.quantity.text(),
#                 self.arrival_area.text(),
#                 self.cargo_type.currentText(),
#                 self.arrival_date.date().toPyDate().strftime("%Y-%m-%d"),
#                 self.truck_type.currentText(),
#                 self.serial_number.text(),
#                 self.receipt_confirmation.currentText(),
#                 self.visa_dt.date().toPyDate().strftime("%Y-%m-%d"),
#                   # timestamp للتأشيرة
#                 self.created_dt.date().toPyDate().strftime("%Y-%m-%d"),  # timestamp للتسجيل
#                 self.merchant_name.text(),
#                 self.seat_number.text(),
#                 self.model.text(),
#                 self.card_number.text(),
#                 self.vehicle_type.text(),
#                 self.owner_name.text(),
#                 self.national_id.text(),
#                 self.driver_national_id.text(),
#                 self.phone.text(),
#                 self.license_type.text(),
#                 self.license_number.text(),
#                 self.id_card_image or "",
#                 self.card_image or "",
#                 self.license_image or "",
#                 self.nahma_number.text(),
#                 self.merchant_number.text(),
#                 self.extra_data.toPlainText(),
#                 self.notes.toPlainText(),
#                 self.intsap.text(),   # بدلاً من ""
#                 self.stop.text(),     # بدلاً من ""
#                 self.office.text(),   # بدلاً من ""
#                 self.color.text()     # بدلاً من ""
#             )

            
#             if self.order_id is not None:
#                 # ✏️ وضع التعديل: تحديث السجل
#                 self.db.update_order(self.order_id, data)
#                 QMessageBox.information(self, "نجاح", "✅ تم تعديل الطلب بنجاح")
#             else:
#                 # ➕ وضع الإضافة: إدخال سجل جديد
#                 self.db.add_order(data)
#                 QMessageBox.information(self, "نجاح", "✅ تم إضافة الطلب بنجاح")

#             self.accept()
#         except Exception as e:
#             QMessageBox.critical(self, "خطأ", f"❌ فشل في الحفظ:\n{str(e)}")
            
#         #     # حفظ في قاعدة البيانات
#         #     if self.db.add_order(data):
#         #         QMessageBox.information(self, "نجاح", "✅ تم حفظ الطلب بنجاح")
#         #         self.accept()
#         #     else:
#         #         QMessageBox.critical(self, "خطأ", "❌ فشل في حفظ الطلب")
                
#         # except Exception as e:
#         #     QMessageBox.critical(self, "خطأ", f"❌ حدث خطأ أثناء حفظ الطلب: {str(e)}")

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QTextEdit, QDateEdit, QTimeEdit, QGroupBox, QGridLayout,
    QFileDialog, QMessageBox, QCheckBox, QTabWidget, QWidget
)
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QFont, QPixmap
import os
import sqlite3
from datetime import datetime
from database import Database


class AddOrderDialog(QDialog):
    def __init__(self, db: Database, order_id=None, parent=None, order_data=None):
        super().__init__(parent)
        self.order_id = order_id
        self.db = db
        self.order_data = order_data
       
        self.setWindowTitle("➕ إضافة طلب جديد" if order_id is None else "✏️ تعديل طلب")
        self.setGeometry(100, 100, 900, 800)
        self.setStyleSheet("background-color: white;")
        
        # مسارات الصور
        self.id_card_image = None
        self.card_image = None
        self.license_image = None
        
        self.init_ui()
        if self.order_id is not None and self.order_data is not None:
            self.load_data_for_edit()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # إنشاء تبويبات
        tabs = QTabWidget()
        
        # تبويب البيانات الأساسية
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        basic_layout.addWidget(self.create_basic_info_group())
        basic_layout.addWidget(self.create_arrival_info_group())
        basic_tab.setLayout(basic_layout)
        tabs.addTab(basic_tab, "البيانات الأساسية")
        
        # تبويب بيانات المركبة
        vehicle_tab = QWidget()
        vehicle_layout = QVBoxLayout()
        vehicle_layout.addWidget(self.create_vehicle_info_group())
        vehicle_tab.setLayout(vehicle_layout)
        tabs.addTab(vehicle_tab, "بيانات المركبة")
        
        # تبويب المرفقات
        attachments_tab = QWidget()
        attachments_layout = QVBoxLayout()
        attachments_layout.addWidget(self.create_attachments_group())
        attachments_tab.setLayout(attachments_layout)
        tabs.addTab(attachments_tab, "المرفقات")
        
        layout.addWidget(tabs)
        
        # أزرار الحفظ والإلغاء
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 حفظ الطلب")
        save_btn.setFont(QFont("Amiri", 16))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        save_btn.clicked.connect(self.save_order)
        button_layout.addWidget(save_btn)


        save_as_new_btn = QPushButton("💾 حفظ كسجل جديد")
        save_as_new_btn.setFont(QFont("Amiri", 16))
        save_as_new_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        save_as_new_btn.clicked.connect(self.save_as_new_order)
        button_layout.addWidget(save_as_new_btn)
        
        
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.setFont(QFont("Amiri", 16))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_data_for_edit(self):
        """ملء حقول النموذج بالبيانات الحالية عند التعديل"""
        order = self.order_data

        # الحقول النصية البسيطة
        self.driver_name.setText(str(order[1] or ""))
        self.tractor_number.setText(str(order[2] or ""))
        self.quantity.setText(str(order[3] or ""))
        self.arrival_area.setText(str(order[4] or ""))
        self.cargo_type.setEditText(str(order[5] or ""))
        self.truck_type.setEditText(str(order[7] or ""))
        self.serial_number.setText(str(order[8] or ""))
        self.receipt_confirmation.setEditText(str(order[9] or ""))
        self.merchant_name.setText(str(order[12] or ""))
        self.seat_number.setText(str(order[13] or ""))
        self.model.setText(str(order[14] or ""))
        self.card_number.setText(str(order[15] or ""))
        self.vehicle_type.setText(str(order[16] or ""))
        self.owner_name.setText(str(order[17] or ""))
        self.national_id.setText(str(order[18] or ""))
        self.driver_national_id.setText(str(order[19] or ""))
        self.phone.setText(str(order[20] or ""))
        self.license_type.setText(str(order[21] or ""))
        self.license_number.setText(str(order[22] or ""))
        self.nahma_number.setText(str(order[26] or ""))
        self.merchant_number.setText(str(order[27] or ""))
        
        # الحقول الجديدة
        self.intsap.setText(str(order[30] or ""))
        self.stop.setText(str(order[31] or ""))
        self.office.setText(str(order[32] or ""))
        self.color.setText(str(order[33] or ""))

        # الحقول النصية الطويلة
        self.extra_data.setPlainText(str(order[28] or ""))
        self.notes.setPlainText(str(order[29] or ""))

        # معالجة التواريخ
        try:
            if order[6]:  # arrival_date
                dt = datetime.fromtimestamp(order[6])
                self.arrival_date.setDate(dt.date())
        except:
            pass

        try:
            if order[10]:  # visa_datetime
                dt = datetime.fromtimestamp(order[10])
                self.visa_dt.setDate(dt.date())
        except:
            pass

        try:
            if order[11]:  # created_datetime
                dt = datetime.fromtimestamp(order[11])
                self.created_dt.setDate(dt.date())
        except:
            pass

        # معالجة الصور
        if order[23]:  # id_card_image
            self.id_card_image = order[23]
            self.id_card_label.setText(os.path.basename(str(order[23])))
        
        if order[24]:  # card_image
            self.card_image = order[24]
            self.card_label.setText(os.path.basename(str(order[24])))
        
        if order[25]:  # license_image
            self.license_image = order[25]
            self.license_label.setText(os.path.basename(str(order[25])))

    # باقي الدوال تبقى كما هي (create_basic_info_group, create_vehicle_info_group, etc.)
    # ... [الكود المتبقي بدون تغيير]

    def create_basic_info_group(self):
        group = QGroupBox("البيانات الأساسية")
        layout = QGridLayout()
        
        # الصف 1
        layout.addWidget(QLabel("اسم السائق:"), 0, 0)
        self.driver_name = QLineEdit()
        layout.addWidget(self.driver_name, 0, 1)
        
        layout.addWidget(QLabel("الرقم الوطني للسائق:"), 0, 2)
        self.driver_national_id = QLineEdit()
        layout.addWidget(self.driver_national_id, 0, 3)
        
        # الصف 2
        layout.addWidget(QLabel("رقم السائق:"), 1, 0)
        self.phone = QLineEdit()
        layout.addWidget(self.phone, 1, 1)
        
        layout.addWidget(QLabel("الرخصة:"), 1, 2)
        self.license_type = QLineEdit()
        layout.addWidget(self.license_type, 1, 3)
        
        # الصف 3
        layout.addWidget(QLabel("رقم الرخصة:"), 2, 0)
        self.license_number = QLineEdit()
        layout.addWidget(self.license_number, 2, 1)
        
        layout.addWidget(QLabel("اسم المالك:"), 2, 2)
        self.owner_name = QLineEdit()
        layout.addWidget(self.owner_name, 2, 3)
        
        # الصف 4
        layout.addWidget(QLabel("الرقم الوطني:"), 3, 0)
        self.national_id = QLineEdit()
        layout.addWidget(self.national_id, 3, 1)
        
        layout.addWidget(QLabel("نوع الطلب "), 3, 2)
        self.vehicle_type = QLineEdit()
        layout.addWidget(self.vehicle_type, 3, 3)
        
        group.setLayout(layout)
        return group

    def create_vehicle_info_group(self):
        group = QGroupBox("بيانات المركبة")
        layout = QGridLayout()
        
        # الصف 1
        layout.addWidget(QLabel("رقم القاطرة:"), 0, 0)
        self.tractor_number = QLineEdit()
        layout.addWidget(self.tractor_number, 0, 1)
        
        layout.addWidget(QLabel("رقم المقعدة:"), 0, 2)
        self.seat_number = QLineEdit()
        layout.addWidget(self.seat_number, 0, 3)
        
        # الصف 2
        layout.addWidget(QLabel("الموديل:"), 1, 0)
        self.model = QLineEdit()
        layout.addWidget(self.model, 1, 1)
        
        layout.addWidget(QLabel("رقم الكرت:"), 1, 2)
        self.card_number = QLineEdit()
        layout.addWidget(self.card_number, 1, 3)
        
        # الصف 3
        layout.addWidget(QLabel("نوع الشاحنة:"), 2, 0)
        self.truck_type = QComboBox()
        self.truck_type.addItems(["عادي", "سكس"])
        layout.addWidget(self.truck_type, 2, 1)
        
        layout.addWidget(QLabel("الرقم التسلسلي:"), 2, 2)
        self.serial_number = QLineEdit()
        layout.addWidget(self.serial_number, 2, 3)
        
        group.setLayout(layout)
        return group

    def create_arrival_info_group(self):
        group = QGroupBox("بيانات الوصول والشحن")
        layout = QGridLayout()
        
        # الصف 0
        layout.addWidget(QLabel("الكمية:"), 0, 0)
        self.quantity = QLineEdit()
        layout.addWidget(self.quantity, 0, 1)
        
        layout.addWidget(QLabel("منطقة الوصول:"), 0, 2)
        self.arrival_area = QLineEdit()
        layout.addWidget(self.arrival_area, 0, 3)
        
        # الصف 1
        layout.addWidget(QLabel("نوع البضاعة:"), 1, 0)
        self.cargo_type = QComboBox()
        self.cargo_type.addItems(["بضاعة جافة", "بضاعة سائلة", "مواد غذائية", "أدوية"," الكترونيات ","ادوات  زراعية ", "ادوات كهربائية","ملابس","أخرى"])
        layout.addWidget(self.cargo_type, 1, 1)
        
        layout.addWidget(QLabel("تاريخ الوصول:"), 1, 2)
        self.arrival_date = QDateEdit()
        self.arrival_date.setDate(QDateTime.currentDateTime().date())
        self.arrival_date.setCalendarPopup(True)
        layout.addWidget(self.arrival_date, 1, 3)
        
        # الصف 2 - تاريخ التأشيرة
        layout.addWidget(QLabel("تاريخ ووقت التاشيرة:"), 2, 0)
        self.visa_dt = QDateEdit()
        self.visa_dt.setDateTime(QDateTime.currentDateTime())
        self.visa_dt.setCalendarPopup(True)
        layout.addWidget(self.visa_dt, 2, 1)
        
        # الصف 3 - تاريخ التسجيل
        layout.addWidget(QLabel("تاريخ ووقت التسجيل:"), 3, 0)
        self.created_dt = QDateEdit()
        self.created_dt.setDateTime(QDateTime.currentDateTime())
        self.created_dt.setCalendarPopup(True)
        layout.addWidget(self.created_dt, 3, 1)
        
        # الصف 4
        layout.addWidget(QLabel("رقم النهمة:"), 4, 0)
        self.nahma_number = QLineEdit()
        layout.addWidget(self.nahma_number, 4, 1)
        
        layout.addWidget(QLabel("رقم التاجر:"), 4, 2)
        self.merchant_number = QLineEdit()
        layout.addWidget(self.merchant_number, 4, 3)
        
        # الصف 5
        layout.addWidget(QLabel("اسم التاجر:"), 5, 0)
        self.merchant_name = QLineEdit()
        layout.addWidget(self.merchant_name, 5, 1)
        
        layout.addWidget(QLabel("تأكيد الاستلام:"), 5, 2)
        self.receipt_confirmation = QComboBox()
        self.receipt_confirmation.addItems(["مؤكد", "في الانتظار", "ملغى"])
        layout.addWidget(self.receipt_confirmation, 5, 3)
        
        # الصف 6
        layout.addWidget(QLabel("بيانات إضافية:"), 6, 0)
        self.extra_data = QTextEdit()
        self.extra_data.setMaximumHeight(80)
        layout.addWidget(self.extra_data, 6, 1, 1, 3)
        
        # الصف 7
        layout.addWidget(QLabel("  ملاحظة /الانتساب:"), 7, 0)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        layout.addWidget(self.notes, 7, 1, 1, 3)

        # الصف 8 - الانتساب
        layout.addWidget(QLabel("الانتساب:"), 8, 0)
        self.intsap = QLineEdit()
        layout.addWidget(self.intsap, 8, 1)

        # الصف 9 - التوقيف
        layout.addWidget(QLabel("التوقيف:"), 9, 0)
        self.stop = QLineEdit()
        layout.addWidget(self.stop, 9, 1)

        # الصف 10 - المكتب
        layout.addWidget(QLabel("المكتب:"), 10, 0)
        self.office = QLineEdit()
        layout.addWidget(self.office, 10, 1)

        # الصف 11 - اللون
        layout.addWidget(QLabel("اللون:"), 11, 0)
        self.color = QLineEdit()
        layout.addWidget(self.color, 11, 1)
        
        group.setLayout(layout)
        return group

    def create_attachments_group(self):
        group = QGroupBox("المرفقات")
        layout = QGridLayout()
        
        # بطاقة الهوية
        layout.addWidget(QLabel("صورة البطاقة:"), 0, 0)
        self.id_card_btn = QPushButton("📷 اختيار صورة البطاقة")
        self.id_card_btn.clicked.connect(lambda: self.select_image("id_card"))
        layout.addWidget(self.id_card_btn, 0, 1)
        self.id_card_label = QLabel("لم يتم اختيار صورة")
        layout.addWidget(self.id_card_label, 0, 2)
        
        # الكرت
        layout.addWidget(QLabel("صورة الكرت:"), 1, 0)
        self.card_btn = QPushButton("📷 اختيار صورة الكرت")
        self.card_btn.clicked.connect(lambda: self.select_image("card"))
        layout.addWidget(self.card_btn, 1, 1)
        self.card_label = QLabel("لم يتم اختيار صورة")
        layout.addWidget(self.card_label, 1, 2)
        
        # الرخصة
        layout.addWidget(QLabel("صورة الرخصة:"), 2, 0)
        self.license_btn = QPushButton("📷 اختيار صورة الرخصة")
        self.license_btn.clicked.connect(lambda: self.select_image("license"))
        layout.addWidget(self.license_btn, 2, 1)
        self.license_label = QLabel("لم يتم اختيار صورة")
        layout.addWidget(self.license_label, 2, 2)
        
        group.setLayout(layout)
        return group

    def select_image(self, image_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"اختر صورة {image_type}", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            if image_type == "id_card":
                self.id_card_image = file_path
                self.id_card_label.setText(os.path.basename(file_path))
            elif image_type == "card":
                self.card_image = file_path
                self.card_label.setText(os.path.basename(file_path))
            elif image_type == "license":
                self.license_image = file_path
                self.license_label.setText(os.path.basename(file_path))

    def save_as_new_order(self):
        """حفظ الطلب كسجل جديد (دائمًا إضافة سجل جديد)"""
        self._save_order(as_new=True)
    

    def _save_order(self, as_new=False):
        try:
            # جمع البيانات من الحقول
            data = (
                self.driver_name.text(),
                self.tractor_number.text(),
                self.quantity.text(),
                self.arrival_area.text(),
                self.cargo_type.currentText(),
                self.arrival_date.date().toPyDate().strftime("%Y-%m-%d"),
                self.truck_type.currentText(),
                self.serial_number.text(),
                self.receipt_confirmation.currentText(),
                self.visa_dt.date().toPyDate().strftime("%Y-%m-%d"),
                  # timestamp للتأشيرة
                self.created_dt.date().toPyDate().strftime("%Y-%m-%d"),  # timestamp للتسجيل
                self.merchant_name.text(),
                self.seat_number.text(),
                self.model.text(),
                self.card_number.text(),
                self.vehicle_type.text(),
                self.owner_name.text(),
                self.national_id.text(),
                self.driver_national_id.text(),
                self.phone.text(),
                self.license_type.text(),
                self.license_number.text(),
                self.id_card_image or "",
                self.card_image or "",
                self.license_image or "",
                self.nahma_number.text(),
                self.merchant_number.text(),
                self.extra_data.toPlainText(),
                self.notes.toPlainText(),
                self.intsap.text(),   # بدلاً من ""
                self.stop.text(),     # بدلاً من ""
                self.office.text(),   # بدلاً من ""
                self.color.text()     # بدلاً من ""
            )


            if as_new or self.order_id is None:
                # ➕ وضع الإضافة: إدخال سجل جديد
                self.db.add_order(data)
                QMessageBox.information(self, "نجاح", "✅ تم إضافة الطلب بنجاح")
            else:
                # ✏️ وضع التعديل: تحديث السجل
                self.db.update_order(self.order_id, data)
                QMessageBox.information(self, "نجاح", "✅ تم تعديل الطلب بنجاح")

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في الحفظ:\n{str(e)}")
    def save_order(self):
        try:
            # جمع البيانات من الحقول
            data = (
                    self.driver_name.text(),
                    self.tractor_number.text(),
                    self.quantity.text(),
                    self.arrival_area.text(),
                    self.cargo_type.currentText(),
                    self.arrival_date.date().toPyDate().strftime("%Y-%m-%d"),
                    self.truck_type.currentText(),
                    self.serial_number.text(),
                    self.receipt_confirmation.currentText(),
                    self.visa_dt.date().toPyDate().strftime("%Y-%m-%d"),
                    # timestamp للتأشيرة
                    self.created_dt.date().toPyDate().strftime("%Y-%m-%d"),  # timestamp للتسجيل
                    self.merchant_name.text(),
                    self.seat_number.text(),
                    self.model.text(),
                    self.card_number.text(),
                    self.vehicle_type.text(),
                    self.owner_name.text(),
                    self.national_id.text(),
                    self.driver_national_id.text(),
                    self.phone.text(),
                    self.license_type.text(),
                    self.license_number.text(),
                    self.id_card_image or "",
                    self.card_image or "",
                    self.license_image or "",
                    self.nahma_number.text(),
                    self.merchant_number.text(),
                    self.extra_data.toPlainText(),
                    self.notes.toPlainText(),
                    self.intsap.text(),   # بدلاً من ""
                    self.stop.text(),     # بدلاً من ""
                    self.office.text(),   # بدلاً من ""
                    self.color.text()     # بدلاً من ""
                )


            if self.order_id is not None:
                # ✏️ وضع التعديل: تحديث السجل
                self.db.update_order(self.order_id, data)
                QMessageBox.information(self, "نجاح", "✅ تم تعديل الطلب بنجاح")
            else:
                # ➕ وضع الإضافة: إدخال سجل جديد
                self.db.add_order(data)
                QMessageBox.information(self, "نجاح", "✅ تم إضافة الطلب بنجاح")

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في الحفظ:\n{str(e)}")



   