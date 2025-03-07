import tkinter as tk
from tkinter import simpledialog, END, messagebox
import random
import json
import os
import pyperclip
from cryptography.fernet import Fernet

# 🔒 קבצים חשובים
KEY_FILE = "key.key"
DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

# 🔑 סיסמת אבטחה ברירת מחדל (ניתן לשנות בקובץ config.json)
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def load_config():
    """ טוען את קובץ ההגדרות או יוצר חדש אם לא קיים """
    if not os.path.exists(CONFIG_FILE):
        config = {"admin_password": DEFAULT_ADMIN_PASSWORD}
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(config, config_file, indent=4)
    else:
        with open(CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
    return config

def load_key():
    """ טוען מפתח הצפנה או יוצר חדש אם לא קיים """
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

# 🔑 טעינת מפתח הצפנה וסיסמת מנהל
KEY = load_key()
cipher = Fernet(KEY)
config = load_config()
ADMIN_PASSWORD = config["admin_password"]

def encrypt_password(password):
    """ מצפין סיסמה """
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """ מפענח סיסמה מוצפנת """
    return cipher.decrypt(encrypted_password.encode()).decode()

def authenticate():
    """ פונקציה שמבקשת סיסמת מנהל כדי להציג סיסמאות """
    user_input = simpledialog.askstring("🔒 Authentication", "Enter admin password:", show="*")
    return user_input == ADMIN_PASSWORD

def generate_password():
    """ מחולל סיסמה חזקה """
    password_entry.delete(0, END)
    symbols = "!@#$%^&*()?"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"

    password = "".join(random.choices(symbols, k=2)) + \
               "".join(random.choices(letters, k=4)) + \
               "".join(random.choices(numbers, k=4))

    password = ''.join(random.sample(password, len(password)))  # ערבוב התווים
    messagebox.showinfo(title="New Password", message=f"Password: {password}")
    password_entry.insert(0, password)
    pyperclip.copy(password)  # שמירה בלוח ההעתקה

def search():
    """ חיפוש פרטי אתר במסד הנתונים עם אימות מנהל """
    website = website_entry.get().strip()

    if not website:
        messagebox.showinfo("Error", "Please enter a website to search")
        return

    # 📌 אימות סיסמה לפני הצגת הסיסמה
    if not authenticate():
        messagebox.showerror("Access Denied", "Incorrect admin password!")
        return

    try:
        with open(DATA_FILE, "r") as data_file:
            data = json.load(data_file)
            if website in data:
                email = data[website]["email"]
                password = decrypt_password(data[website]["password"])
                messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
                pyperclip.copy(password)  # העתקה ללוח
            else:
                messagebox.showinfo(title=website, message="No details found for this website")
    except FileNotFoundError:
        messagebox.showinfo("Error", "Data file not found!")

def save():
    """ שמירת פרטי גישה למסד הנתונים """
    website = website_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not website or not email or not password:
        messagebox.showinfo("Oops", "Please don't leave any fields empty!")
        return

    new_data = {
        website: {
            "email": email,
            "password": encrypt_password(password),
        }
    }

    try:
        with open(DATA_FILE, "r") as data_file:
            data = json.load(data_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data.update(new_data)

    with open(DATA_FILE, "w") as data_file:
        json.dump(data, data_file, indent=4)

    messagebox.showinfo("Success", "Details saved successfully!")

    website_entry.delete(0, END)
    email_entry.delete(0, END)
    password_entry.delete(0, END)

# 🎨 עיצוב הממשק הגרפי
window = tk.Tk()
window.title("🔒 Password Manager")
window.config(padx=50, pady=50)

# 🖼️ לוגו
canvas = tk.Canvas(width=200, height=200)
lock_photo = tk.PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=lock_photo)
canvas.grid(column=1, row=0)

# 🌐 אתר
website_label = tk.Label(text="Website:")
website_label.grid(column=0, row=1)
website_entry = tk.Entry(width=35)
website_entry.grid(column=1, row=1, columnspan=1)
search_button = tk.Button(text="🔍 Search", width=13, command=search)
search_button.grid(column=2, row=1)

# 📧 אימייל
email_label = tk.Label(text="Email:")
email_label.grid(column=0, row=2)
email_entry = tk.Entry(width=35)
email_entry.grid(column=1, row=2, columnspan=1)

# 🔑 סיסמה
password_label = tk.Label(text="Password:")
password_label.grid(column=0, row=3)
password_entry = tk.Entry(width=35, show="*")
password_entry.grid(column=1, row=3, columnspan=1)
generate_button = tk.Button(text="🔑 Generate", width=15, command=generate_password)
generate_button.grid(column=2, row=3)

# 💾 כפתור שמירה
add_button = tk.Button(text="💾 Save", width=30, command=save)
add_button.grid(column=1, row=4, columnspan=2)

window.mainloop()
