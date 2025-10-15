import tkinter as tk
from tkinter import messagebox
import sqlite3

# ==========================
# Database Setup
# ==========================
conn = sqlite3.connect("nvit.db")
cursor = conn.cursor()

# Create tables if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Student_Information (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    course_id INTEGER,
    instructor_id INTEGER,
    FOREIGN KEY(course_id) REFERENCES Course(course_id),
    FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Course (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    duration TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Instructors (
    instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    expertise TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Result (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    grade TEXT,
    FOREIGN KEY(student_id) REFERENCES Student_Information(student_id),
    FOREIGN KEY(course_id) REFERENCES Course(course_id)
)
""")

conn.commit()
conn.close()


# ==========================
# Functions
# ==========================
def register_user():
    name = entry_name.get()
    email = entry_email.get()
    password = entry_password.get()

    if name == "" or email == "" or password == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    conn = sqlite3.connect("nvit.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
        reg_window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already exists!")
    finally:
        conn.close()


def login_user():
    email = login_email.get()
    password = login_password.get()

    conn = sqlite3.connect("nvit.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Success", f"Welcome {user[1]} to NVIT System!")
        open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid Email or Password!")


def open_register():
    global reg_window, entry_name, entry_email, entry_password
    reg_window = tk.Toplevel(root)
    reg_window.title("Register - NVIT")
    reg_window.geometry("350x300")

    tk.Label(reg_window, text="Full Name:", font=("Arial", 11)).pack(pady=5)
    entry_name = tk.Entry(reg_window, width=30)
    entry_name.pack()

    tk.Label(reg_window, text="Email:", font=("Arial", 11)).pack(pady=5)
    entry_email = tk.Entry(reg_window, width=30)
    entry_email.pack()

    tk.Label(reg_window, text="Password:", font=("Arial", 11)).pack(pady=5)
    entry_password = tk.Entry(reg_window, show="*", width=30)
    entry_password.pack()

    tk.Button(reg_window, text="Register", command=register_user, bg="#0078D7", fg="white").pack(pady=10)


def open_dashboard():
    dash = tk.Toplevel(root)
    dash.title("Dashboard - NVIT")
    dash.geometry("500x400")
    tk.Label(dash, text="Welcome to NVIT Student Management System",
             font=("Arial", 13, "bold")).pack(pady=20)

    tk.Label(dash, text="Available Tables:", font=("Arial", 11, "underline")).pack()
    tk.Label(dash, text="- Student_Information\n- Course\n- Instructors\n- Result",
             font=("Arial", 10)).pack(pady=10)


# ==========================
# Login Window GUI
# ==========================
root = tk.Tk()
root.title("NVIT Login System")
root.geometry("400x350")
root.config(bg="white")

tk.Label(root, text="NVIT", font=("Arial", 20, "bold"), fg="#0078D7", bg="white").pack(pady=10)
tk.Label(root, text="New Vision Information Technology Limited", font=("Arial", 10), bg="white").pack()

tk.Label(root, text="Email", font=("Arial", 11), bg="white").pack(pady=(30, 5))
login_email = tk.Entry(root, width=30)
login_email.pack()

tk.Label(root, text="Password", font=("Arial", 11), bg="white").pack(pady=5)
login_password = tk.Entry(root, show="*", width=30)
login_password.pack()

tk.Button(root, text="Login", command=login_user, bg="#0078D7", fg="white", width=15).pack(pady=20)
tk.Button(root, text="Create Account", command=open_register, fg="#0078D7", bg="white", bd=0).pack()

root.mainloop()
