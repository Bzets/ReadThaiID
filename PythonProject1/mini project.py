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


# โหลดข้อมูลผู้ใช้
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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


# --- ฟังก์ชันฝากเงิน พร้อมปุ่มคัดลอกเลขบัญชีและแนบสลิป ---
def deposit_money(username, balance_var):
    users = load_users()
    deposit_window = tk.Toplevel()
    deposit_window.title("ฝากเงิน")
    deposit_window.config(bg="#FFF5E1")
    center_window(deposit_window, 450, 300)

    tk.Label(deposit_window, text="โอนเงินเข้าบัญชีนี้:", font=("Arial", 12), bg="#FFF5E1").pack(pady=5)
    bank_info = "1508573444 ธนาคารกสิกร"
    bank_entry = tk.Entry(deposit_window, width=30, justify="center", font=("Arial", 12))
    bank_entry.pack(pady=5)
    bank_entry.insert(0, bank_info)
    bank_entry.config(state="readonly")

    def copy_account():
        deposit_window.clipboard_clear()
        deposit_window.clipboard_append(bank_entry.get())
        messagebox.showinfo("คัดลอกเรียบร้อย", "คัดลอกเลขบัญชีเรียบร้อยแล้ว!")

    tk.Button(deposit_window, text="คัดลอกเลขบัญชี", command=copy_account,
              bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=5)

    deposit_status_var = tk.StringVar()
    deposit_status_var.set("")
    tk.Label(deposit_window, textvariable=deposit_status_var, fg="red", bg="#FFF5E1", font=("Arial", 11)).pack(pady=5)

    tk.Label(deposit_window, text="จำนวนเงินที่ฝาก:", font=("Arial", 12), bg="#FFF5E1").pack()
    deposit_amount = tk.Entry(deposit_window, font=("Arial", 12))
    deposit_amount.pack(pady=5)

    slip_path_var = tk.StringVar()
    slip_path_var.set("ยังไม่ได้แนบสลิป")

    def attach_slip():
        file_path = filedialog.askopenfilename(
            title="เลือกสลิปโอนเงิน",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
        )
        if file_path:
            slip_path_var.set(f"แนบแล้ว: {os.path.basename(file_path)}")
            messagebox.showinfo("แนบสลิป", f"แนบสลิปเรียบร้อย: {os.path.basename(file_path)}")

    tk.Button(deposit_window, text="แนบสลิป", command=attach_slip,
              bg="#58D68D", fg="white", font=("Arial", 12)).pack(pady=5)

    tk.Label(deposit_window, textvariable=slip_path_var, font=("Arial", 10), bg="#FFF5E1").pack()

    def confirm_deposit():
        amount = deposit_amount.get()
        if not amount.isdigit() or int(amount) <= 0:
            deposit_status_var.set("⚠️ กรุณากรอกจำนวนเงินที่ถูกต้อง")
            return

        if slip_path_var.get() == "ยังไม่ได้แนบสลิป":
            deposit_status_var.set("⚠️ กรุณาแนบสลิปก่อนยืนยัน")
            return

        users[username]["balance"] += int(amount)
        save_users(users)
        balance_var.set(f"ยอดเงิน: {users[username]['balance']} บาท")
        deposit_status_var.set(f"✅ ฝากเงิน {amount} บาทเรียบร้อยแล้ว")
        deposit_window.after(1500, deposit_window.destroy)

    tk.Button(deposit_window, text="ยืนยันฝากเงิน", command=confirm_deposit,
              bg="#58D68D", fg="white", font=("Arial", 12)).pack(pady=10)


# --- ฟังก์ชันแสดงประวัติการสั่งซื้อ ---
def show_order_history(username):
    users = load_users()
    history = users.get(username, {}).get("order_history", [])

    history_window = tk.Toplevel()
    history_window.title("ประวัติการสั่งซื้อ")
    history_window.config(bg="#FFF5E1")
    center_window(history_window, 450, 600)

    tk.Label(history_window, text="📜 ประวัติการสั่งซื้อ", font=("Arial", 16, "bold"), bg="#FFF5E1").pack(pady=10)

    history_frame = tk.Frame(history_window, bg="#FFF5E1")
    history_frame.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(history_frame, bg="#FFF5E1")
    scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#FFF5E1")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if not history:
        tk.Label(scrollable_frame, text="คุณยังไม่มีประวัติการสั่งซื้อ", font=("Arial", 12), bg="#FFF5E1").pack(pady=20)
    else:
        for order in history:
            order_text = f"สินค้า: {order['product']} | ราคา: {order['price']} บาท\nวันที่: {order['timestamp']}"
            tk.Label(scrollable_frame, text=order_text, font=("Arial", 11), bg="#D4E6F1",
                     relief="groove", bd=2, justify="left", wraplength=400).pack(fill="x", padx=5, pady=5)

    tk.Button(history_window, text="ปิด", command=history_window.destroy,
              bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)


# --- ฟังก์ชันออกจากระบบ ---
def logout(window):
    window.destroy()
    login_window.deiconify()
    login_status_var.set("✅ ออกจากระบบสำเร็จแล้ว")


# --- หน้าร้านค้า (แบบใหม่) ---
def open_shop(username):
    users = load_users()
    shop_window = tk.Toplevel()
    shop_window.title("ร้านขายเหล้าและเบียร์")
    shop_window.config(bg="#FFF5E1")
    center_window(shop_window, 650, 650)

    # --- UI ด้านบน ---
    top_frame = tk.Frame(shop_window, bg="#FFF5E1")
    top_frame.pack(side="top", fill="x", pady=10)

    # ปุ่มออกจากระบบและประวัติการสั่งซื้อ
    tk.Button(top_frame, text="ออกจากระบบ", width=12, command=lambda: logout(shop_window),
              bg="#E74C3C", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 0))
    tk.Button(top_frame, text="ประวัติการสั่งซื้อ", width=15, command=lambda: show_order_history(username),
              bg="#A569BD", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 0))

    tk.Label(top_frame, text=f"สวัสดี {username}", font=("Arial", 16, "bold"), bg="#FFF5E1").pack(side="left", padx=50,
                                                                                                  expand=True)

    balance_frame = tk.Frame(top_frame, bg="#FFF5E1")
    balance_frame.pack(side="right", padx=10)
    balance_var = tk.StringVar()
    balance_var.set(f"ยอดเงิน: {users.get(username, {}).get('balance', 0)} บาท")
    tk.Label(balance_frame, textvariable=balance_var, font=("Arial", 12, "bold"), fg="#2E86C1", bg="#FFF5E1").pack()
    tk.Button(balance_frame, text="💰 ฝากเงิน", width=12, command=lambda: deposit_money(username, balance_var),
              bg="#58D68D", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

    shop_status_var = tk.StringVar()
    shop_status_var.set("")
    tk.Label(shop_window, textvariable=shop_status_var, fg="red", bg="#FFF5E1", font=("Arial", 12, "bold")).pack(
        pady=(0, 10))

    # --- กรอบหลักสำหรับแถบข้างและพื้นที่แสดงสินค้า ---
    main_frame = tk.Frame(shop_window, bg="#FFF5E1")
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # --- แถบเมนูด้านข้าง ---
    sidebar_frame = tk.Frame(main_frame, width=150, bg="#EAF2F8", relief="raised", bd=2)
    sidebar_frame.pack(side="left", fill="y", padx=(0, 10))

    tk.Label(sidebar_frame, text="หมวดหมู่", font=("Arial", 14, "bold"), bg="#EAF2F8").pack(pady=10)

    # สร้างปุ่มสำหรับแต่ละหมวดหมู่
    tk.Button(sidebar_frame, text="ดูสินค้าทั้งหมด",
              command=lambda: show_products("all", product_display_frame, username, balance_var, shop_status_var),
              bg="#D6EAF8", fg="black", font=("Arial", 11)).pack(fill="x", padx=5, pady=2)

    tk.Button(sidebar_frame, text="เบียร์",
              command=lambda: show_products("เบียร์", product_display_frame, username, balance_var, shop_status_var),
              bg="#D6EAF8", fg="black", font=("Arial", 11)).pack(fill="x", padx=5, pady=2)

    tk.Button(sidebar_frame, text="เหล้า",
              command=lambda: show_products("เหล้า", product_display_frame, username, balance_var, shop_status_var),
              bg="#D6EAF8", fg="black", font=("Arial", 11)).pack(fill="x", padx=5, pady=2)

    tk.Button(sidebar_frame, text="มิกเซอร์",
              command=lambda: show_products("มิกเซอร์", product_display_frame, username, balance_var, shop_status_var),
              bg="#D6EAF8", fg="black", font=("Arial", 11)).pack(fill="x", padx=5, pady=2)

    # --- พื้นที่แสดงสินค้า ---
    product_display_frame = tk.Frame(main_frame, bg="#FFF5E1")
    product_display_frame.pack(side="left", fill="both", expand=True)

    def show_products(category, parent_frame, username, balance_var, shop_status_var):
        # ล้างสินค้าเก่า
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # สร้าง Canvas และ Scrollbar ใหม่
        canvas = tk.Canvas(parent_frame, bg="#FFF5E1")
        scrollbar = tk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF5E1")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # แสดงสินค้า
        if category == "all":
            products_to_show = PRODUCTS_BY_CATEGORY
        elif category == "เบียร์":
            products_to_show = {"เบียร์กระป๋อง": PRODUCTS_BY_CATEGORY["เบียร์กระป๋อง"],
                                "เบียร์ขวด": PRODUCTS_BY_CATEGORY["เบียร์ขวด"]}
        else:
            products_to_show = {category: PRODUCTS_BY_CATEGORY[category]}

        for cat, items in products_to_show.items():
            frame = tk.LabelFrame(scrollable_frame, text=f"🍶 {cat}", font=("Arial", 13, "bold"), bg="#FFF5E1", padx=10,
                                  pady=10)
            frame.pack(fill="both", expand=True, padx=10, pady=5)
            for name, price in items:
                tk.Button(frame, text=f"{name} - {price} บาท",
                          command=lambda n=name, p=price: buy_product(n, p, username, balance_var, shop_status_var),
                          width=40, bg="#AED6F1", fg="black", font=("Arial", 12)).pack(pady=2)

    # เมื่อเปิดหน้าต่าง จะแสดงสินค้าทั้งหมดก่อน
    show_products("all", product_display_frame, username, balance_var, shop_status_var)


# --- หน้าสมัครสมาชิก ---
def open_register_window():
    global reg_window, reg_username, reg_password, reg_age, reg_phone, reg_bank_number, reg_bank_name, reg_status_var
    reg_window = tk.Toplevel()
    reg_window.title("สมัครสมาชิก")
    reg_window.geometry("320x450")
    reg_window.config(bg="#FFF5E1")
    center_window(reg_window, 320, 450)

    reg_status_var = tk.StringVar()
    reg_status_var.set("")

    tk.Label(reg_window, text="สมัครสมาชิก", font=("Arial", 16, "bold"), bg="#FFF5E1").pack(pady=10)
    tk.Label(reg_window, text="ชื่อผู้ใช้", bg="#FFF5E1").pack()
    reg_username = tk.Entry(reg_window, font=("Arial", 12))
    reg_username.pack()
    tk.Label(reg_window, text="รหัสผ่าน (รหัสผ่าน 4 หลัก)", bg="#FFF5E1").pack()
    reg_password = tk.Entry(reg_window, show="*", font=("Arial", 12))
    reg_password.pack()
    tk.Label(reg_window, text="อายุ", bg="#FFF5E1").pack()
    reg_age = tk.Entry(reg_window, font=("Arial", 12))
    reg_age.pack()
    tk.Label(reg_window, text="เบอร์โทร", bg="#FFF5E1").pack()
    reg_phone = tk.Entry(reg_window, font=("Arial", 12))
    reg_phone.pack()
    tk.Label(reg_window, text="เลขบัญชี", bg="#FFF5E1").pack()
    reg_bank_number = tk.Entry(reg_window, font=("Arial", 12))
    reg_bank_number.pack()
    tk.Label(reg_window, text="ชื่อเจ้าของบัญชี", bg="#FFF5E1").pack()
    reg_bank_name = tk.Entry(reg_window, font=("Arial", 12))
    reg_bank_name.pack()
    tk.Button(reg_window, text="สมัครสมาชิก", command=register_user,
              bg="#58D68D", fg="white", font=("Arial", 12)).pack(pady=10)
    tk.Button(reg_window, text="ยกเลิก", command=reg_window.destroy,
              bg="#E74C3C", fg="white", font=("Arial", 12)).pack()
    tk.Label(reg_window, textvariable=reg_status_var, fg="red", bg="#FFF5E1", font=("Arial", 11)).pack(pady=10)


# --- หน้าล็อกอิน ---
login_window = tk.Tk()
login_window.title("ระบบร้านขายเหล้าและเบียร์")
login_window.geometry("350x320")
login_window.config(bg="#FFF5E1")
center_window(login_window, 350, 320)

login_status_var = tk.StringVar()
login_status_var.set("")

tk.Label(login_window, text="เข้าสู่ระบบ", font=("Arial", 16, "bold"), bg="#FFF5E1").pack(pady=10)
tk.Label(login_window, text="ชื่อผู้ใช้", bg="#FFF5E1").pack(pady=5)
login_username = tk.Entry(login_window, font=("Arial", 12))
login_username.pack()
tk.Label(login_window, text="รหัสผ่าน (รหัสผ่าน 4 หลัก)", bg="#FFF5E1").pack(pady=5)
login_password = tk.Entry(login_window, show="*", font=("Arial", 12))
login_password.pack()
tk.Button(login_window, text="เข้าสู่ระบบ", command=login_user,
          bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(login_window, text="สมัครสมาชิก", command=open_register_window,
          bg="#58D68D", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Label(login_window, textvariable=login_status_var, fg="green", bg="#FFF5E1", font=("Arial", 11)).pack(pady=10)

login_window.mainloop()