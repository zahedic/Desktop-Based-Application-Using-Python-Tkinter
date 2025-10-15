from tkinter import *
from tkinter import messagebox
import sqlite3

# --- Database Setup ---
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()
conn.close()

# --- GUI Setup ---
root = Tk()
root.title("Login System - NVIT")
root.geometry("400x300")

Label(root, text="NVIT Login System", font=("Arial", 16, "bold")).pack(pady=10)

Label(root, text="Username").pack()
username_entry = Entry(root)
username_entry.pack(pady=5)

Label(root, text="Password").pack()
password_entry = Entry(root, show="*")
password_entry.pack(pady=5)

def register_user():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showerror("Error", "All fields are required")
    else:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User Registered Successfully!")

def login_user():
    username = username_entry.get()
    password = password_entry.get()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    conn.close()

    if row:
        messagebox.showinfo("Login", f"Welcome {username} to NVIT!")
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

Button(root, text="Login", width=10, command=login_user).pack(pady=10)
Button(root, text="Register", width=10, command=register_user).pack()

root.mainloop()
