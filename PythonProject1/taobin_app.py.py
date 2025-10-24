import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
from datetime import datetime

# --- Global Configurations ---
USER_FILE = "users.json"
PRODUCTS_BY_CATEGORY = {
    "กาแฟ": [
        ("กาแฟดำ", 30), ("เอสเปรสโซ่", 40), ("คาปูชิโน่", 45),
        ("ลาเต้", 45), ("มอคค่า", 50)
    ],
    "ชาและช็อกโกแลต": [
        ("ชาไทย", 35), ("ชาเขียว", 40), ("ช็อกโกแลตร้อน", 45),
        ("โกโก้", 40)
    ],
    "โซดาและน้ำผลไม้": [
        ("น้ำส้มโซดา", 35), ("น้ำมะนาวโซดา", 35), ("น้ำแอปเปิ้ล", 40),
        ("น้ำฝรั่ง", 40)
    ],
    "เมนูพิเศษ": [
        ("นมสดโอริโอ้", 50), ("นมชมพู", 40), ("นมคาราเมล", 45)
    ]
}


# --- Data Handling ---
def load_users():
    """Loads user data from a JSON file."""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    """Saves user data to a JSON file."""
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


# --- GUI Classes (Frames) ---

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        main_frame = ttk.Frame(self, padding="40")
        main_frame.pack(expand=True)

        ttk.Label(main_frame, text="เข้าสู่ระบบตู้เต่าบิน", font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(main_frame, text="ชื่อผู้ใช้").pack()
        self.username_entry = ttk.Entry(main_frame, font=("Arial", 12))
        self.username_entry.pack()

        ttk.Label(main_frame, text="รหัสผ่าน").pack(pady=5)
        self.password_entry = ttk.Entry(main_frame, show="*", font=("Arial", 12))
        self.password_entry.pack()

        ttk.Button(main_frame, text="เข้าสู่ระบบ", command=self.login_user).pack(pady=5)

        ttk.Button(main_frame, text="สมัครสมาชิก", command=lambda: controller.show_frame("RegisterPage")).pack(pady=5)

        self.status_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green", font=("Arial", 11)).pack(pady=10)

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        users = load_users()

        if username not in users:
            self.status_var.set("❌ ไม่มีผู้ใช้บัญชีนี้ กรุณาสมัครสมาชิก")
            return

        if users[username]["password"] == password:
            self.status_var.set("✅ เข้าสู่ระบบสำเร็จแล้ว")
            self.controller.current_user = username
            self.controller.after(500, lambda: self.controller.show_frame("ShopPage"))
        else:
            self.status_var.set("❌ รหัสผ่านไม่ถูกต้อง")


class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="20")
        self.controller = controller

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True)

        ttk.Label(main_frame, text="สมัครสมาชิก", font=("Arial", 16, "bold")).pack(pady=10)

        self.fields = {}
        labels = ["ชื่อผู้ใช้", "รหัสผ่าน (4 หลัก)", "เบอร์โทร", "เลขบัญชี", "ชื่อเจ้าของบัญชี"]
        for label_text in labels:
            ttk.Label(main_frame, text=label_text).pack()
            entry = ttk.Entry(main_frame, font=("Arial", 12))
            if "รหัสผ่าน" in label_text:
                entry.config(show="*")
            entry.pack(pady=2)
            self.fields[label_text] = entry

        ttk.Button(main_frame, text="สมัครสมาชิก", command=self.register_user).pack(pady=10)
        ttk.Button(main_frame, text="กลับ", command=lambda: controller.show_frame("LoginPage")).pack()

        self.status_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="red", font=("Arial", 11)).pack(pady=10)

    def register_user(self):
        username = self.fields["ชื่อผู้ใช้"].get().strip()
        password = self.fields["รหัสผ่าน (4 หลัก)"].get().strip()
        phone = self.fields["เบอร์โทร"].get().strip()
        bank_number = self.fields["เลขบัญชี"].get().strip()
        bank_name = self.fields["ชื่อเจ้าของบัญชี"].get().strip()

        if not all([username, password, phone, bank_number, bank_name]):
            self.status_var.set("⚠️ กรุณากรอกข้อมูลให้ครบ")
            return
        if len(password) != 4 or not password.isdigit():
            self.status_var.set("⚠️ รหัสผ่านต้องเป็นตัวเลข 4 หลัก")
            return
        if not (phone.isdigit() and len(phone) == 10):
            self.status_var.set("⚠️ เบอร์โทรต้องมี 10 หลัก")
            return
        if not (bank_number.isdigit() and len(bank_number) == 10):
            self.status_var.set("⚠️ เลขบัญชีไม่ถูกต้อง (ต้องมี 10 หลัก)")
            return

        users = load_users()
        if username in users:
            self.status_var.set("❌ มีชื่อผู้ใช้นี้อยู่แล้ว")
            return
        for user, data in users.items():
            if data.get("bank_number") == bank_number:
                self.status_var.set("❌ เลขบัญชีนี้ถูกใช้ไปแล้ว")
                return

        users[username] = {
            "password": password, "phone": phone,
            "bank_number": bank_number, "bank_name": bank_name,
            "balance": 0, "order_history": []
        }
        save_users(users)
        self.status_var.set("✅ สมัครสมาชิกเรียบร้อยแล้ว")
        self.controller.after(2000, lambda: self.controller.show_frame("LoginPage"))


class ShopPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(side="top", fill="x")

        ttk.Button(top_frame, text="ออกจากระบบ", command=self.logout).pack(side="left", padx=5)
        ttk.Button(top_frame, text="📜 ประวัติการสั่งซื้อ",
                   command=lambda: self.controller.show_frame("HistoryPage")).pack(side="left", padx=5)

        self.balance_var = tk.StringVar()
        self.balance_label = ttk.Label(top_frame, textvariable=self.balance_var, font=("Arial", 12, "bold"))
        self.balance_label.pack(side="right", padx=10)
        ttk.Button(top_frame, text="💰 เติมเงิน", command=lambda: self.controller.show_frame("DepositPage")).pack(
            side="right", padx=5)

        self.shop_status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.shop_status_var, foreground="red", font=("Arial", 12)).pack(pady=(0, 10))

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        sidebar_frame = ttk.Frame(main_frame, width=150)
        sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
        ttk.Label(sidebar_frame, text="หมวดหมู่", font=("Arial", 14, "bold")).pack(pady=10)

        categories = list(PRODUCTS_BY_CATEGORY.keys())
        for category in categories:
            ttk.Button(sidebar_frame, text=category, command=lambda c=category: self.show_products(c)).pack(fill="x",
                                                                                                            padx=5,
                                                                                                            pady=2)

        self.product_display_frame = ttk.Frame(main_frame)
        self.product_display_frame.pack(side="left", fill="both", expand=True)

        self.update_balance()
        self.show_products(categories[0])

    def update_balance(self):
        users = load_users()
        self.balance_var.set(f"ยอดเงิน: {users.get(self.controller.current_user, {}).get('balance', 0)} บาท")

    def logout(self):
        self.controller.current_user = None
        messagebox.showinfo("ออกจากระบบ", "คุณได้ออกจากระบบแล้ว")
        self.controller.show_frame("LoginPage")

    def show_products(self, category):
        for widget in self.product_display_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.product_display_frame)
        scrollbar = ttk.Scrollbar(self.product_display_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        items = PRODUCTS_BY_CATEGORY.get(category, [])
        for name, price in items:
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(item_frame, text=f"{name} - {price} บาท", font=("Arial", 12)).pack(side="left")
            ttk.Button(item_frame, text="ซื้อ", command=lambda n=name, p=price: self.buy_product(n, p)).pack(
                side="right")

    def buy_product(self, name, price):
        users = load_users()
        if users[self.controller.current_user]["balance"] < price:
            self.shop_status_var.set("⚠️ ยอดเงินไม่เพียงพอ กรุณาเติมเงิน")
            return

        response = messagebox.askyesno("ยืนยันการซื้อ", f"คุณต้องการซื้อ {name} ราคา {price} บาท หรือไม่?")
        if response:
            users[self.controller.current_user]["balance"] -= price
            order = {"product": name, "price": price, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            users[self.controller.current_user]["order_history"].append(order)
            save_users(users)
            self.update_balance()
            self.shop_status_var.set(f"✅ ซื้อ {name} เรียบร้อยแล้ว")
        else:
            self.shop_status_var.set(f"❌ ยกเลิกการซื้อ {name}")


class DepositPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="20")

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True)

        ttk.Label(main_frame, text="เติมเงิน", font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(main_frame, text="จำนวนเงินที่ต้องการเติม:").pack()
        self.deposit_amount = ttk.Entry(main_frame)
        self.deposit_amount.pack(pady=5)

        ttk.Button(main_frame, text="ยืนยันการเติมเงิน", command=self.confirm_deposit).pack(pady=10)
        ttk.Button(main_frame, text="กลับ", command=lambda: self.controller.show_frame("ShopPage")).pack()

        self.status_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green", font=("Arial", 11)).pack(pady=10)

    def confirm_deposit(self):
        amount_str = self.deposit_amount.get()
        if not amount_str.isdigit() or int(amount_str) <= 0:
            self.status_var.set("⚠️ กรุณากรอกจำนวนเงินที่ถูกต้อง")
            return

        amount = int(amount_str)

        users = load_users()
        users[self.controller.current_user]["balance"] += amount
        save_users(users)
        self.status_var.set(f"✅ เติมเงิน {amount} บาทเรียบร้อยแล้ว")
        self.controller.after(1500, lambda: self.controller.show_frame("ShopPage"))


class HistoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="20")

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True)

        ttk.Label(main_frame, text="📜 ประวัติการสั่งซื้อ", font=("Arial", 16, "bold")).pack(pady=10)

        self.history_text = tk.Text(main_frame, wrap="word", height=20, width=50)
        self.history_text.pack(pady=10)
        self.history_text.config(state=tk.DISABLED)  # Make it read-only

        ttk.Button(main_frame, text="กลับ", command=lambda: controller.show_frame("ShopPage")).pack(pady=10)

    def show_history(self):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)

        users = load_users()
        history = users.get(self.controller.current_user, {}).get("order_history", [])

        if not history:
            self.history_text.insert(tk.END, "คุณยังไม่มีประวัติการสั่งซื้อ")
        else:
            for i, order in enumerate(history):
                order_text = f"--- รายการที่ {i + 1} ---\n"
                order_text += f"สินค้า: {order['product']}\n"
                order_text += f"ราคา: {order['price']} บาท\n"
                order_text += f"วันที่: {order['timestamp']}\n\n"
                self.history_text.insert(tk.END, order_text)

        self.history_text.config(state=tk.DISABLED)


# --- Main Application ---
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ตู้เต่าบิน")
        self.geometry("600x600")
        self.current_user = None

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        for F in (LoginPage, RegisterPage, ShopPage, DepositPage, HistoryPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "ShopPage":
            frame.update_balance()
        elif page_name == "HistoryPage":
            frame.show_history()

    def get_user_data(self):
        users = load_users()
        return users.get(self.current_user, {})


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()