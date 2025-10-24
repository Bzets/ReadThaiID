import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import json
import os
from datetime import datetime

# ไฟล์เก็บข้อมูลสมาชิก
USER_FILE = "users.json"

# ข้อมูลสินค้าทั้งหมด
PRODUCTS_BY_CATEGORY = {
    "เบียร์กระป๋อง": [
        ("เบียร์สิงห์", 35), ("เบียร์ช้าง", 30), ("เบียร์ลีโอ", 28),
        ("เบียร์ไฮเนเก้น", 45), ("เบียร์คาร์ลสเบิร์ก", 40)
    ],
    "เบียร์ขวด": [
        ("สิงห์ขวด", 60), ("ช้างขวด", 60), ("ลีโอขวด", 60),
        ("ไฮเนเก้นขวด", 55), ("คาร์ลสเบิร์กขวด", 50)
    ],
    "เหล้า": [
        ("แสงโสม", 250), ("แม่โขง", 220), ("พลังแสง", 200), ("มังกรทอง", 180)
    ],
    "มิกเซอร์": [
        ("โซดา", 15), ("โทนิค", 20), ("น้ำผลไม้", 25)
    ]
}

# --- ฟังก์ชันช่วยจัดหน้าต่างให้อยู่กลาง ---
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# โหลดข้อมูลผู้ใช้ (แก้ไขให้ทุก user มี order_history เสมอ)
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
            # 🔹 ตรวจสอบให้ทุก user มี order_history
            for username, data in users.items():
                if "order_history" not in data:
                    users[username]["order_history"] = []
            return users
    return {}

# บันทึกข้อมูลผู้ใช้
def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- สมัครสมาชิก ---
def register_user():
    username = reg_username.get().strip()
    password = reg_password.get().strip()
    age = reg_age.get().strip()
    phone = reg_phone.get().strip()
    bank_number = reg_bank_number.get().strip()
    bank_name = reg_bank_name.get().strip()

    if not (username and password and age and phone and bank_number and bank_name):
        reg_status_var.set("⚠️ กรุณากรอกข้อมูลให้ครบ")
        return

    if len(password) != 4:
        reg_status_var.set("⚠️ รหัสผ่านต้องมี 4 ตัว")
        return

    if not age.isdigit():
        reg_status_var.set("⚠️ อายุต้องเป็นตัวเลข")
        return
    age = int(age)
    if age < 20:
        reg_status_var.set("❌ คุณต้องมีอายุ 20 ปีขึ้นไปจึงจะสมัครได้")
        return

    if not (phone.isdigit() and len(phone) == 10):
        reg_status_var.set("⚠️ เบอร์โทรต้องมี 10 ตัว")
        return

    if not (bank_number.isdigit() and len(bank_number) == 10):
        reg_status_var.set("⚠️ เลขบัญชีไม่ถูกต้อง (ต้องมี 10 หลัก)")
        return

    users = load_users()
    if username in users:
        reg_status_var.set("❌ มีชื่อผู้ใช้นี้อยู่แล้ว")
        return
    for user, data in users.items():
        if data["bank_number"] == bank_number:
            reg_status_var.set("❌ เลขบัญชีนี้ถูกใช้ไปแล้ว")
            return

    users[username] = {
        "password": password,
        "age": age,
        "phone": phone,
        "bank_number": bank_number,
        "bank_name": bank_name,
        "balance": 0,
        "order_history": []  # เพิ่มคีย์ order_history
    }
    save_users(users)
    reg_status_var.set("✅ สมัครสมาชิกเรียบร้อยแล้ว")
    reg_window.after(2000, reg_window.destroy)

# --- ล็อกอิน ---
def login_user():
    username = login_username.get().strip()
    password = login_password.get().strip()
    users = load_users()

    if username not in users:
        login_status_var.set("❌ ไม่มีผู้ใช้บัญชีนี้ กรุณาสมัครสมาชิก")
        return

    if users[username]["password"] == password:
        if users[username]["age"] < 20:
            login_status_var.set("❌ คุณต้องมีอายุ 20 ปีขึ้นไปจึงจะซื้อได้")
            return
        login_status_var.set("✅ เข้าสู่ระบบสำเร็จแล้ว")
        login_window.after(500, lambda: [login_window.withdraw(), open_shop(username)])
    else:
        login_status_var.set("❌ รหัสผ่านไม่ถูกต้อง")

# --- ฟังก์ชันซื้อสินค้าแบบ GUI ---
def buy_product(name, price, username, balance_var, shop_status_var):
    users = load_users()
    if users[username]["balance"] < price:
        shop_status_var.set("⚠️ เครดิตไม่เพียงพอ")
        return

    confirm_window = tk.Toplevel()
    confirm_window.title("ยืนยันการซื้อ")
    confirm_window.config(bg="#FFF5E1")
    center_window(confirm_window, 300, 150)

    tk.Label(confirm_window, text=f"คุณต้องการซื้อ\n{name}\nราคา {price} บาท หรือไม่?",
             bg="#FFF5E1", font=("Arial", 12), justify="center").pack(pady=10)

    def confirm():
        # บันทึกประวัติการสั่งซื้อ
        purchase_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order = {"product": name, "price": price, "timestamp": purchase_time}

        # ป้องกัน KeyError อีกชั้น
        if "order_history" not in users[username]:
            users[username]["order_history"] = []

        users[username]["order_history"].append(order)
        users[username]["balance"] -= price
        save_users(users)
        balance_var.set(f"ยอดเงิน: {users[username]['balance']} บาท")
        shop_status_var.set(f"✅ ซื้อ {name} เรียบร้อยแล้ว")
        confirm_window.destroy()

        success_window = tk.Toplevel()
        success_window.title("สั่งซื้อสำเร็จ")
        success_window.config(bg="#D4EFDF")
        center_window(success_window, 250, 100)
        tk.Label(success_window, text=f"คุณซื้อ {name} เรียบร้อยแล้ว!",
                 bg="#D4EFDF", font=("Arial", 12)).pack(pady=10)
        tk.Button(success_window, text="ปิด", command=success_window.destroy,
                  bg="#58D68D", fg="white", font=("Arial", 10)).pack(pady=5)

    def cancel():
        shop_status_var.set(f"❌ ยกเลิกการซื้อ {name}")
        confirm_window.destroy()

    tk.Button(confirm_window, text="ยืนยัน", command=confirm,
              bg="#58D68D", fg="white", font=("Arial", 12), width=10).pack(side="left", padx=20, pady=20)
    tk.Button(confirm_window, text="ยกเลิก", command=cancel,
              bg="#E74C3C", fg="white", font=("Arial", 12), width=10).pack(side="right", padx=20, pady=20)

# --- ฟังก์ชันฝากเงิน ---
# (คงเดิม)

# --- ฟังก์ชันแสดงประวัติการสั่งซื้อ ---
# (คงเดิม)

# --- ฟังก์ชันออกจากระบบ ---
# (คงเดิม)

# --- หน้าร้านค้า ---
# (คงเดิม)

# --- หน้าสมัครสมาชิก ---
# (คงเดิม)

# --- หน้าล็อกอิน ---
# (คงเดิม)
