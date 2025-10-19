# main.py
import os
import sys

# إصلاح المسارات لتعمل على Android
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
import sys
from PyQt5.QtWidgets import QApplication
from login_screen import LoginScreen
import os
import sqlite3
# ... باقي استيرادات المكتبات ...

# ========== دالة resource_path هنا ==========




#


def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(1)  # Right to Left
    login_screen = LoginScreen()
    login_screen.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()