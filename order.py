# from PyQt5.QtWidgets import (
#     QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
#     QComboBox, QTextEdit, QDateEdit, QGroupBox, QGridLayout, QMessageBox
# )
# from PyQt5.QtCore import QDateTime, Qt
# from PyQt5.QtGui import QFont
# from datetime import datetime
# from database import Database


# class regist(QDialog):
#     def __init__(self, db: Database, order_id=None, parent=None, order_data=None):
#         super().__init__()
#         self.order_id = order_id
#         self.db = db
#         self.order_data = order_data
       
#         self.setWindowTitle("➕ إضافة طلب جديد")
#         self.setGeometry(100, 100, 800, 600)
#         self.setStyleSheet("background-color: white;")
        
#         self.init_ui()
#         if self.order_id is not None and self.order_data is not None:
#             self.load_data_for_edit()

#     def init_ui(self):
#         layout = QVBoxLayout()
        
#         # مجموعة البيانات الأساسية
#         group = QGroupBox("البيانات الأساسية")
#         grid_layout = QGridLayout()
        
#         # الصف 1
#         grid_layout.addWidget(QLabel("الرقم المسلسل:"), 0, 0)
#         self.serial_number = QLineEdit()
#         grid_layout.addWidget(self.serial_number, 0, 1)
        
#         grid_layout.addWidget(QLabel("اسم السائق:"), 0, 2)
#         self.driver_name = QLineEdit()
#         grid_layout.addWidget(self.driver_name, 0, 3)
        
#         # الصف 2
#         grid_layout.addWidget(QLabel("اسم المالك:"), 1, 0)
#         self.owner_name = QLineEdit()
#         grid_layout.addWidget(self.owner_name, 1, 1)
        
#         grid_layout.addWidget(QLabel("نوع القاطرة:"), 1, 2)
#         self.truck_type = QComboBox()
#         self.truck_type.addItems(["عادي", "سكس"])
#         grid_layout.addWidget(self.truck_type, 1, 3)
        
#         # الصف 3
#         grid_layout.addWidget(QLabel("رقم القاطرة:"), 2, 0)
#         self.tractor_number = QLineEdit()
#         grid_layout.addWidget(self.tractor_number, 2, 1)
        
#         grid_layout.addWidget(QLabel("رقم الجوال:"), 2, 2)
#         self.phone = QLineEdit()
#         grid_layout.addWidget(self.phone, 2, 3)
        
#         # الصف 4
#         grid_layout.addWidget(QLabel("تاريخ الوصول:"), 3, 0)
#         self.arrival_date = QDateEdit()
#         self.arrival_date.setDate(QDateTime.currentDateTime().date())
#         self.arrival_date.setCalendarPopup(True)
#         grid_layout.addWidget(self.arrival_date, 3, 1)
        
#         # الصف 5 - الانتساب
#         grid_layout.addWidget(QLabel("الانتساب:"), 4, 0)
#         self.intsap = QTextEdit()
#         self.intsap.setMaximumHeight(60)
#         grid_layout.addWidget(self.intsap, 4, 1, 1, 3)
        
#         # الصف 6 - الاستعلامات
#         grid_layout.addWidget(QLabel("الاستعلامات:"), 5, 0)
#         self.extra_data = QTextEdit()
#         self.extra_data.setMaximumHeight(60)
#         grid_layout.addWidget(self.extra_data, 5, 1, 1, 3)
        
#         # الصف 7 - ملاحظة
#         grid_layout.addWidget(QLabel("ملاحظة:"), 6, 0)
#         self.notes = QTextEdit()
#         self.notes.setMaximumHeight(60)
#         grid_layout.addWidget(self.notes, 6, 1, 1, 3)
        
#         # الصف 8 - التوقيف
#         grid_layout.addWidget(QLabel("التوقيف:"), 7, 0)
#         self.stop = QTextEdit()
#         self.stop.setMaximumHeight(60)
#         grid_layout.addWidget(self.stop, 7, 1, 1, 3)
        
#         group.setLayout(grid_layout)
#         layout.addWidget(group)
        
#         # زر الحفظ
#         save_btn = QPushButton("💾 حفظ الطلب")
#         save_btn.setFont(QFont("Arial", 14))
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
#         if not self.order_data:
#             return

#         order = self.order_data

#         # تحميل البيانات حسب الأعمدة في قاعدة البيانات
#         self.serial_number.setText(str(order[8] or ""))        # العمود 8: serial_number
#         self.driver_name.setText(str(order[1] or ""))          # العمود 1: driver_name
#         self.owner_name.setText(str(order[17] or ""))          # العمود 17: owner_name
#         self.truck_type.setCurrentText(str(order[7] or ""))    # العمود 7: truck_type
#         self.tractor_number.setText(str(order[2] or ""))       # العمود 2: tractor_number
#         self.phone.setText(str(order[20] or ""))               # العمود 20: phone
#         self.intsap.setPlainText(str(order[30] or ""))         # العمود 30: intsap
#         self.extra_data.setPlainText(str(order[28] or ""))     # العمود 28: extra_data
#         self.notes.setPlainText(str(order[29] or ""))          # العمود 29: notes
#         self.stop.setPlainText(str(order[31] or ""))           # العمود 31: stop

#         # تاريخ الوصول
#         if order[6]:
#             try:
#                 arrival_date = datetime.strptime(str(order[6]), "%Y-%m-%d").date()
#                 self.arrival_date.setDate(arrival_date)
#             except ValueError:
#                 self.arrival_date.setDate(QDateTime.currentDateTime().date())

#     def save_order(self):
#         try:
#             # تجميع البيانات حسب ترتيب الأعمدة في قاعدة البيانات
#             data = (
#                 self.driver_name.text(),           # 1: driver_name
#                 self.tractor_number.text(),        # 2: tractor_number
#                 "",                                # 3: quantity
#                 "",                                # 4: arrival_area
#                 "",                                # 5: cargo_type
#                 self.arrival_date.date().toString("yyyy-MM-dd"),  # 6: arrival_date
#                 self.truck_type.currentText(),     # 7: truck_type
#                 self.serial_number.text(),         # 8: serial_number
#                 "",                                # 9: receipt_confirmation
#                 "",                                # 10: visa_datetime
#                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 11: created_datetime
#                 "",                                # 12: merchant_name
#                 "",                                # 13: seat_number
#                 "",                                # 14: model
#                 "",                                # 15: card_number
#                 "",                                # 16: vehicle_type
#                 self.owner_name.text(),            # 17: owner_name
#                 "",                                # 18: national_id
#                 "",                                # 19: driver_national_id
#                 self.phone.text(),                 # 20: phone
#                 "",                                # 21: license
#                 "",                                # 22: license_number
#                 "",                                # 23: id_card_image
#                 "",                                # 24: card_image
#                 "",                                # 25: license_image
#                 "",                                # 26: nahma_number
#                 "",                                # 27: merchant_number
#                 self.extra_data.toPlainText(),     # 28: extra_data
#                 self.notes.toPlainText(),          # 29: notes
#                 self.intsap.toPlainText(),         # 30: intsap
#                 self.stop.toPlainText(),           # 31: stop
#                 "",                                # 32: office
#                 ""                                 # 33: color
#             )

#             if self.order_id is not None:
#                 # تحديث الطلب الموجود
#                 self.db.update_order(self.order_id, data)
#                 QMessageBox.information(self, "نجاح", "✅ تم تعديل الطلب بنجاح")
#             else:
#                 # إضافة طلب جديد
#                 self.db.add_order(data)
#                 QMessageBox.information(self, "نجاح", "✅ تم إضافة الطلب بنجاح")

#             self.accept()
#         except Exception as e:
#             QMessageBox.critical(self, "خطأ", f"❌ فشل في الحفظ:\n{str(e)}")



from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QTextEdit, QDateEdit, QGroupBox, QGridLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QWidget
)
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from database import Database


class regist(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_order_id = None  # لتخزين معرف الطلب الذي يتم تعديله
        
        self.setWindowTitle("إدارة الطلبات - التسجيل والبحث والتعديل")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # عنوان النافذة
        title = QLabel("إدارة نظام الطلبات")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # إنشاء تبويبات
        tabs = QTabWidget()
        
        # تبويب التسجيل والبحث
        main_tab = self.create_main_tab()
        tabs.addTab(main_tab, "التسجيل والبحث")
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_main_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم البحث
        search_group = QGroupBox("🔍 البحث في الطلبات")
        search_layout = QVBoxLayout()
        
        # شريط البحث
        search_row = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث باسم السائق أو رقم القاطرة أو الرقم المسلسل...")
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 5px;")
        search_row.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 بحث")
        search_btn.setFont(QFont("Arial", 12))
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        search_btn.clicked.connect(self.search_orders)
        search_row.addWidget(search_btn)
        
        clear_search_btn = QPushButton("مسح البحث")
        clear_search_btn.setFont(QFont("Arial", 12))
        clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        clear_search_btn.clicked.connect(self.clear_search)
        search_row.addWidget(clear_search_btn)
        
        search_layout.addLayout(search_row)
        
        # جدول نتائج البحث
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "م", "الرقم المسلسل", "اسم السائق", "رقم القاطرة", "اسم المالك", "رقم الجوال", "الإجراءات"
        ])
        self.results_table.setFont(QFont("Arial", 10))
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setFont(QFont("Arial", 10, QFont.Bold))
        self.results_table.horizontalHeader().setStretchLastSection(True)
        
        # ضبط أبعاد الأعمدة
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.results_table.setColumnWidth(0, 40)
        
        search_layout.addWidget(self.results_table)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # قسم إدخال البيانات
        data_group = QGroupBox("📝 بيانات الطلب")
        grid_layout = QGridLayout()
        
        # الصف 1
        grid_layout.addWidget(QLabel("الرقم المسلسل:"), 0, 0)
        self.serial_number = QLineEdit()
        grid_layout.addWidget(self.serial_number, 0, 1)
        
        grid_layout.addWidget(QLabel("اسم السائق:"), 0, 2)
        self.driver_name = QLineEdit()
        grid_layout.addWidget(self.driver_name, 0, 3)
        
        # الصف 2
        grid_layout.addWidget(QLabel("اسم المالك:"), 1, 0)
        self.owner_name = QLineEdit()
        grid_layout.addWidget(self.owner_name, 1, 1)
        
        grid_layout.addWidget(QLabel("نوع القاطرة:"), 1, 2)
        self.truck_type = QComboBox()
        self.truck_type.addItems(["عادي", "سكس"])
        grid_layout.addWidget(self.truck_type, 1, 3)
        
        # الصف 3
        grid_layout.addWidget(QLabel("رقم القاطرة:"), 2, 0)
        self.tractor_number = QLineEdit()
        grid_layout.addWidget(self.tractor_number, 2, 1)
        
        grid_layout.addWidget(QLabel("رقم الجوال:"), 2, 2)
        self.phone = QLineEdit()
        grid_layout.addWidget(self.phone, 2, 3)
        
        # الصف 4
        grid_layout.addWidget(QLabel("تاريخ الوصول:"), 3, 0)
        self.arrival_date = QDateEdit()
        self.arrival_date.setDate(QDateTime.currentDateTime().date())
        self.arrival_date.setCalendarPopup(True)
        grid_layout.addWidget(self.arrival_date, 3, 1)
        
        # الصف 5 - الانتساب
        grid_layout.addWidget(QLabel("الانتساب:"), 4, 0)
        self.intsap = QTextEdit()
        self.intsap.setMaximumHeight(60)
        grid_layout.addWidget(self.intsap, 4, 1, 1, 3)
        
        # الصف 6 - الاستعلامات
        grid_layout.addWidget(QLabel("الاستعلامات:"), 5, 0)
        self.extra_data = QTextEdit()
        self.extra_data.setMaximumHeight(60)
        grid_layout.addWidget(self.extra_data, 5, 1, 1, 3)
        
        # الصف 7 - ملاحظة
        grid_layout.addWidget(QLabel("ملاحظة:"), 6, 0)
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        grid_layout.addWidget(self.notes, 6, 1, 1, 3)
        
        # الصف 8 - التوقيف
        grid_layout.addWidget(QLabel("التوقيف:"), 7, 0)
        self.stop = QTextEdit()
        self.stop.setMaximumHeight(60)
        grid_layout.addWidget(self.stop, 7, 1, 1, 3)
        
        data_group.setLayout(grid_layout)
        layout.addWidget(data_group)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        # زر تسجيل جديد
        new_btn = QPushButton("🆕 تسجيل جديد")
        new_btn.setFont(QFont("Arial", 14))
        new_btn.setStyleSheet("""
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
        new_btn.clicked.connect(self.new_order)
        button_layout.addWidget(new_btn)
        
        # زر حفظ
        save_btn = QPushButton("💾 حفظ")
        save_btn.setFont(QFont("Arial", 14))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_order)
        button_layout.addWidget(save_btn)
        
        # زر حفظ كسجل جديد
        save_as_new_btn = QPushButton("🆕 حفظ كسجل جديد")
        save_as_new_btn.setFont(QFont("Arial", 14))
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
        
        # زر مسح الحقول
        clear_btn = QPushButton("🗑️ مسح الحقول")
        clear_btn.setFont(QFont("Arial", 14))
        clear_btn.setStyleSheet("""
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
        clear_btn.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        widget.setLayout(layout)
        return widget

    def search_orders(self):
        """البحث في الطلبات"""
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "تحذير", "⚠️ يرجى إدخال نص للبحث!")
            return

        try:
            # البحث في قاعدة البيانات
            orders = self.db.search_orders(search_text)
            self.display_search_results(orders)
            
            if not orders:
                QMessageBox.information(self, "نتائج البحث", "❌ لم يتم العثور على نتائج للبحث")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في البحث:\n{str(e)}")

    def display_search_results(self, orders):
        """عرض نتائج البحث في الجدول"""
        self.results_table.setRowCount(len(orders))
        
        for i, order in enumerate(orders):
            # تعبئة البيانات في الجدول
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(order[8] or "")))  # serial_number
            self.results_table.setItem(i, 2, QTableWidgetItem(str(order[1] or "")))  # driver_name
            self.results_table.setItem(i, 3, QTableWidgetItem(str(order[2] or "")))  # tractor_number
            self.results_table.setItem(i, 4, QTableWidgetItem(str(order[17] or ""))) # owner_name
            self.results_table.setItem(i, 5, QTableWidgetItem(str(order[20] or ""))) # phone
            
            # زر التعديل
            edit_btn = QPushButton("✏️ تعديل")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            edit_btn.order_id = order[0]  # تخزين معرف الطلب
            edit_btn.order_data = order   # تخزين بيانات الطلب كاملة
            edit_btn.clicked.connect(lambda checked, btn=edit_btn: self.load_order_for_edit(btn))
            self.results_table.setCellWidget(i, 6, edit_btn)

    def load_order_for_edit(self, button):
        """تحميل بيانات الطلب للتعديل"""
        order_id = button.order_id
        order_data = button.order_data
        
        self.current_order_id = order_id

        # تحميل البيانات في الحقول
        self.serial_number.setText(str(order_data[8] or ""))
        self.driver_name.setText(str(order_data[1] or ""))
        self.owner_name.setText(str(order_data[17] or ""))
        self.truck_type.setCurrentText(str(order_data[7] or ""))
        self.tractor_number.setText(str(order_data[2] or ""))
        self.phone.setText(str(order_data[20] or ""))
        self.intsap.setPlainText(str(order_data[30] or ""))
        self.extra_data.setPlainText(str(order_data[28] or ""))
        self.notes.setPlainText(str(order_data[29] or ""))
        self.stop.setPlainText(str(order_data[31] or ""))

        # تاريخ الوصول
        if order_data[6]:
            try:
                # إذا كان timestamp
                arrival_date = datetime.fromtimestamp(order_data[6]).date()
                self.arrival_date.setDate(arrival_date)
            except (TypeError, ValueError):
                try:
                    # إذا كان نصاً
                    arrival_date = datetime.strptime(str(order_data[6]), "%Y-%m-%d").date()
                    self.arrival_date.setDate(arrival_date)
                except ValueError:
                    self.arrival_date.setDate(QDateTime.currentDateTime().date())

        QMessageBox.information(self, "نجاح", "✅ تم تحميل بيانات الطلب للتعديل!")

    def new_order(self):
        """بدء تسجيل طلب جديد"""
        self.current_order_id = None
        self.clear_fields()
        QMessageBox.information(self, "تهيئة", "🆕 جاهز لتسجيل طلب جديد")

    def save_order(self):
        """حفظ الطلب (تعديل إذا كان هناك current_order_id، أو إضافة إذا لم يكن)"""
        self._save_order()

    def save_as_new_order(self):
        """حفظ الطلب كسجل جديد (دائمًا إضافة سجل جديد)"""
        self._save_order(as_new=True)

    def _save_order(self, as_new=False):
        try:
            # التحقق من الحقول المطلوبة
            if not self.driver_name.text().strip() or not self.tractor_number.text().strip():
                QMessageBox.warning(self, "تحذير", "⚠️ يرجى ملء الحقول المطلوبة (اسم السائق ورقم القاطرة)!")
                return

            # تجميع البيانات حسب ترتيب الأعمدة في قاعدة البيانات
            data = (
                self.driver_name.text().strip(),           # 1: driver_name
                self.tractor_number.text().strip(),        # 2: tractor_number
                "",                                       # 3: quantity
                "",                                       # 4: arrival_area
                "",                                       # 5: cargo_type
                self.arrival_date.date().toString("yyyy-MM-dd"),  # 6: arrival_date
                self.truck_type.currentText(),            # 7: truck_type
                self.serial_number.text().strip(),        # 8: serial_number
                "",                                       # 9: receipt_confirmation
                "",                                       # 10: visa_datetime
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 11: created_datetime
                "",                                       # 12: merchant_name
                "",                                       # 13: seat_number
                "",                                       # 14: model
                "",                                       # 15: card_number
                "",                                       # 16: vehicle_type
                self.owner_name.text().strip(),           # 17: owner_name
                "",                                       # 18: national_id
                "",                                       # 19: driver_national_id
                self.phone.text().strip(),                # 20: phone
                "",                                       # 21: license
                "",                                       # 22: license_number
                "",                                       # 23: id_card_image
                "",                                       # 24: card_image
                "",                                       # 25: license_image
                "",                                       # 26: nahma_number
                "",                                       # 27: merchant_number
                self.extra_data.toPlainText().strip(),    # 28: extra_data
                self.notes.toPlainText().strip(),         # 29: notes
                self.intsap.toPlainText().strip(),        # 30: intsap
                self.stop.toPlainText().strip(),          # 31: stop
                "",                                       # 32: office
                ""                                        # 33: color
            )

            if as_new or self.current_order_id is None:
                # ➕ وضع الإضافة: إدخال سجل جديد
                success = self.db.add_order(data)
                if success:
                    QMessageBox.information(self, "نجاح", "✅ تم إضافة الطلب الجديد بنجاح")
                    self.clear_fields()
                    # تحديث نتائج البحث إذا كان هناك بحث نشط
                    if self.search_input.text().strip():
                        self.search_orders()
                else:
                    QMessageBox.critical(self, "خطأ", "❌ فشل في إضافة الطلب")
            else:
                # ✏️ وضع التعديل: تحديث السجل
                success = self.db.update_order(self.current_order_id, data)
                if success:
                    QMessageBox.information(self, "نجاح", "✅ تم تعديل الطلب بنجاح")
                    # تحديث نتائج البحث
                    if self.search_input.text().strip():
                        self.search_orders()
                else:
                    QMessageBox.critical(self, "خطأ", "❌ فشل في تعديل الطلب")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ فشل في الحفظ:\n{str(e)}")

    def clear_fields(self):
        """مسح جميع الحقول"""
        self.serial_number.clear()
        self.driver_name.clear()
        self.owner_name.clear()
        self.truck_type.setCurrentIndex(0)
        self.tractor_number.clear()
        self.phone.clear()
        self.arrival_date.setDate(QDateTime.currentDateTime().date())
        self.intsap.clear()
        self.extra_data.clear()
        self.notes.clear()
        self.stop.clear()

    def clear_search(self):
        """مسح البحث ونتائجه"""
        self.search_input.clear()
        self.results_table.setRowCount(0)