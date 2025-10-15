import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, hashlib

DB = "nvit.db"

# -------------------------
# Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS Course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        duration TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS Instructors (
        instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expertise TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS Student_Information (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        course_id INTEGER,
        instructor_id INTEGER,
        FOREIGN KEY(course_id) REFERENCES Course(course_id),
        FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS Result (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        grade TEXT,
        FOREIGN KEY(student_id) REFERENCES Student_Information(student_id),
        FOREIGN KEY(course_id) REFERENCES Course(course_id)
    )""")

    conn.commit()
    conn.close()

init_db()

# -------------------------
# DB Helper
# -------------------------
def fetch_all(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def run_query(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

# -------------------------
# Password Hashing
# -------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------
# Register
# -------------------------
def open_register():
    reg = tk.Toplevel(root)
    reg.title("Register - NVIT")
    reg.geometry("350x270")

    tk.Label(reg, text="Full Name:").pack(pady=5)
    name_e = tk.Entry(reg, width=35); name_e.pack()
    tk.Label(reg, text="Email:").pack(pady=5)
    email_e = tk.Entry(reg, width=35); email_e.pack()
    tk.Label(reg, text="Password:").pack(pady=5)
    pass_e = tk.Entry(reg, width=35, show="*"); pass_e.pack()

    def register_user():
        name = name_e.get().strip()
        email = email_e.get().strip()
        pwd = pass_e.get().strip()
        if not (name and email and pwd):
            messagebox.showwarning("Error", "All fields required")
            return
        hashed = hash_password(pwd)
        try:
            run_query("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name,email,hashed))
            messagebox.showinfo("Success", "Registration successful")
            reg.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already registered")

    tk.Button(reg, text="Register", command=register_user, bg="#0078D7", fg="white").pack(pady=12)

# -------------------------
# Login
# -------------------------
def login_user():
    email = login_email.get().strip()
    pwd = login_password.get().strip()
    hashed = hash_password(pwd)
    user = fetch_all("SELECT * FROM users WHERE email=? AND password=?", (email,hashed))
    if user:
        messagebox.showinfo("Welcome", f"Welcome {user[0][1]}!")
        open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid email or password")

# -------------------------
# Dashboard
# -------------------------
def open_dashboard():
    dash = tk.Toplevel(root)
    dash.title("NVIT Dashboard")
    dash.geometry("600x400")
    dash.config(bg="white")

    tk.Label(dash, text="NVIT Dashboard", font=("Arial", 18, "bold"), bg="white", fg="#0078D7").pack(pady=20)
    frame = tk.Frame(dash, bg="white"); frame.pack(pady=15)

    tk.Button(frame, text="Manage Students", width=20, bg="#0078D7", fg="white", command=open_students).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(frame, text="Manage Courses", width=20, bg="#0078D7", fg="white", command=open_courses).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(frame, text="Manage Instructors", width=20, bg="#0078D7", fg="white", command=open_instructors).grid(row=1, column=0, padx=10, pady=10)
    tk.Button(frame, text="Manage Results", width=20, bg="#0078D7", fg="white", command=open_results).grid(row=1, column=1, padx=10, pady=10)

# -------------------------
# Student CRUD (with Combobox)
# -------------------------
def open_students():
    win = tk.Toplevel(root)
    win.title("Manage Students")
    win.geometry("750x500")

    tk.Label(win, text="Student Name:").grid(row=0, column=0, padx=10, pady=10)
    name_e = tk.Entry(win, width=30); name_e.grid(row=0, column=1)

    tk.Label(win, text="Course:").grid(row=1, column=0, padx=10, pady=10)
    courses = fetch_all("SELECT course_id, course_name FROM Course")
    course_dict = {c[1]: c[0] for c in courses}
    course_combo = ttk.Combobox(win, values=list(course_dict.keys()), width=27)
    course_combo.grid(row=1, column=1)

    tk.Label(win, text="Instructor:").grid(row=2, column=0, padx=10, pady=10)
    instructors = fetch_all("SELECT instructor_id, name FROM Instructors")
    instr_dict = {i[1]: i[0] for i in instructors}
    instr_combo = ttk.Combobox(win, values=list(instr_dict.keys()), width=27)
    instr_combo.grid(row=2, column=1)

    # Treeview
    cols = ("ID", "Name", "Course", "Instructor")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=150)
    tree.grid(row=4, column=0, columnspan=4, pady=20)

    def load_students():
        tree.delete(*tree.get_children())
        data = fetch_all("""
            SELECT s.student_id, s.name, c.course_name, i.name
            FROM Student_Information s
            LEFT JOIN Course c ON s.course_id=c.course_id
            LEFT JOIN Instructors i ON s.instructor_id=i.instructor_id
        """)
        for row in data:
            tree.insert("", "end", values=row)

    def add_student():
        name = name_e.get().strip()
        course = course_combo.get()
        instr = instr_combo.get()
        cid = course_dict.get(course)
        iid = instr_dict.get(instr)
        if not name:
            messagebox.showwarning("Error", "Name required")
            return
        run_query("INSERT INTO Student_Information (name,course_id,instructor_id) VALUES (?,?,?)", (name,cid,iid))
        load_students()
        clear_form()

    def clear_form():
        name_e.delete(0, tk.END)
        course_combo.set('')
        instr_combo.set('')

    def on_select(event):
        sel = tree.focus()
        if not sel: return
        vals = tree.item(sel, "values")
        name_e.delete(0, tk.END); name_e.insert(0, vals[1])
        course_combo.set(vals[2] or '')
        instr_combo.set(vals[3] or '')

    def update_student():
        sel = tree.focus()
        if not sel: return messagebox.showwarning("Error", "Select a record")
        sid = tree.item(sel, "values")[0]
        name = name_e.get().strip()
        course = course_combo.get()
        instr = instr_combo.get()
        cid = course_dict.get(course)
        iid = instr_dict.get(instr)
        run_query("UPDATE Student_Information SET name=?, course_id=?, instructor_id=? WHERE student_id=?", (name,cid,iid,sid))
        load_students(); clear_form()

    def delete_student():
        sel = tree.focus()
        if not sel: return messagebox.showwarning("Error", "Select a record")
        sid = tree.item(sel, "values")[0]
        if messagebox.askyesno("Confirm", "Delete this student?"):
            run_query("DELETE FROM Student_Information WHERE student_id=?", (sid,))
            load_students(); clear_form()

    # Buttons
    tk.Button(win, text="Add", bg="#0078D7", fg="white", width=10, command=add_student).grid(row=3,column=0,pady=10)
    tk.Button(win, text="Update", bg="#28a745", fg="white", width=10, command=update_student).grid(row=3,column=1,pady=10)
    tk.Button(win, text="Delete", bg="#dc3545", fg="white", width=10, command=delete_student).grid(row=3,column=2,pady=10)
    tk.Button(win, text="Clear", width=10, command=clear_form).grid(row=3,column=3,pady=10)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_students()

# -------------------------
# Courses
# -------------------------
def open_courses():
    win = tk.Toplevel(root)
    win.title("Courses")
    win.geometry("600x400")
    tk.Label(win, text="Course Name:").pack(pady=5)
    cname = tk.Entry(win, width=35); cname.pack()
    tk.Label(win, text="Duration:").pack(pady=5)
    cdur = tk.Entry(win, width=35); cdur.pack()

    cols = ("ID","Name","Duration")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols: tree.heading(c, text=c)
    tree.pack(pady=20, fill="x")

    def load():
        tree.delete(*tree.get_children())
        for row in fetch_all("SELECT * FROM Course"):
            tree.insert("", "end", values=row)

    def add():
        n=cname.get(); d=cdur.get()
        if not (n and d): return messagebox.showwarning("Error","All fields")
        run_query("INSERT INTO Course (course_name,duration) VALUES (?,?)",(n,d))
        load(); cname.delete(0,tk.END); cdur.delete(0,tk.END)

    tk.Button(win, text="Add", bg="#0078D7", fg="white", command=add).pack(pady=10)
    load()

# -------------------------
# Instructors
# -------------------------
def open_instructors():
    win = tk.Toplevel(root)
    win.title("Instructors")
    win.geometry("600x400")
    tk.Label(win, text="Instructor Name:").pack(pady=5)
    iname = tk.Entry(win, width=35); iname.pack()
    tk.Label(win, text="Expertise:").pack(pady=5)
    iexp = tk.Entry(win, width=35); iexp.pack()

    cols = ("ID","Name","Expertise")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols: tree.heading(c, text=c)
    tree.pack(pady=20, fill="x")

    def load():
        tree.delete(*tree.get_children())
        for row in fetch_all("SELECT * FROM Instructors"):
            tree.insert("", "end", values=row)

    def add():
        n=iname.get(); e=iexp.get()
        if not (n and e): return messagebox.showwarning("Error","All fields")
        run_query("INSERT INTO Instructors (name,expertise) VALUES (?,?)",(n,e))
        load(); iname.delete(0,tk.END); iexp.delete(0,tk.END)

    tk.Button(win, text="Add", bg="#0078D7", fg="white", command=add).pack(pady=10)
    load()

# -------------------------
# Results
# -------------------------
def open_results():
    win = tk.Toplevel(root)
    win.title("Results")
    win.geometry("600x400")
    tk.Label(win, text="Student ID:").pack(pady=5)
    sid = tk.Entry(win, width=35); sid.pack()
    tk.Label(win, text="Course ID:").pack(pady=5)
    cid = tk.Entry(win, width=35); cid.pack()
    tk.Label(win, text="Grade:").pack(pady=5)
    grade = tk.Entry(win, width=35); grade.pack()

    cols = ("ID","Student","Course","Grade")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols: tree.heading(c, text=c)
    tree.pack(pady=20, fill="x")

    def load():
        tree.delete(*tree.get_children())
        for row in fetch_all("SELECT * FROM Result"):
            tree.insert("", "end", values=row)

    def add():
        s=sid.get(); c=cid.get(); g=grade.get()
        if not (s and c and g): return messagebox.showwarning("Error","All fields")
        run_query("INSERT INTO Result (student_id,course_id,grade) VALUES (?,?,?)",(s,c,g))
        load(); sid.delete(0,tk.END); cid.delete(0,tk.END); grade.delete(0,tk.END)

    tk.Button(win, text="Add", bg="#0078D7", fg="white", command=add).pack(pady=10)
    load()

# -------------------------
# MAIN LOGIN UI
# -------------------------
root = tk.Tk()
root.title("NVIT Login")
root.geometry("420x350")
root.config(bg="white")

tk.Label(root, text="NVIT", font=("Arial", 22, "bold"), fg="#0078D7", bg="white").pack(pady=10)
tk.Label(root, text="New Vision Information Technology Limited", font=("Arial", 10), bg="white").pack()

tk.Label(root, text="Email", bg="white", font=("Arial",11)).pack(pady=(20,5))
login_email = tk.Entry(root, width=35); login_email.pack()
tk.Label(root, text="Password", bg="white", font=("Arial",11)).pack(pady=(10,5))
login_password = tk.Entry(root, width=35, show="*"); login_password.pack()

tk.Button(root, text="Login", bg="#0078D7", fg="white", width=18, command=login_user).pack(pady=16)
tk.Button(root, text="Create Account", bg="white", fg="#0078D7", bd=0, command=open_register).pack()

root.mainloop()
