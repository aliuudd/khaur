


import sys
import os
import shutil
import sqlite3
from datetime import datetime
import json
import ast

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QDateEdit,
    QComboBox, QCheckBox, QPushButton, QGridLayout, QGroupBox,
    QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QDate

# PDF + Arabic shaping
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

DB_FILE = "forms.db"
STORAGE_DIR = "stored_files"
FONT_TTF = "assets/fonts/Amiri-Regular.ttf"

os.makedirs(STORAGE_DIR, exist_ok=True)

# ------------------------------------------------
## Database Helpers
# ------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS forms (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             member_id TEXT NOT NULL UNIQUE, 
             name TEXT NOT NULL,
             created_at TEXT NOT NULL, 
             pdf_path TEXT,
             idcard_path TEXT,
             data TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_record(member_id, name, pdf_path, idcard_path, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    data_json = json.dumps(data) 

    c.execute('''
    INSERT OR REPLACE INTO forms (member_id, name, created_at, pdf_path, idcard_path, data)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (member_id, name, now, pdf_path, idcard_path, data_json))
    
    conn.commit()
    conn.close()

def load_record(member_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM forms WHERE member_id = ?', (member_id,))
    row = c.fetchone()
    conn.close()
    return row

# ------------------------------------------------
## Arabic Utilities and PDF Generation
# ------------------------------------------------
def fix_arabic(text: str) -> str:
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return bidi_text

def generate_pdf(data, filename, idcard_path=None, additional_images=None):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    import arabic_reshaper
    from bidi.algorithm import get_display
    import os

    def fix(text):
        if not text or not isinstance(text, str):
            return ""
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except:
            return str(text)
        
    if not os.path.exists(FONT_TTF):
        raise FileNotFoundError(f"الخط المطلوب غير موجود: {FONT_TTF}")
    pdfmetrics.registerFont(TTFont('ArabicFont', FONT_TTF))

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    title = fix("عقد انتساب شاحنة لمكتب نقل بتاريخ")
    c.setFont("ArabicFont", 16)
    c.drawCentredString(width / 2, height - 50, title)
    c.line(50, height - 70, width - 50, height - 70)

    date_str = data.get('contract_date', '__/__/____')
    intro = fix(f"الموافق {date_str} إنه في يوم ________ 2025م حرر بين كلا من:")
    c.setFont("ArabicFont", 12)
    c.drawCentredString(width / 2, height - 100, intro)

    y = height - 130

    # الطرف الأول
    c.setFont("ArabicFont", 12)
    c.drawCentredString(width / 2, y, fix("1- مكتب نقل البضائع الموضحة بياناته ادناه ويسمى لاغراض هذا العقد بالطرف الاول"))
    y -= 25
    
    table_data = [
        [fix("الصفة القانونية لمدير المكتب أو المنشأة"), fix("اسم مدير المكتب أو المنشأة")],
        [fix(data.get('manager_legal_status', '')), fix(data.get('office_manager', ''))],
        [fix(f"تاريخ الإصدار: {data.get('manager_id_issue_date', '')}"), fix(f"رقمها: {data.get('manager_id_number', '')} - نوع الهوية: {data.get('manager_id_type', '')}")],
        [fix("مكان نشاط المكتب أو المنشأة"), fix("عدد الفروع إن وجدت")],
        [fix(data.get('office_location', '')), fix(data.get('office_branches', ''))],
        [fix("الشكل القانوني"), fix("اسم المكتب أو المنشأة التجارية")],
        [fix(data.get('office_legal_form', '')), fix(data.get('office_name', ''))],
        [fix(f"واتساب: {data.get('office_whatsapp', '')}"), fix(f"الجوال: {data.get('office_mobile', '')} - الثابت: {data.get('office_landline', '')}")]
    ]

    table = Table(table_data, colWidths=[250, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    w, h = table.wrapOn(c, width, height)
    table.drawOn(c, (width - w) / 2, y - h)
    y = y - h - 15
    
    # نوع النقل
    transport_types = []
    if data.get('transport_heavy') == 'True': transport_types.append(fix("ثقيل"))
    if data.get('transport_medium') == 'True': transport_types.append(fix("متوسط"))
    if data.get('transport_light') == 'True': transport_types.append(fix("خفيف"))
    transport_str = fix("نوع النقل: ") + " - ".join(transport_types) if transport_types else fix("نوع النقل: ")

    scopes = []
    if data.get('scope_domestic') == 'True': scopes.append(fix("داخلي"))
    if data.get('scope_international') == 'True': scopes.append(fix("دولي"))
    scope_str = fix("نوع النقل: ") + " - ".join(scopes) if scopes else fix("نوع النقل: ")

    activities = []
    if data.get('activity_freight') == 'True': activities.append(fix("نقل بضائع"))
    if data.get('activity_freight_load') == 'True': activities.append(fix("نقل بضائع بالحموله"))
    activity_str = fix("نوع النشاط: ") + " - ".join(activities) if activities else fix("نوع النشاط: ")

    categories = []
    if data.get('vehicle_type_heavy') == 'True': categories.append(fix("ثقيل"))
    elif data.get('vehicle_type_medium') == 'True': categories.append(fix("متوسط"))
    elif data.get('vehicle_type_light') == 'True': categories.append(fix("خفيف"))
    category_str = fix("تصنيف النقل: ") + " - ".join(categories) if categories else fix("تصنيف النقل: ")

    extra_data = [
        [fix(f"عدد التنقلات التابعة والمنتسبة: {data.get('affiliated_vehicles', '')}"), category_str],
        [activity_str, scope_str],
        ["", transport_str]
    ]

    extra_table = Table(extra_data, colWidths=[250, 250])
    extra_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    w, h = extra_table.wrapOn(c, width, height)
    extra_table.drawOn(c, (width - w) / 2, y - h)
    y = y - h - 12

    # الطرف الثاني
    c.setFont("ArabicFont", 12)
    c.drawCentredString(width / 2, y, fix("2- مالك شاحنة نقل البضائع الموضحه بياناته ادناة ويسمى لاغرام هذا العقد بالطرف الثاني"))
    y -= 25

    vehicle_data = [
        ["", fix("بيانات المقطورة"), "", fix("بيانات الناقلة")],
        [
            fix("منطقة التحميل"), 
            "\n".join([
                ("خفيف" if data.get('vehicle_type_light') == 'True' else ""),
                ("متوسط" if data.get('vehicle_type_medium') == 'True' else ""),
                ("ثقيل" if data.get('vehicle_type_heavy') == 'True' else "")
            ]),
            fix(f"الحمولة (طن): {data.get('payload', '')}"),
            fix(f"اللون: {data.get('vehicle_color', '')}"),
            fix(f"رقم اللوحة: {data.get('vehicle_plate', '')}")
        ],
        [
            "",
            fix(f"رقم الشاسية: {data.get('trailer_chassis', '')}"),
            "",
            fix(f"رقم الشاسية: {data.get('vehicle_chassis', '')}"),
            fix(f"الشركة المصنعة: {data.get('vehicle_manufacturer', '')}")
        ],
        [
            "",
            fix(f"رقم المقطورة: {data.get('trailer_number', '')}"),
            "",
            fix(f"عدد المحاور: {data.get('vehicle_axles', '')}"),
            fix(f"الموديل/تاريخ الصنع: {data.get('vehicle_manufacture_date', '')}")
        ],
        [
            fix("نوع الناقلة"),
            "",
            fix("رقم كرت الناقلة"),
            fix(f"رقم اللوحة الإضافية: {data.get('vehicle_plate2', '')}"),
            fix(f"جهة الإصدار: {data.get('vehicle_issuing_authority', '')}")
        ],
        [
            "\n".join([
             (fix("خفيف") if data.get('vehicle_type_light') == 'True' else ""),
             (fix("متوسط") if data.get('vehicle_type_medium') == 'True' else ""),
             (fix("ثقيل") if data.get('vehicle_type_heavy') == 'True' else "")
            ]),
            "",
            fix(data.get('vehicle_card_number', '')),
            "",
            ""
        ]
    ]

    vehicle_table = Table(vehicle_data, colWidths=[100, 150, 100, 100, 100])
    vehicle_table.setStyle(TableStyle([
        ('SPAN', (1, 0), (1, 0)),
        ('SPAN', (3, 0), (4, 0)),
        ('BACKGROUND', (1, 0), (1, 0), colors.lightgrey),
        ('BACKGROUND', (3, 0), (4, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    w, h = vehicle_table.wrapOn(c, width, height)
    vehicle_table.drawOn(c, (width - w) / 2, y - h)
    y = y - h - 15

    # بيانات السائق
    
    c.setFont("ArabicFont", 12)
    c.drawCentredString(width / 2, y, fix("بيانات السائق الشخصيه "))
    y -= 25

    driver_data = [
        [fix("رخصة القيادة"), fix("الاتصال"), fix("البيانات الشخصية")],
        [
            fix(f"رقمها ({data.get('driver_license_number', '')})\n"
                f"تاريخ إصدارها: {data.get('driver_license_issue_date', '')}\n"
                f"مكان إصدارها: {data.get('driver_license_issue_place', '')}"),
            fix(f"الهاتف: {data.get('driver_phone', '')}\n"
                f"واتساب: {data.get('driver_whatsapp', '')}"),
            fix(f"الاسم: {data.get('driver_name', '')}\n"
                f"الهوية: {data.get('driver_id', '')}")
        ]
    ]

    driver_table = Table(driver_data, colWidths=[180, 160, 160])
    driver_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    w, h = driver_table.wrapOn(c, width, height)
    driver_table.drawOn(c, (width - w) / 2, y - h)
    y = y - h - 15

    # بيانات المالك
    c.setFont("ArabicFont", 12)
    c.drawCentredString(width / 2, y, fix("بيانات المالك "))
    y -= 25

    owner_data = [
        [fix("واتساب"), fix("النقال"), fix("الهوية"), fix("الاسم")],
        [
            fix(data.get('owner_whatsapp', '')),
            fix(data.get('owner_mobile', '')),
            fix(data.get('owner_id', '')),
            fix(data.get('owner_name', ''))
        ]
    ]

    owner_table = Table(owner_data, colWidths=[125, 125, 125, 125])
    owner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), "ArabicFont"),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    w, h = owner_table.wrapOn(c, width, height)
    owner_table.drawOn(c, (width - w) / 2, y - h)

    # التوقيعات
    bottom_margin = 50
    c.setFont("ArabicFont", 10)
    c.drawString(60, bottom_margin + 40, fix("اسم المكتب: ___________________"))
    c.drawString(60, bottom_margin + 20, fix("التوقيع: _______________"))
    c.drawString(60, bottom_margin, fix("الختم: _______________"))
    c.drawRightString(width - 60, bottom_margin + 40, fix("اسم السائق: ___________________"))
    c.drawRightString(width - 60, bottom_margin + 20, fix("التوقيع: _______________"))
    c.drawRightString(width - 60, bottom_margin, fix("البصمة: _______________"))

    # ========== الصفحة الثانية: صورة بطاقة الهوية ==========
    if idcard_path and os.path.exists(idcard_path):
        c.showPage()
        c.setFont("ArabicFont", 14)
        c.drawCentredString(width / 2, height - 50, fix("صورة بطاقة الهوية"))
        c.line(50, height - 70, width - 50, height - 70)
        
        try:
            c.drawImage(idcard_path, 100, height - 400, width - 200, 300, preserveAspectRatio=True)
        except Exception as e:
            c.setFont("ArabicFont", 10)
            c.drawCentredString(width / 2, height - 200, fix(f"فشل تحميل الصورة: {str(e)}"))

    # ========== الصفحات الإضافية للصور الخمس ==========
    image_titles = [
        "",
        "", 
        "",
        "",
        ""
    ]

    if additional_images is None:
        additional_images = [None] * 5

    # for i, (image_path, title) in enumerate(zip(additional_images, image_titles)):
    #     c.showPage()
    #     c.setFont("ArabicFont", 14)
    #     c.drawCentredString(width / 2, height - 50, fix(title))
    #     c.line(50, height - 70, width - 50, height - 70)


        # ========== صفحة واحدة تحتوي جميع الصور ==========

    if idcard_path or any(additional_images):
        c.showPage()
        c.setFont("ArabicFont", 10)
        c.drawCentredString(width / 2, height - 50, fix("صور المنتسب"))
        c.line(50, height - 70, width - 50, height - 70)

        # إحداثيات البداية
        x_start = 70
        y_start = height - 180
        img_w = 150
        img_h = 120
        spacing_x = 20
        spacing_y = 30
        col = 0
        row = 0

        # قائمة بجميع الصور: الهوية أولاً ثم الصور الخمس
        all_images = [idcard_path] + additional_images

        for img in all_images:
            if img and os.path.exists(img):
                try:
                    x = x_start + (col * (img_w + spacing_x))
                    y = y_start - (row * (img_h + spacing_y))
                    c.drawImage(img, x, y, width=img_w, height=img_h, preserveAspectRatio=True)
                    col += 1
                    if col >= 3:  # بعد 3 صور ينتقل إلى الصف التالي
                        col = 0
                        row += 1
                except Exception as e:
                    c.setFont("ArabicFont", 8)
                    c.drawCentredString(width / 2, height - 300, fix(f"خطأ تحميل صورة: {str(e)}"))
                    c.save()

        
    #     if image_path and os.path.exists(image_path):
    #         try:
    #             c.drawImage(image_path, 100, height - 400, width - 200, 300, preserveAspectRatio=True)
    #         except Exception as e:
    #             c.setFont("ArabicFont", 10)
    #             c.drawCentredString(width / 2, height - 200, fix(f"فشل تحميل الصورة: {str(e)}"))
    #     else:
    #         c.setFont("ArabicFont", 12)
    #         c.drawCentredString(width / 2, height - 200, fix("لا توجد صورة متاحة"))
        
    #     c.setFont("ArabicFont", 10)
    #     c.drawCentredString(width / 2, 30, fix(f"الصفحة {i + 3}"))


        

    c.save()

# ------------------------------------------------
## PyQt UI
# ------------------------------------------------
class MainWindoww(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بيانات الانتساب")
        self.resize(1100, 800)
        self.idcard_path = None
        self.additional_images = [None] * 5  # لتخزين مسارات 5 صور إضافية
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header: title and date
        header_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        header_layout.addWidget(QLabel("تاريخ العقد:"))
        header_layout.addWidget(self.date_edit)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        
        # Group: Office / الطرف الاول
        office_group = QGroupBox("الطرف الأول - بيانات المكتب/المنشأة")
        grid = QGridLayout()
        # Row 0
        grid.addWidget(QLabel("اسم مدير المكتب/المنشأة:"), 0, 0)
        self.manager_name = QLineEdit(); grid.addWidget(self.manager_name, 0, 1)
        grid.addWidget(QLabel("الصفة القانونية:"), 0, 2)
        self.manager_status = QLineEdit(); grid.addWidget(self.manager_status, 0, 3)
        
        # Row 1
        grid.addWidget(QLabel("نوع الهوية:"), 1, 0)
        self.id_type = QLineEdit(); grid.addWidget(self.id_type, 1, 1)
        grid.addWidget(QLabel("رقم الهوية:"), 1, 2)
        self.id_number = QLineEdit(); grid.addWidget(self.id_number, 1, 3)
        grid.addWidget(QLabel("تاريخ الإصدار:"), 1, 4)
        self.id_issue = QLineEdit(); grid.addWidget(self.id_issue, 1, 5)

        # Row 2 office details
        grid.addWidget(QLabel("اسم المكتب/المنشأة:"), 2, 0)
        self.office_name = QLineEdit(); grid.addWidget(self.office_name, 2, 1)
        grid.addWidget(QLabel("الشكل القانوني:"), 2, 2)
        self.office_legal = QLineEdit(); grid.addWidget(self.office_legal, 2, 3)

        grid.addWidget(QLabel("عدد الفروع:"), 3, 0)
        self.office_branches = QLineEdit(); grid.addWidget(self.office_branches, 3, 1)
        grid.addWidget(QLabel("مكان النشاط:"), 3, 2)
        self.office_place = QLineEdit(); grid.addWidget(self.office_place, 3, 3)

        grid.addWidget(QLabel("هاتف ثابت:"), 4, 0)
        self.phone_fixed = QLineEdit(); grid.addWidget(self.phone_fixed, 4, 1)
        grid.addWidget(QLabel("هاتف جوال:"), 4, 2)
        self.phone_mobile = QLineEdit(); grid.addWidget(self.phone_mobile, 4, 3)
        grid.addWidget(QLabel("واتساب:"), 4, 4)
        self.phone_whatsapp = QLineEdit(); grid.addWidget(self.phone_whatsapp, 4, 5)

        # transport intensity checkboxes
        grid.addWidget(QLabel("قشة النقل (ثقيل/متوسط/خفيف):"), 5, 0)
        self.chq_heavy = QCheckBox("ثقيل"); grid.addWidget(self.chq_heavy, 5, 1)
        self.chq_med = QCheckBox("متوسط"); grid.addWidget(self.chq_med, 5, 2)
        self.chq_light = QCheckBox("خفيف"); grid.addWidget(self.chq_light, 5, 3)

        grid.addWidget(QLabel("نوع النقل (داخلي/دولي):"), 6, 0)
        self.ch_in = QCheckBox("داخلي"); grid.addWidget(self.ch_in, 6, 1)
        self.ch_out = QCheckBox("دولي"); grid.addWidget(self.ch_out, 6, 2)

        grid.addWidget(QLabel("نوع النشاط:"), 7, 0)
        self.act_1 = QCheckBox("نقل بضائع"); grid.addWidget(self.act_1, 7, 1)
        self.act_2 = QCheckBox("نقل بضائع بالحمولة"); grid.addWidget(self.act_2, 7, 2)

        grid.addWidget(QLabel("عدد التنقلات:"), 8, 0)
        self.num_movements = QLineEdit(); grid.addWidget(self.num_movements, 8, 1)

        office_group.setLayout(grid)
        main_layout.addWidget(office_group)

        # Group: Vehicle & Trailer (الطرف الثاني)
        vt_group = QGroupBox("الطرف الثاني - بيانات المركبة والمقطورة")
        vt_layout = QGridLayout()

        # Truck (ناقلة)
        vt_layout.addWidget(QLabel("الشركة المصنعة:"), 0, 0)
        self.truck_maker = QLineEdit(); vt_layout.addWidget(self.truck_maker, 0, 1)
        vt_layout.addWidget(QLabel("رقم اللوحة:"), 0, 2)
        self.truck_plate = QLineEdit(); vt_layout.addWidget(self.truck_plate, 0, 3)
        vt_layout.addWidget(QLabel("اللون:"), 0, 4)
        self.truck_color = QLineEdit(); vt_layout.addWidget(self.truck_color, 0, 5)

        vt_layout.addWidget(QLabel("تاريخ الصنع:"), 1, 0)
        self.truck_year = QLineEdit(); vt_layout.addWidget(self.truck_year, 1, 1)
        vt_layout.addWidget(QLabel("رقم القعدة الشاسية:"), 1, 2)
        self.truck_chassis = QLineEdit(); vt_layout.addWidget(self.truck_chassis, 1, 3)
        vt_layout.addWidget(QLabel("عدد المحاور:"), 1, 4)
        self.truck_axles = QLineEdit(); vt_layout.addWidget(self.truck_axles, 1, 5)

        vt_layout.addWidget(QLabel("رقم كرت الناقلة:"), 2, 0)
        self.truck_card = QLineEdit(); vt_layout.addWidget(self.truck_card, 2, 1)
        vt_layout.addWidget(QLabel("جهة الاصدار:"), 2, 2)
        self.truck_card_issuer = QLineEdit(); vt_layout.addWidget(self.truck_card_issuer, 2, 3)

        vt_layout.addWidget(QLabel("نوع الناقلة:"), 3, 0)
        self.truck_type_light = QCheckBox("خفيف"); vt_layout.addWidget(self.truck_type_light, 3, 1)
        self.truck_type_med = QCheckBox("متوسط"); vt_layout.addWidget(self.truck_type_med, 3, 2)
        self.truck_type_heavy = QCheckBox("ثقيل"); vt_layout.addWidget(self.truck_type_heavy, 3, 3)

        # Trailer (مقطورة)
        vt_layout.addWidget(QLabel("رقم المقطورة:"), 4, 0)
        self.trailer_no = QLineEdit(); vt_layout.addWidget(self.trailer_no, 4, 1)
        vt_layout.addWidget(QLabel("رقم القعدة/الشاسيه:"), 4, 2)
        self.trailer_chassis = QLineEdit(); vt_layout.addWidget(self.trailer_chassis, 4, 3)
        vt_layout.addWidget(QLabel("الحمولة (طن):"), 4, 4)
        self.payload = QLineEdit(); vt_layout.addWidget(self.payload, 4, 5)

        vt_layout.addWidget(QLabel("منطقة التحميل:"), 5, 0)
        self.load_port = QCheckBox("الميناء"); vt_layout.addWidget(self.load_port, 5, 1)
        self.load_yards = QCheckBox("أحواض/مخازن"); vt_layout.addWidget(self.load_yards, 5, 2)
        self.load_factory = QCheckBox("مصانع وشركات"); vt_layout.addWidget(self.load_factory, 5, 3)

        vt_group.setLayout(vt_layout)
        main_layout.addWidget(vt_group)

        # Driver & Owner
        do_group = QGroupBox("بيانات السائق والمالك")
        do_layout = QGridLayout()

        # driver
        do_layout.addWidget(QLabel("اسم السائق:"), 0, 0)
        self.driver_name = QLineEdit(); do_layout.addWidget(self.driver_name, 0, 1)
        do_layout.addWidget(QLabel("الهوية:"), 0, 2)
        self.driver_id = QLineEdit(); do_layout.addWidget(self.driver_id, 0, 3)
        do_layout.addWidget(QLabel("رقم السائق :"), 1, 0)
        self.driver_phone = QLineEdit(); do_layout.addWidget(self.driver_phone, 1, 1)
        do_layout.addWidget(QLabel("واتساب:"), 1, 2)
        self.driver_whatsapp = QLineEdit(); do_layout.addWidget(self.driver_whatsapp, 1, 3)
        do_layout.addWidget(QLabel("رخصة القيادة - رقم:"), 2, 0)
        self.license_no = QLineEdit(); do_layout.addWidget(self.license_no, 2, 1)
        do_layout.addWidget(QLabel("تاريخ إصدارها:"), 2, 2)
        self.license_date = QLineEdit(); do_layout.addWidget(self.license_date, 2, 3)
        do_layout.addWidget(QLabel("مكان اصدارها:"), 2, 4)
        self.license_place = QLineEdit(); do_layout.addWidget(self.license_place, 2, 5)

        # owner
        do_layout.addWidget(QLabel("اسم المالك:"), 3, 0)
        self.owner_name = QLineEdit(); do_layout.addWidget(self.owner_name, 3, 1)
        do_layout.addWidget(QLabel("هوية المالك:"), 3, 2)
        self.owner_id = QLineEdit(); do_layout.addWidget(self.owner_id, 3, 3)
        do_layout.addWidget(QLabel("هاتف المالك:"), 3, 4)
        self.owner_phone = QLineEdit(); do_layout.addWidget(self.owner_phone, 3, 5)
        do_layout.addWidget(QLabel("واتساب المالك:"), 4, 0)
        self.owner_whatsapp = QLineEdit(); do_layout.addWidget(self.owner_whatsapp, 4, 1)

        do_group.setLayout(do_layout)
        main_layout.addWidget(do_group)
        
        # Group: Additional Images
        images_group = QGroupBox("الصور الإضافية")
        images_layout = QGridLayout()
        
        self.image_buttons = []      
        image_labels = [
            "صورة 1",
            "صورة 2 ",
            "صورة 3 ",
            " صورة 4 ",
            "صوره 5" ,
        ]
        
        for i, label in enumerate(image_labels):
            images_layout.addWidget(QLabel(f"{label}:"), i, 0)
            btn = QPushButton(f"تحميل {label}")
            btn.clicked.connect(lambda checked, idx=i: self.upload_additional_image(idx))
            images_layout.addWidget(btn, i, 1)
            self.image_buttons.append(btn)
            
        images_group.setLayout(images_layout)
        main_layout.addWidget(images_group)
    
        bottom_h = QHBoxLayout()
        self.member_id_edit = QLineEdit(); self.member_id_edit.setPlaceholderText("رقم العضوية")
        bottom_h.addWidget(QLabel("رقم العضوية:")); bottom_h.addWidget(self.member_id_edit)
        self.upload_btn = QPushButton("تحميل البطاقة الشخصية")
        self.upload_btn.clicked.connect(self.upload_idcard)
        # bottom_h.addWidget(self.upload_btn)

        self.save_btn = QPushButton("حفظ وتصدير PDF")
        self.save_btn.clicked.connect(self.on_save)
        bottom_h.addWidget(self.save_btn)

        self.search_btn = QPushButton("بحث برقم العضوية")
        self.search_btn.clicked.connect(self.on_search)
        bottom_h.addWidget(self.search_btn)

        main_layout.addLayout(bottom_h)
        self.setLayout(main_layout)

        self.m  = QPushButton("كشف المنتسبين")
        self.m.clicked.connect(self.mm)
        self.m.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        bottom_h.addWidget(self.m)
    def mm(self):
        self.members_list_dialog = MembersListDialog()
        self.members_list_dialog.exec_()

    def upload_idcard(self):
        path, _ = QFileDialog.getOpenFileName(self, "اختر صورة البطاقة الشخصية", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            member_id = self.member_id_edit.text().strip() or "temp"
            file_ext = os.path.splitext(path)[1]
            dest_filename = f"idcard_{member_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
            dest = os.path.join(STORAGE_DIR, dest_filename)
            
            shutil.copy(path, dest)
            self.idcard_path = dest
            QMessageBox.information(self, "تم", f"تم رفع صورة البطاقة وحفظها محلياً: {dest_filename}")

    def upload_additional_image(self, index):
        path, _ = QFileDialog.getOpenFileName(self, f"اختر {[' تحميل صوره  ', '  تحميل صورة  ', ' تحميل صورة   ', 'تحميل صوره ','تحميل صورة'][index]}", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            member_id = self.member_id_edit.text().strip() or "temp"
            file_ext = os.path.splitext(path)[1]
            dest_filename = f"image_{index}_{member_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
            dest = os.path.join(STORAGE_DIR, dest_filename)
            
            shutil.copy(path, dest)
            self.additional_images[index] = dest
            QMessageBox.information(self, "تم", f"تم رفع الصورة {index+1} وحفظها محلياً: {dest_filename}")

    def collect_data(self):
        return {
            # office
            'office_manager': self.manager_name.text(),
            'manager_legal_status': self.manager_status.text(),
            'manager_id_type': self.id_type.text(),
            'manager_id_number': self.id_number.text(),
            'manager_id_issue_date': self.id_issue.text(),
            'office_name': self.office_name.text(),
            'office_legal_form': self.office_legal.text(),
            'office_branches': self.office_branches.text(),
            'office_location': self.office_place.text(),
            'office_landline': self.phone_fixed.text(),
            'office_mobile': self.phone_mobile.text(),
            'office_whatsapp': self.phone_whatsapp.text(),
            'affiliated_vehicles': self.num_movements.text(),
            # checkboxes
            'transport_heavy': str(self.chq_heavy.isChecked()),
            'transport_medium': str(self.chq_med.isChecked()),
            'transport_light': str(self.chq_light.isChecked()),
            'scope_domestic': str(self.ch_in.isChecked()),
            'scope_international': str(self.ch_out.isChecked()),
            'activity_freight': str(self.act_1.isChecked()),
            'activity_freight_load': str(self.act_2.isChecked()),
            # truck
            'vehicle_manufacturer': self.truck_maker.text(),
            'vehicle_plate': self.truck_plate.text(),
            'vehicle_color': self.truck_color.text(),
            'vehicle_manufacture_date': self.truck_year.text(),
            'vehicle_chassis': self.truck_chassis.text(),
            'vehicle_axles': self.truck_axles.text(),
            'vehicle_card_number': self.truck_card.text(),
            'vehicle_issuing_authority': self.truck_card_issuer.text(),
            'vehicle_plate2': self.truck_plate.text(),
            'vehicle_type_light': str(self.truck_type_light.isChecked()),
            'vehicle_type_medium': str(self.truck_type_med.isChecked()),
            'vehicle_type_heavy': str(self.truck_type_heavy.isChecked()),
            # trailer
            'trailer_number': self.trailer_no.text(),
            'trailer_chassis': self.trailer_chassis.text(),
            'payload': self.payload.text(),
            'trailer_mina': str(self.load_port.isChecked()),
            'trailer_warehouses': str(self.load_yards.isChecked()),
            'trailer_factories': str(self.load_factory.isChecked()),
            # driver & owner
            'driver_name': self.driver_name.text(),
            'driver_id': self.driver_id.text(),
            'driver_phone': self.driver_phone.text(),
            'driver_mobile': self.driver_phone.text(),  
            'driver_whatsapp': self.driver_whatsapp.text(),
            'driver_license_number': self.license_no.text(),
            'driver_license_issue_date': self.license_date.text(),
            'driver_license_issue_place': self.license_place.text(),
            'owner_name': self.owner_name.text(),
            'owner_id': self.owner_id.text(),
            'owner_mobile': self.owner_phone.text(),
            'owner_whatsapp': self.owner_whatsapp.text(),
            'contract_date': self.date_edit.date().toString("dd/MM/yyyy"),
        }

    def on_save(self):
        member_id = self.member_id_edit.text().strip()
        if not member_id:
            QMessageBox.warning(self, "مطلوب", "أدخل رقم العضوية أولاً لحفظ السجل.")
            return

        data = self.collect_data()

        pdf_path = os.path.join(STORAGE_DIR, f"form_{member_id}.pdf")

        try:
            generate_pdf(data, pdf_path, self.idcard_path, self.additional_images)
        except Exception as e:
            QMessageBox.critical(self, "خطأ PDF", str(e))
            return
    
        name_for_db = data.get('office_manager') or data.get('owner_name') or ''
        save_record(member_id, name_for_db, pdf_path, self.idcard_path, data)

        QMessageBox.information(self, "تم", f"تم الحفظ! رقم العضوية: {member_id}")

    def on_search(self):
        member_id = self.member_id_edit.text().strip()
        if not member_id:
            QMessageBox.warning(self, "مطلوب", "ادخل رقم العضوية للبحث.")
            return
        
        row = load_record(member_id)
        if not row:
            QMessageBox.information(self, "غير موجود", "لا يوجد سجل لهذا الرقم.")
            return

        data_string = row[6]
        data_dict = {}
        try:
            data_dict = json.loads(data_string)
        except json.JSONDecodeError:
            try:
                data_dict = ast.literal_eval(data_string)
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل تحميل بيانات السجل:\n{str(e)}")
                return

        # تعبئة الحقول (نفس الكود السابق)
        self.manager_name.setText(data_dict.get('office_manager', ''))
        self.manager_status.setText(data_dict.get('manager_legal_status', ''))
        self.id_type.setText(data_dict.get('manager_id_type', ''))
        self.id_number.setText(data_dict.get('manager_id_number', ''))
        self.id_issue.setText(data_dict.get('manager_id_issue_date', ''))
        self.office_name.setText(data_dict.get('office_name', ''))
        self.office_legal.setText(data_dict.get('office_legal_form', ''))
        self.office_branches.setText(data_dict.get('office_branches', ''))
        self.office_place.setText(data_dict.get('office_location', ''))
        self.phone_fixed.setText(data_dict.get('office_landline', ''))
        self.phone_mobile.setText(data_dict.get('office_mobile', ''))
        self.phone_whatsapp.setText(data_dict.get('office_whatsapp', ''))
        self.num_movements.setText(data_dict.get('affiliated_vehicles', ''))

        self.chq_heavy.setChecked(data_dict.get('transport_heavy') == 'True')
        self.chq_med.setChecked(data_dict.get('transport_medium') == 'True')
        self.chq_light.setChecked(data_dict.get('transport_light') == 'True')
        self.ch_in.setChecked(data_dict.get('scope_domestic') == 'True')
        self.ch_out.setChecked(data_dict.get('scope_international') == 'True')
        self.act_1.setChecked(data_dict.get('activity_freight') == 'True')
        self.act_2.setChecked(data_dict.get('activity_freight_load') == 'True')

        self.truck_maker.setText(data_dict.get('vehicle_manufacturer', ''))
        self.truck_plate.setText(data_dict.get('vehicle_plate', ''))
        self.truck_color.setText(data_dict.get('vehicle_color', ''))
        self.truck_year.setText(data_dict.get('vehicle_manufacture_date', ''))
        self.truck_chassis.setText(data_dict.get('vehicle_chassis', ''))
        self.truck_axles.setText(data_dict.get('vehicle_axles', ''))
        self.truck_card.setText(data_dict.get('vehicle_card_number', ''))
        self.truck_card_issuer.setText(data_dict.get('vehicle_issuing_authority', ''))
        self.trailer_no.setText(data_dict.get('trailer_number', ''))
        self.trailer_chassis.setText(data_dict.get('trailer_chassis', ''))
        self.payload.setText(data_dict.get('payload', ''))

        self.load_port.setChecked(data_dict.get('trailer_mina') == 'True')
        self.load_yards.setChecked(data_dict.get('trailer_warehouses') == 'True')
        self.load_factory.setChecked(data_dict.get('trailer_factories') == 'True')

        self.truck_type_light.setChecked(data_dict.get('vehicle_type_light') == 'True')
        self.truck_type_med.setChecked(data_dict.get('vehicle_type_medium') == 'True')
        self.truck_type_heavy.setChecked(data_dict.get('vehicle_type_heavy') == 'True')

        self.driver_name.setText(data_dict.get('driver_name', ''))
        self.driver_id.setText(data_dict.get('driver_id', ''))
        self.driver_phone.setText(data_dict.get('driver_phone', ''))
        self.driver_whatsapp.setText(data_dict.get('driver_whatsapp', ''))
        self.license_no.setText(data_dict.get('driver_license_number', ''))
        self.license_date.setText(data_dict.get('driver_license_issue_date', ''))
        self.license_place.setText(data_dict.get('driver_license_issue_place', ''))
        self.owner_name.setText(data_dict.get('owner_name', ''))
        self.owner_id.setText(data_dict.get('owner_id', ''))
        self.owner_phone.setText(data_dict.get('owner_mobile', ''))
        self.owner_whatsapp.setText(data_dict.get('owner_whatsapp', ''))

        date_str = data_dict.get('contract_date')
        if date_str:
            try:
                date = QDate.fromString(date_str, "dd/MM/yyyy")
                self.date_edit.setDate(date)
            except:
                pass

        pdf_path = row[4]
        idcard_path = row[5]
        self.idcard_path = idcard_path 

        if pdf_path and os.path.exists(pdf_path):
            os.startfile(pdf_path)

        QMessageBox.information(self, "تم", f"تم تحميل سجل العضوية: {member_id}\nالاسم: {row[2]}")



class MembersListDialog(QDialog):

    """عرض كشف المنتسبين المسجلين في النظام"""
    def __init__(self):
       

        super().__init__()
        self.setWindowTitle("📋 كشف المنتسبين")
        self.setGeometry(200, 150, 1200, 600)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📋 كشف المنتسبين")
        title.setFont(QFont("Amiri", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # إنشاء الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "اسم السائق", "اسم المالك", "رقم القاطرة", "الشركة المصنعة",
            "رقم اللوحة", "رقم القعادة", "رقم الهاتف", "الموديل", "اللون"
        ])
        self.table.setFont(QFont("Amiri", 9))
        self.table.horizontalHeader().setFont(QFont("Amiri", 10, QFont.Bold))
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)

        # زر التحديث
        refresh_btn = QPushButton("🔄 تحديث القائمة")
        refresh_btn.setFont(QFont("Amiri", 12))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        refresh_btn.clicked.connect(self.load_members)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)
        self.load_members()

    def load_members(self):
        """تحميل بيانات المنتسبين من قاعدة البيانات"""
        import sqlite3, json

        db_path = "forms.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM forms ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            try:
                data = json.loads(row[0]) if row[0] else {}
            except:
                data = {}

            # جلب البيانات المطلوبة
            driver_name = data.get('driver_name', '')
            owner_name = data.get('owner_name', '')
            tractor_number = data.get('trailer_number', '')
            manufacturer = data.get('vehicle_manufacturer', '')
            plate_number = data.get('vehicle_plate', '')
            chassis = data.get('vehicle_chassis', '')
            phone = data.get('driver_phone', '')
            model = data.get('vehicle_manufacture_date', '')
            color = data.get('vehicle_color', '')

            values = [driver_name, owner_name, tractor_number, manufacturer,
                      plate_number, chassis, phone, model, color]

            for col, val in enumerate(values):
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, col, cell)
