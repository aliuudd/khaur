from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QAction, QMenuBar, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from database import Database
from datetime import datetime
from order import regist 
from managem import AddmarScreen# تأكد أن اسم الملف order.py والكلاس regist
from nihme_report_screen     import NihmeReportScreen




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ضياء اليمن للنقل والاستيراد - الشاشة الرئيسية")
        self.setGeometry(100, 100, 1300, 750)
        self.db = Database()
        self.transferred_orders = self.db.get_transferred_orders()
        self.init_ui()

    def init_ui(self):
        # شريط القوائم
        menubar = self.menuBar()
        menubar.setLayoutDirection(Qt.RightToLeft)

        file_menu = menubar.addMenu("📋 قائمة")
        file_menu.setLayoutDirection(Qt.RightToLeft)

        add_action = QAction("📝 إضافة سجل", self)
        add_action.triggered.connect(self.open_add_record)
        # file_menu.addAction(add_action)

        orders_action = QAction("📦 إدارة الطلبات", self)
        orders_action.triggered.connect(self.open_orders_management)
        # file_menu.addAction(orders_action)

        nihme_action = QAction("📄 كشف النهمة", self)
        nihme_action.triggered.connect(self.open_nihme_report)
        # file_menu.addAction(nihme_action)

        member_action = QAction("👥 المنتسبين", self)
        member_action.triggered.connect(self.open_members)
        # file_menu.addAction(member_action)

        reports_action = QAction("📊 تقارير", self)
        reports_action.triggered.connect(self.open_reports)
        file_menu.addAction(reports_action)

        search_action = QAction("🔍 بحث", self)
        search_action.triggered.connect(self.open_search)
        file_menu.addAction(search_action)

        logout_action = QAction("🚪 تسجيل الخروج", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        # الشاشة المركزية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # العنوان
        title = QLabel("📋  بيانات التسجيل ")
        title.setFont(QFont("Amiri", 24, QFont.Bold))
        title.setStyleSheet("color: green;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # جدول الطلبات (11 عمودًا: 10 بيانات + 1 إجراءات)
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "الرقم التسلسلي",
            "اسم السائق",
            "اسم المالك",
            "رقم القاطرة",
            "نوع القاطرة",
            "رقم القعادة",
            "رقم الجوال",
            "تاريخ الوصول",
            "الاستعلامات",      # extra_data
            "ملاحظة النظام",    # notes
            "الإجراءات"
        ])
        self.table.setFont(QFont("Amiri", 10))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)

        # أزرار التحكم
        buttons_layout = QHBoxLayout()

        add_btn = QPushButton("➕ إضافة طلب جديد")
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
        add_btn.clicked.connect(self.open_add_record)
        # buttons_layout.addWidget(add_btn)

        orders_btn = QPushButton("4  قاعده البيانات    ")
        orders_btn.setFont(QFont("Amiri", 16))
        orders_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        orders_btn.clicked.connect(self.open_orders_management)
        buttons_layout.addWidget(orders_btn)

        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setFont(QFont("Amiri", 14))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        refresh_btn.clicked.connect(self.load_recent_orders)
        # buttons_layout.addWidget(refresh_btn)

        layout.addLayout(buttons_layout)

        # زر "بيانات التسجيل" (إضافة طلب جديد عبر regist)
        agg = QPushButton("📝   بينات التسجيل 1  ")
        agg.setFont(QFont("Amiri", 14))
        agg.setStyleSheet("""
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
        agg.clicked.connect(self.newre)



        aggs = QPushButton("📝    كشف النهمه 2  ")
        aggs.setFont(QFont("Amiri", 14))
        aggs.setStyleSheet("""
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
        aggs.clicked.connect(self.newre)


        
                # زر فتح كشف التشطيب
        open_addmar_btn = QPushButton("📋 ادارة الطلبات 3 ")
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
        buttons_layout.addWidget(open_addmar_btn)
        layout.addWidget(agg)



        open_addmar_btnn = QPushButton("📋 كشف النهمة 2  ")
        open_addmar_btnn.setFont(QFont("Amiri", 14))
        open_addmar_btnn.setStyleSheet("""
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
        open_addmar_btnn.clicked.connect(self.open_addmar_screens)
        buttons_layout.addWidget(open_addmar_btnn)



        open_addmarr_btn = QPushButton("📋   الانتسابات ")
        open_addmarr_btn.setFont(QFont("Amiri", 14))
        open_addmarr_btn.setStyleSheet("""
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
        open_addmarr_btn.clicked.connect(self.open_addmarr_screen)
        buttons_layout.addWidget(open_addmarr_btn)
        # layout.addWidget(agg)

        # تحميل البيانات أول مرة
        self.load_recent_orders()
    def open_addmar_screen(self):
        """ ادارة الطلبات """
        dialog = AddmarScreen(self.db)
        dialog.exec_()
    def open_addmar_screens(self):
        """ ادارة الطلبات """
        dialog = NihmeReportScreen(self.db)
        dialog.exec_()
    def open_addmarr_screen(self):
        from members import MainWindoww
        self.mem = MainWindoww()
        self.mem.show()
    def newre(self):
        """فتح نموذج إضافة طلب جديد (regist)"""
        self.gg = regist(self.db)
        self.gg.finished.connect(self.load_recent_orders)  # تحديث عند الإغلاق
        self.gg.show()

    def load_recent_orders(self):
        """تحميل آخر 10 طلبات مع حالة الترحيل"""
        orders = self.db.get_all_orders()
        self.transferred_orders = self.db.get_transferred_orders()  # تحديث القائمة

        recent_orders = orders[:10]
        self.table.setRowCount(len(recent_orders))

        for i, order in enumerate(recent_orders):
            # معالجة تاريخ الوصول (مخزن كـ "YYYY-MM-DD")
            arrival_date = ""
            if order[6]:  # arrival_date
                try:
                    dt = datetime.strptime(str(order[6]), "%Y-%m-%d")
                    arrival_date = dt.strftime("%d/%m/%Y")
                except Exception:
                    arrival_date = str(order[6])

            # ✅ الترتيب الصحيح حسب جدولك
            row_items = [
                str(order[8] or ""),   # الرقم التسلسلي (serial_number)
                str(order[1] or ""),   # اسم السائق
                str(order[17] or ""),  # اسم المالك
                str(order[2] or ""),   # رقم القاطرة
                str(order[7] or ""),   # نوع القاطرة (truck_type)
                str(order[13] or ""),  # رقم القعادة (seat_number)
                str(order[20] or ""),  # رقم الجوال (phone)
                arrival_date,          # تاريخ الوصول
                str(order[28] or ""),  # ✅ الاستعلامات (extra_data)
                str(order[29] or ""),
                
                  # ✅ ملاحظة النظام (notes)
            ]

            # ملء الخلايا (0 إلى 9)
            for col, val in enumerate(row_items):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if order[0] in self.transferred_orders:
                    cell.setBackground(QColor(255, 255, 0))  # أصفر
                self.table.setItem(i, col, cell)

            # العمود 10: زر الإجراءات
            if order[0] in self.transferred_orders:
                btn = QPushButton("✅ تم الترحيل")
                btn.setEnabled(False)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 5px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                """)
            # else:
            #     btn = QPushButton("📤 ترحيل")
            #     btn.setStyleSheet("""
            #         QPushButton {
            #             background-color: #FF9800;
            #             color: white;
            #             padding: 5px;
            #             border-radius: 3px;
            #             font-weight: bold;
            #         }
            #         QPushButton:hover {
            #             background-color: #F57C00;
            #         }
            #     """)
            #     btn.clicked.connect(lambda checked, oid=order[0]: self.transfer_order(oid))
            
            # self.table.setCellWidget(i, 10, btn)

    def transfer_order(self, order_id):
        """ترحيل طلب"""
        try:
            order = self.db.get_order_by_id(order_id)
            if not order:
                QMessageBox.critical(self, "خطأ", "❌ لم يتم العثور على الطلب")
                return

            success = self.db.transfer_to_main_database(order)
            if success:
                self.transferred_orders.add(order_id)
                self.load_recent_orders()
                QMessageBox.information(self, "نجاح", f"✅ تم ترحيل الطلب رقم {order_id} بنجاح")
            else:
                QMessageBox.critical(self, "خطأ", "❌ فشل في ترحيل البيانات")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"❌ خطأ في الترحيل: {str(e)}")

    # --- الدوال الأخرى (بدون تغيير) ---
    def open_add_record(self):
        from add_record_dialog import AddRecordDialog
        dialog = AddRecordDialog(self.db)
        dialog.finished.connect(self.load_recent_orders)
        dialog.exec_()

    def open_orders_management(self):
        from orders_management_screen import OrdersManagementScreen
        dialog = OrdersManagementScreen(self.db)
        dialog.order_transferred.connect(self.on_order_transferred)
        dialog.finished.connect(self.load_recent_orders)
        dialog.exec_()

    def on_order_transferred(self, order_id):
        self.transferred_orders.add(order_id)
        self.load_recent_orders()
        QMessageBox.information(self, "تم الترحيل", f"✅ تم ترحيل الطلب رقم {order_id} بنجاح")

    def open_nihme_report(self):
        from nihme_report_screen import NihmeReportScreen
        dialog = NihmeReportScreen(self.db)
        dialog.exec_()

    def open_members(self):
        from members import MainWindoww
        self.mem = MainWindoww()
        self.mem.show()

    def open_reports(self):
        from reports_screenW import ReportsScreen
        dialog = ReportsScreen(self.db)
        dialog.exec_()

    def open_search(self):
        from search_screen import SearchScreen
        dialog = SearchScreen(self.db)
        dialog.exec_()

    def logout(self):
        reply = QMessageBox.question(
            self, 'تأكيد تسجيل الخروج',
            'هل أنت متأكد من أنك تريد تسجيل الخروج؟',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from login_screen import LoginScreen
            self.login_screen = LoginScreen()
            self.login_screen.show()
            self.close()