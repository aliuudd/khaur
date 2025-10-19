

import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="orders.db"):
        self.db_path = db_path
        self.init_database()

    
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()



        # جدول الطلبات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_name TEXT,
                tractor_number TEXT,
                quantity TEXT,
                arrival_area TEXT,
                cargo_type TEXT,
                arrival_date TEXT,
                truck_type TEXT,
                serial_number TEXT,
                receipt_confirmation TEXT,
                visa_datetime TEXT,
                created_datetime TEXT,
                merchant_name TEXT,
                seat_number TEXT,
                model TEXT,
                card_number TEXT,
                vehicle_type TEXT,
                owner_name TEXT,
                national_id TEXT,
                driver_national_id TEXT,
                phone TEXT,
                license TEXT,
                license_number TEXT,
                id_card_image TEXT,
                card_image TEXT,
                license_image TEXT,
                nahma_number TEXT,
                merchant_number TEXT,
                extra_data TEXT,
                notes TEXT,
                intsap  TEXT ,
                stop  TEXT,
                office  TEXT  , 
                color TEXT,
                is_transferred BOOLEAN DEFAULT 0,
                is_completed INTEGER DEFAULT 0
            )
        ''')
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN is_completed INTEGER DEFAULT 0;")
        except sqlite3.OperationalError:
            # إذا العمود موجود أصلاً، نتجاهل الخطأ
            pass

     
        # جدول الطلبات المؤكدة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confirmed_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                driver_name TEXT,
                tractor_number TEXT,
                quantity TEXT,
                arrival_area TEXT,
                cargo_type TEXT,
                arrival_date TEXT,
                truck_type TEXT,
                serial_number TEXT,
                receipt_confirmation TEXT,
                visa_datetime TEXT,
                created_datetime TEXT,
                merchant_name TEXT,
                seat_number TEXT,
                model TEXT,
                card_number TEXT,
                vehicle_type TEXT,
                owner_name TEXT,
                national_id TEXT,
                driver_national_id TEXT,
                phone TEXT,
                license TEXT,
                license_number TEXT,
                id_card_image TEXT,
                card_image TEXT,
                license_image TEXT,
                nahma_number TEXT,
                merchant_number TEXT,
                extra_data TEXT,
                notes TEXT,
                intsap  TEXT ,
                stop  TEXT,
                office  TEXT  , 
                color TEXT,
                confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def add_order(self, data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (
                    driver_name, tractor_number, quantity, arrival_area, cargo_type,
                    arrival_date, truck_type, serial_number, receipt_confirmation,
                    visa_datetime, created_datetime, merchant_name, seat_number,
                    model, card_number, vehicle_type, owner_name, national_id,
                    driver_national_id, phone, license, license_number,
                    id_card_image, card_image, license_image, nahma_number,
                    merchant_number, extra_data, notes, intsap, stop, office  , color
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?)
            ''', data)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding order: {e}")
            return False

    def get_all_orders(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY created_datetime ASC')
        orders = cursor.fetchall()
        conn.close()
        return orders

    def get_order_by_id(self, order_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        conn.close()
        return order

    def delete_order(self, order_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False

    def transfer_to_main_database(self, order_data):
        """نقل الطلب إلى جدول الطلبات المؤكدة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # بيانات للتخزين
            confirmed_data = order_data[:34]  # أول 30 عمود بدون is_transferred

            cursor.execute('''
                INSERT INTO confirmed_orders (
                    order_id, driver_name, tractor_number, quantity, arrival_area,
                    cargo_type, arrival_date, truck_type, serial_number,
                    receipt_confirmation, visa_datetime, created_datetime,
                    merchant_name, seat_number, model, card_number, vehicle_type,
                    owner_name, national_id, driver_national_id, phone, license,
                    license_number, id_card_image, card_image, license_image,
                    nahma_number, merchant_number, extra_data, notes , intsap, stop, office  , color
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?,?,?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', confirmed_data)

            # تحديث حالة الترحيل
            cursor.execute('UPDATE orders SET is_transferred = 1 WHERE id = ?', (order_data[0],))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error transferring order: {e}")
            return False
    def search_orders(self, search_text):
        """الببحث في الطلبات حسب اسم السائق أو رقم القاطرة أو الرقم المسلسل"""
        query = """
        SELECT * FROM orders 
        WHERE driver_name LIKE ? OR tractor_number LIKE ? OR serial_number LIKE ?
        """
        search_pattern = f'%{search_text}%'
        return self.fetch_all(query, (search_pattern, search_pattern, search_pattern))
   
    def fetch_all(self, query, params=()):
        """تنفيذ استعلام SELECT وإرجاع جميع النتائج"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def get_transferred_orders(self):
        """إرجاع مجموعة معرفات الطلبات المُرحلة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM orders WHERE is_transferred = 1')
        transferred_orders = cursor.fetchall()
        conn.close()
        return {order[0] for order in transferred_orders}
    
    def mark_as_completed(self, order_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET is_completed = 1 WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

    def update_order(self, order_id, data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orders SET
                    driver_name = ?, tractor_number = ?, quantity = ?, arrival_area = ?,
                    cargo_type = ?, arrival_date = ?, truck_type = ?, serial_number = ?,
                    receipt_confirmation = ?, visa_datetime = ?, created_datetime = ?, merchant_name = ?,
                    seat_number = ?, model = ?, card_number = ?, vehicle_type = ?,
                    owner_name = ?, national_id = ?, driver_national_id = ?, phone = ?,
                    license = ?, license_number = ?, id_card_image = ?, card_image = ?, license_image = ?,
                    nahma_number = ?, merchant_number = ?, extra_data = ?, notes = ? , intsap = ? , stop = ? , office = ? , color = ?
                WHERE id = ?
            ''', (*data, order_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating order: {e}")
            return False
