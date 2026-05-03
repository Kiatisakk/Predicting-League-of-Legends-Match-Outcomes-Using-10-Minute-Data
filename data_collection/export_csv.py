import mysql.connector
import csv
import os

# ตั้งค่าการเชื่อมต่อฐานข้อมูล (ใช้ config เดิมของคุณเป๊ะๆ)
config = {
    'user': 'league_user',
    'password': 'mysql',
    'host': 'localhost',
    'port': 3306,
    'database': 'LeagueStats',
    'buffered': True,
    'auth_plugin': 'mysql_native_password'
}

def export_all_tables_to_csv():
    try:
        # 1. เชื่อมต่อฐานข้อมูล
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # 2. ดึงรายชื่อตารางทั้งหมดในฐานข้อมูล
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if not tables:
            print("ไม่พบตารางในฐานข้อมูลเลยครับ")
            return

        # 3. สร้างโฟลเดอร์สำหรับเก็บไฟล์ CSV (ถ้ายังไม่มี)
        export_dir = "League_CSV_Export"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        print(f"📁 สร้างโฟลเดอร์ '{export_dir}' สำหรับเก็บไฟล์เรียบร้อย\n")

        # 4. วนลูปดึงข้อมูลทีละตาราง
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            print(f"กำลังดึงข้อมูลตาราง: {table_name} ...")

            # ดึงข้อมูลทั้งหมดจากตาราง
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()

            # ดึงชื่อคอลัมน์ (Header)
            column_names = [i[0] for i in cursor.description]

            # กำหนด Path ของไฟล์ CSV
            csv_file_path = os.path.join(export_dir, f"{table_name}.csv")

            # 5. เขียนข้อมูลลงไฟล์ CSV
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(column_names)  # เขียน Header
                csv_writer.writerows(rows)         # เขียน Data ทั้งหมด

            print(f"✅ บันทึก {table_name}.csv สำเร็จ! (ได้ข้อมูลมา {len(rows)} แถว)")

        print(f"\n🎉 ดึงข้อมูลเสร็จสิ้น! ไฟล์ CSV ทั้งหมดรอคุณอยู่ในโฟลเดอร์ '{export_dir}' ครับ")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        # ปิดการเชื่อมต่อเสมอเพื่อไม่ให้เปลืองทรัพยากร
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    export_all_tables_to_csv()