import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ==========================
# Database Setup
# ==========================
conn = sqlite3.connect("nvit.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
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
# LOGIN / REGISTER SYSTEM
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


# ==========================
# DASHBOARD
# ==========================
def open_dashboard():
    dash = tk.Toplevel(root)
    dash.title("NVIT Dashboard")
    dash.geometry("500x400")
    dash.config(bg="white")

    tk.Label(dash, text="NVIT Management Dashboard",
             font=("Arial", 16, "bold"), fg="#0078D7", bg="white").pack(pady=20)

    tk.Button(dash, text="Manage Students", command=open_students, width=25, bg="#0078D7", fg="white").pack(pady=10)
    tk.Button(dash, text="Manage Courses", command=open_courses, width=25, bg="#0078D7", fg="white").pack(pady=10)
    tk.Button(dash, text="Manage Instructors", command=open_instructors, width=25, bg="#0078D7", fg="white").pack(pady=10)
    tk.Button(dash, text="Manage Results", command=open_results, width=25, bg="#0078D7", fg="white").pack(pady=10)


# ==========================
# STUDENT MANAGEMENT
# ==========================
def open_students():
    win = tk.Toplevel(root)
    win.title("Student Information")
    win.geometry("500x400")

    tk.Label(win, text="Student Name").pack()
    s_name = tk.Entry(win)
    s_name.pack()

    tk.Label(win, text="Course ID").pack()
    s_course = tk.Entry(win)
    s_course.pack()

    tk.Label(win, text="Instructor ID").pack()
    s_instructor = tk.Entry(win)
    s_instructor.pack()

    def add_student():
        conn = sqlite3.connect("nvit.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO Student_Information (name, course_id, instructor_id) VALUES (?, ?, ?)",
                    (s_name.get(), s_course.get(), s_instructor.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Student Added!")

    tk.Button(win, text="Add Student", command=add_student, bg="#0078D7", fg="white").pack(pady=10)


# ==========================
# COURSE MANAGEMENT
# ==========================
def open_courses():
    win = tk.Toplevel(root)
    win.title("Courses")
    win.geometry("500x400")

    tk.Label(win, text="Course Name").pack()
    c_name = tk.Entry(win)
    c_name.pack()

    tk.Label(win, text="Duration").pack()
    c_duration = tk.Entry(win)
    c_duration.pack()

    def add_course():
        conn = sqlite3.connect("nvit.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO Course (course_name, duration) VALUES (?, ?)",
                    (c_name.get(), c_duration.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Course Added!")

    tk.Button(win, text="Add Course", command=add_course, bg="#0078D7", fg="white").pack(pady=10)


# ==========================
# INSTRUCTORS MANAGEMENT
# ==========================
def open_instructors():
    win = tk.Toplevel(root)
    win.title("Instructors")
    win.geometry("500x400")

    tk.Label(win, text="Instructor Name").pack()
    i_name = tk.Entry(win)
    i_name.pack()

    tk.Label(win, text="Expertise").pack()
    i_exp = tk.Entry(win)
    i_exp.pack()

    def add_instructor():
        conn = sqlite3.connect("nvit.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO Instructors (name, expertise) VALUES (?, ?)",
                    (i_name.get(), i_exp.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Instructor Added!")

    tk.Button(win, text="Add Instructor", command=add_instructor, bg="#0078D7", fg="white").pack(pady=10)


# ==========================
# RESULTS MANAGEMENT
# ==========================
def open_results():
    win = tk.Toplevel(root)
    win.title("Results")
    win.geometry("500x400")

    tk.Label(win, text="Student ID").pack()
    r_student = tk.Entry(win)
    r_student.pack()

    tk.Label(win, text="Course ID").pack()
    r_course = tk.Entry(win)
    r_course.pack()

    tk.Label(win, text="Grade").pack()
    r_grade = tk.Entry(win)
    r_grade.pack()

    def add_result():
        conn = sqlite3.connect("nvit.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO Result (student_id, course_id, grade) VALUES (?, ?, ?)",
                    (r_student.get(), r_course.get(), r_grade.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Result Added!")

    tk.Button(win, text="Add Result", command=add_result, bg="#0078D7", fg="white").pack(pady=10)


# ==========================
# LOGIN GUI
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
