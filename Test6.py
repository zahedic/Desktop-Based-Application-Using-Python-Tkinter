import sqlite3
from tkinter import *
from tkinter import messagebox

# ========== Database Setup ==========
conn = sqlite3.connect("nvit.db")
cursor = conn.cursor()

# Create users table
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')

# Create relational tables
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    gender TEXT,
    phone TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    duration TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS instructors (
    instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    subject TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    grade TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id)
)''')

conn.commit()

# ========== Registration Window ==========
def register_user():
    name = reg_name.get()
    email = reg_email.get()
    password = reg_pass.get()
    confirm = reg_confirm.get()

    if name == "" or email == "" or password == "" or confirm == "":
        messagebox.showwarning("Error", "All fields are required!")
        return
    if password != confirm:
        messagebox.showerror("Error", "Passwords do not match!")
        return

    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration Successful!")
        reg_name.delete(0, END)
        reg_email.delete(0, END)
        reg_pass.delete(0, END)
        reg_confirm.delete(0, END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already registered!")

# ========== Login System ==========
def login_user():
    email = login_email.get()
    password = login_pass.get()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Welcome", f"Login Successful! Welcome {user[1]}")
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid Email or Password!")

# ========== Dashboard ==========
def open_dashboard():
    dash = Tk()
    dash.title("NVIT Management System")
    dash.geometry("700x500")
    dash.config(bg="#eef8fc")

    Label(dash, text="🎓 NVIT Management System", font=("Arial", 20, "bold"), bg="#eef8fc", fg="#003366").pack(pady=15)

    def add_student():
        name = entry_name.get()
        email = entry_email.get()
        gender = entry_gender.get()
        phone = entry_phone.get()
        if name == "" or email == "":
            messagebox.showwarning("Warning", "Please fill all fields!")
            return
        cursor.execute("INSERT INTO students (name, email, gender, phone) VALUES (?, ?, ?, ?)",
                       (name, email, gender, phone))
        conn.commit()
        messagebox.showinfo("Success", "Student Added Successfully!")

    # ---- Student Section ----
    frame = Frame(dash, bg="#eef8fc")
    frame.pack(pady=10)

    Label(frame, text="Student Name:", bg="#eef8fc").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    Label(frame, text="Email:", bg="#eef8fc").grid(row=1, column=0, padx=10, pady=5, sticky=E)
    Label(frame, text="Gender:", bg="#eef8fc").grid(row=2, column=0, padx=10, pady=5, sticky=E)
    Label(frame, text="Phone:", bg="#eef8fc").grid(row=3, column=0, padx=10, pady=5, sticky=E)

    entry_name = Entry(frame, width=30)
    entry_email = Entry(frame, width=30)
    entry_gender = Entry(frame, width=30)
    entry_phone = Entry(frame, width=30)

    entry_name.grid(row=0, column=1, padx=10, pady=5)
    entry_email.grid(row=1, column=1, padx=10, pady=5)
    entry_gender.grid(row=2, column=1, padx=10, pady=5)
    entry_phone.grid(row=3, column=1, padx=10, pady=5)

    Button(frame, text="Add Student", bg="#0066cc", fg="white", width=20, command=add_student).grid(row=4, columnspan=2, pady=10)

    dash.mainloop()

# ========== Login Window ==========
login_window = Tk()
login_window.title("NVIT Login")
login_window.geometry("400x450")
login_window.config(bg="#f2f6fc")

Label(login_window, text="🔐 NVIT Login Panel", font=("Arial", 18, "bold"), bg="#f2f6fc", fg="#003366").pack(pady=15)

Label(login_window, text="Email:", bg="#f2f6fc").pack()
login_email = Entry(login_window, width=30)
login_email.pack(pady=5)

Label(login_window, text="Password:", bg="#f2f6fc").pack()
login_pass = Entry(login_window, width=30, show="*")
login_pass.pack(pady=5)

Button(login_window, text="Login", bg="#007acc", fg="white", width=20, command=login_user).pack(pady=10)

Label(login_window, text="OR Register Below", bg="#f2f6fc").pack(pady=10)

# ========== Registration Form ==========
Label(login_window, text="Name:", bg="#f2f6fc").pack()
reg_name = Entry(login_window, width=30)
reg_name.pack(pady=5)

Label(login_window, text="Email:", bg="#f2f6fc").pack()
reg_email = Entry(login_window, width=30)
reg_email.pack(pady=5)

Label(login_window, text="Password:", bg="#f2f6fc").pack()
reg_pass = Entry(login_window, width=30, show="*")
reg_pass.pack(pady=5)

Label(login_window, text="Confirm Password:", bg="#f2f6fc").pack()
reg_confirm = Entry(login_window, width=30, show="*")
reg_confirm.pack(pady=5)

Button(login_window, text="Register", bg="#009933", fg="white", width=20, command=register_user).pack(pady=10)

login_window.mainloop()
