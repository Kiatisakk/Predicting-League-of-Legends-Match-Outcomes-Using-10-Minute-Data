import os
import subprocess
import sys

def main():
    print("=== League of Legends 10-Min Dataset Setup ===")
    
    # 1. เช็คว่ามีไลบรารี kaggle หรือไม่ ถ้าไม่มีให้ติดตั้ง
    try:
        import kaggle
    except ImportError:
        print("ไม่พบไลบรารี 'kaggle' กำลังทำการติดตั้ง...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])
        print("ติดตั้งไลบรารี 'kaggle' สำเร็จ!")
        print("หมายเหตุ: กรุณารันสคริปต์นี้ใหม่อีกครั้งหลังจากติดตั้งเสร็จ")
        sys.exit(0)

    # 2. สร้างโฟลเดอร์ data ถ้ายังไม่มี
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"เตรียมโฟลเดอร์สำหรับเก็บข้อมูลที่: {data_dir}")

    # 3. ดาวน์โหลดและแตกไฟล์จาก Kaggle
    dataset_name = "kiatisakkk/cpe232-lol-10min-dataset"
    print(f"\nกำลังดาวน์โหลดข้อมูลจาก Kaggle Dataset: {dataset_name}...")
    print("(ต้องแน่ใจว่าคุณได้ตั้งค่าไฟล์ kaggle.json ไว้ที่ C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json แล้ว)\n")
    
    # รันคำสั่ง kaggle
    command = f'kaggle datasets download -d {dataset_name} -p "{data_dir}" --unzip'
    
    try:
        # ใช้ subprocess เพื่อให้เห็น output ระหว่างโหลด
        subprocess.check_call(command, shell=True)
        print("\n✅ ดาวน์โหลดและแตกไฟล์เสร็จสมบูรณ์! ข้อมูลอยู่ในโฟลเดอร์ 'data'")
    except subprocess.CalledProcessError:
        print("\n❌ เกิดข้อผิดพลาดในการดาวน์โหลด!")
        print("วิธีแก้ไข:")
        print("1. ไปที่ https://www.kaggle.com/settings")
        print("2. เลื่อนลงมาที่หัวข้อ API แล้วกด 'Create New Token'")
        print("3. นำไฟล์ kaggle.json ที่ได้ ไปวางไว้ที่โฟลเดอร์: C:\\Users\\ชื่อผู้ใช้ของคุณ\\.kaggle\\")
        print("4. ลองรันสคริปต์นี้ใหม่อีกครั้ง")

if __name__ == "__main__":
    main()
