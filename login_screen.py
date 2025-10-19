# login_screen.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from main_window import MainWindow

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ضياء اليمن للنقل والاستيراد - تسجيل الدخول")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # الشعار
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        if pixmap.isNull():
            logo_label.setText("🖼️")
            logo_label.setStyleSheet("font-size: 60px;")
        else:
            logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # العنوان
        title = QLabel("🚛 ضياء اليمن للنقل والاستيراد")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("نظام تتبع القاطرات")
        subtitle.setFont(QFont("Amiri", 18))
        subtitle.setStyleSheet("color: grey;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # حقل كلمة المرور
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Amiri", 18))
        self.password_input.setAlignment(Qt.AlignRight)
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        layout.addWidget(self.password_input)

        # زر الدخول
        login_btn = QPushButton("🔓 دخول")
        login_btn.setFont(QFont("Amiri", 18))
        login_btn.setStyleSheet("background-color: green; color: white; padding: 10px;")
        login_btn.clicked.connect(self.check_password)
        layout.addWidget(login_btn)

        self.setLayout(layout)
            
    def check_password(self):
        entered = self.password_input.text().strip()
        if entered != "admin":
            QMessageBox.critical(self, "خطأ", "❌ كلمة المرور غير صحيحة!")
            self.password_input.clear()
            self.password_input.setFocus()
            return

        # هنا كلمة المرور صحيحة
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
