# add_record_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QPushButton, QCheckBox,QDateTimeEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
from PyQt5.QtCore import QEvent
from database import Database

class AddRecordDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("📝 إضافة سجل جديد")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: white;")
        self.init_ui()
        self.flagged_checkbox.installEventFilter(self)
        self._ignore_checkbox_change = False
        

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self._ignore_checkbox_change = False

        

        # عنوان الشاشة
        title = QLabel("📝 إضافة سجل جديد")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.truck_inputt = QLineEdit()
        self.truck_inputt.setFont(QFont("Amiri", 18))
        self.truck_inputt.setAlignment(Qt.AlignRight)
        self.truck_inputt.setPlaceholderText("م")
        layout.addWidget(self.truck_inputt)
        # حقول الإدخال
        self.truck_input = QLineEdit()
        self.truck_input.setFont(QFont("Amiri", 18))
        self.truck_input.setAlignment(Qt.AlignRight)
        self.truck_input.setPlaceholderText("رقم القاطرة")
        layout.addWidget(self.truck_input)

        self.driver_input = QLineEdit()
        self.driver_input.setFont(QFont("Amiri", 18))
        self.driver_input.setAlignment(Qt.AlignRight)
        self.driver_input.setPlaceholderText("اسم السائق")
        layout.addWidget(self.driver_input)

        self.phone_input = QLineEdit()
        self.phone_input.setFont(QFont("Amiri", 18))
        self.phone_input.setAlignment(Qt.AlignRight)
        self.phone_input.setPlaceholderText("رقم السائق")
        layout.addWidget(self.phone_input)

        # تاريخ الوصول
        self.date_input = QDateTimeEdit()
        self.date_input.setFont(QFont("Amiri", 18))
        self.date_input.setAlignment(Qt.AlignRight)
        self.date_input.setDateTime(datetime.now())
        self.date_input.setDisplayFormat("dd/MM/yyyy - hh:mm AP")
        layout.addWidget(self.date_input)
        # في init_ui أو مكان تهيئة الواجهة
        self.order_type_input = QLineEdit()
        self.order_type_input.setPlaceholderText("نوع الطلب")
        layout.addWidget(self.order_type_input)

        self.merchant_name_input = QLineEdit()
        self.merchant_name_input.setPlaceholderText("اسم التاجر")
        layout.addWidget(self.merchant_name_input)

        
        self.flagged_checkbox = QCheckBox("إرجاع الى نظام الدور")
        self.flagged_checkbox.installEventFilter(self)
        layout.addWidget(self.flagged_checkbox)
        # return_btn = QPushButton("🔒 إرجاع إلى نظام الدور")
        # return_btn.setFont(QFont("Amiri", 18))
        # return_btn.setStyleSheet("background-color: orange; color: black; padding: 10px;")
        # return_btn.clicked.connect(self.return_to_queue)
        # layout.addWidget(return_btn)



        # أزرار الحفظ والإلغاء
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setFont(QFont("Amiri", 18))
        cancel_btn.setStyleSheet("background-color: grey; color: white; padding: 10px;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 حفظ")
        save_btn.setFont(QFont("Amiri", 18))
        save_btn.setStyleSheet("background-color: green; color: white; padding: 10px;")
        save_btn.clicked.connect(self.save_record)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
    def eventFilter(self, source, event):
       

        if source == self.flagged_checkbox and event.type() == QEvent.MouseButtonRelease:
            # فقط إذا لم يكن مفعلًا مسبقًا (أي يريد المستخدم التأشير)
            if not self.flagged_checkbox.isChecked():
                password, ok = QInputDialog.getText(self, "التحقق", "أدخل الرقم السري:", QLineEdit.Password)
                if ok and password == "ali":
                    self.flagged_checkbox.setChecked(True)
                    QMessageBox.information(self, "نجاح", "✅ تم التأشير بنجاح.")
                else:
                    QMessageBox.warning(self, "خطأ", "❌ الرقم السري غير صحيح.")
                return True  # ← منع checkbox من تغيير حالته تلقائيًا

            else:
                # إذا أردت حماية إلغاء التأشير أيضًا، أضف هنا نفس منطق التحقق
                self.flagged_checkbox.setChecked(False)
                return True

        return super().eventFilter(source, event)

    def on_checkbox_clicked(self, currently_checked):
    # نعيد الحالة كما كانت (نمنع التغيير)
        self.flagged_checkbox.blockSignals(True)  # إيقاف مؤقت للإشارات لمنع الحلقة
        self.flagged_checkbox.setChecked(not currently_checked)  # عكس الحالة مؤقتاً
        self.flagged_checkbox.blockSignals(False)  # إعادة تفعيل الإشارات

        if not currently_checked:  # المستخدم يريد التأشير (تشغيل)
            password, ok = QInputDialog.getText(self, "التحقق", "أدخل الرقم السري:", QLineEdit.Password)
            if ok and password == "ali":
                QMessageBox.information(self, "نجاح", "✅ تم التأشير بنجاح.")
                self.flagged_checkbox.setChecked(True)  # نعيد التفعيل يدويًا
            else:
                QMessageBox.warning(self, "خطأ", "❌ الرقم السري غير صحيح.")
        else:
            # إذا أردت منع الإلغاء أيضًا بكلمة سر، ضع التحقق هنا.
            self.flagged_checkbox.setChecked(False)  # المستخدم ألغى التأشير، نسمح بذلك أو نتحقق حسب الحاجة



    def save_record(self):

        
        idd   =  self.truck_inputt.text().strip()
        truck = self.truck_input.text().strip()
        driver = self.driver_input.text().strip()
        phone = self.phone_input.text().strip()
        timestamp = self.date_input.dateTime().toString("dd-MM-yyyy")
        
        order_type = self.order_type_input.text().strip()  # مثلاً حقل جديد
        merchant_name = self.merchant_name_input.text().strip()  # حقل جديد
        flagged = self.flagged_checkbox.isChecked()  # حالة التأشير، checkbox

        if not all([idd,truck, driver, phone, order_type, merchant_name]):
            QMessageBox.critical(self, "خطأ", "يرجى ملء جميع الحقول!")
            return

        self.db.get_all_orders()
        QMessageBox.information(self, "نجاح", "تم الحفظ بنجاح!")
        self.accept()
