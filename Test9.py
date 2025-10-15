import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB = "nvit.db"

# -------------------------
# Database Setup (ensure tables)
# -------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS Course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        duration TEXT NOT NULL
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS Instructors (
        instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expertise TEXT NOT NULL
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS Student_Information (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        course_id INTEGER,
        instructor_id INTEGER,
        FOREIGN KEY(course_id) REFERENCES Course(course_id),
        FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS Result (
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
# Utility DB helpers
# -------------------------
def run_query(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last = cur.lastrowid
    rows = cur.fetchall()
    conn.close()
    return last, rows

def fetch_all(query, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------------
# LOGIN / REGISTER (simple)
# -------------------------
def open_register():
    reg = tk.Toplevel(root)
    reg.title("Register - NVIT")
    reg.geometry("350x260")

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
            messagebox.showwarning("Error", "All fields are required")
            return
        try:
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name,email,pwd))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful")
            reg.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already registered")

    tk.Button(reg, text="Register", command=register_user, bg="#0078D7", fg="white").pack(pady=12)

def login_user():
    email = login_email.get().strip()
    pwd = login_password.get().strip()
    if not (email and pwd):
        messagebox.showwarning("Error", "Enter email and password")
        return
    rows = fetch_all("SELECT * FROM users WHERE email=? AND password=?", (email, pwd))
    if rows:
        messagebox.showinfo("Welcome", f"Welcome {rows[0][1]}!")
        open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid credentials")

# -------------------------
# DASHBOARD
# -------------------------
def open_dashboard():
    dash = tk.Toplevel(root)
    dash.title("NVIT Dashboard")
    dash.geometry("600x420")
    dash.config(bg="white")
    tk.Label(dash, text="NVIT Management Dashboard", font=("Arial",16,"bold"), fg="#0078D7", bg="white").pack(pady=12)

    btn_frame = tk.Frame(dash, bg="white"); btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Manage Students", width=20, command=open_students, bg="#0078D7", fg="white").grid(row=0,column=0,padx=8,pady=8)
    tk.Button(btn_frame, text="Manage Courses", width=20, command=open_courses, bg="#0078D7", fg="white").grid(row=0,column=1,padx=8,pady=8)
    tk.Button(btn_frame, text="Manage Instructors", width=20, command=open_instructors, bg="#0078D7", fg="white").grid(row=1,column=0,padx=8,pady=8)
    tk.Button(btn_frame, text="Manage Results", width=20, command=open_results, bg="#0078D7", fg="white").grid(row=1,column=1,padx=8,pady=8)

# -------------------------
# STUDENTS CRUD
# -------------------------
def open_students():
    win = tk.Toplevel(root); win.title("Students"); win.geometry("700x450")
    # Form
    frm = tk.Frame(win); frm.pack(pady=8)
    tk.Label(frm, text="Name").grid(row=0,column=0,padx=5,pady=5)
    e_name = tk.Entry(frm, width=30); e_name.grid(row=0,column=1)
    tk.Label(frm, text="Course ID").grid(row=1,column=0,padx=5,pady=5)
    e_course = tk.Entry(frm, width=10); e_course.grid(row=1,column=1, sticky="w")
    tk.Label(frm, text="Instructor ID").grid(row=2,column=0,padx=5,pady=5)
    e_instr = tk.Entry(frm, width=10); e_instr.grid(row=2,column=1, sticky="w")

    # Treeview
    cols = ("student_id","name","course_id","instructor_id")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=140 if c=="name" else 90, anchor="center")
    tree.pack(pady=10, fill="x")

    def load_students():
        for r in tree.get_children(): tree.delete(r)
        rows = fetch_all("SELECT student_id, name, course_id, instructor_id FROM Student_Information")
        for row in rows: tree.insert("", "end", values=row)

    def add_student():
        name = e_name.get().strip(); cid = e_course.get().strip() or None; iid = e_instr.get().strip() or None
        if not name:
            messagebox.showwarning("Error","Name required"); return
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("INSERT INTO Student_Information (name, course_id, instructor_id) VALUES (?,?,?)", (name, cid, iid))
        conn.commit(); conn.close()
        load_students(); clear_form()

    def on_select(event=None):
        sel = tree.focus()
        if not sel: return
        vals = tree.item(sel, "values")
        e_name.delete(0,tk.END); e_name.insert(0, vals[1])
        e_course.delete(0,tk.END); e_course.insert(0, vals[2] if vals[2] else "")
        e_instr.delete(0,tk.END); e_instr.insert(0, vals[3] if vals[3] else "")

    def update_student():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Error","Select a student to update"); return
        sid = tree.item(sel,"values")[0]
        name = e_name.get().strip(); cid = e_course.get().strip() or None; iid = e_instr.get().strip() or None
        if not name: messagebox.showwarning("Error","Name required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("UPDATE Student_Information SET name=?, course_id=?, instructor_id=? WHERE student_id=?",
                    (name, cid, iid, sid))
        conn.commit(); conn.close()
        load_students(); clear_form()

    def delete_student():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select a student to delete"); return
        sid = tree.item(sel,"values")[0]
        if messagebox.askyesno("Confirm","Delete selected student?"):
            conn = sqlite3.connect(DB); cur=conn.cursor()
            cur.execute("DELETE FROM Student_Information WHERE student_id=?", (sid,))
            conn.commit(); conn.close()
            load_students(); clear_form()

    def clear_form():
        e_name.delete(0,tk.END); e_course.delete(0,tk.END); e_instr.delete(0,tk.END)

    # Buttons
    btnf = tk.Frame(win); btnf.pack(pady=6)
    tk.Button(btnf, text="Add", command=add_student, bg="#0078D7", fg="white", width=10).grid(row=0,column=0,padx=4)
    tk.Button(btnf, text="Update", command=update_student, bg="#28a745", fg="white", width=10).grid(row=0,column=1,padx=4)
    tk.Button(btnf, text="Delete", command=delete_student, bg="#dc3545", fg="white", width=10).grid(row=0,column=2,padx=4)
    tk.Button(btnf, text="Clear", command=clear_form, width=10).grid(row=0,column=3,padx=4)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_students()

# -------------------------
# COURSES CRUD
# -------------------------
def open_courses():
    win = tk.Toplevel(root); win.title("Courses"); win.geometry("600x420")
    frm = tk.Frame(win); frm.pack(pady=8)
    tk.Label(frm, text="Course Name").grid(row=0,column=0,padx=5,pady=5)
    c_name = tk.Entry(frm, width=30); c_name.grid(row=0,column=1)
    tk.Label(frm, text="Duration").grid(row=1,column=0,padx=5,pady=5)
    c_dur = tk.Entry(frm, width=20); c_dur.grid(row=1,column=1)

    cols = ("course_id","course_name","duration")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c)
    tree.pack(pady=10, fill="x")

    def load_courses():
        for r in tree.get_children(): tree.delete(r)
        rows = fetch_all("SELECT course_id, course_name, duration FROM Course")
        for row in rows: tree.insert("", "end", values=row)

    def add_course():
        name = c_name.get().strip(); dur = c_dur.get().strip()
        if not (name and dur): messagebox.showwarning("Error","All fields required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("INSERT INTO Course (course_name, duration) VALUES (?,?)", (name,dur))
        conn.commit(); conn.close()
        load_courses(); clear_form()

    def on_sel(event=None):
        sel = tree.focus()
        if not sel: return
        v = tree.item(sel,"values")
        c_name.delete(0,tk.END); c_name.insert(0, v[1])
        c_dur.delete(0,tk.END); c_dur.insert(0, v[2])

    def update_course():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select a course"); return
        cid = tree.item(sel,"values")[0]
        name = c_name.get().strip(); dur = c_dur.get().strip()
        if not (name and dur): messagebox.showwarning("Error","All fields required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("UPDATE Course SET course_name=?, duration=? WHERE course_id=?", (name,dur,cid))
        conn.commit(); conn.close()
        load_courses(); clear_form()

    def delete_course():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select a course"); return
        cid = tree.item(sel,"values")[0]
        if messagebox.askyesno("Confirm","Delete selected course?"):
            conn = sqlite3.connect(DB); cur=conn.cursor()
            cur.execute("DELETE FROM Course WHERE course_id=?", (cid,))
            conn.commit(); conn.close()
            load_courses(); clear_form()

    def clear_form():
        c_name.delete(0,tk.END); c_dur.delete(0,tk.END)

    btnf = tk.Frame(win); btnf.pack(pady=6)
    tk.Button(btnf, text="Add", command=add_course, bg="#0078D7", fg="white", width=10).grid(row=0,column=0,padx=4)
    tk.Button(btnf, text="Update", command=update_course, bg="#28a745", fg="white", width=10).grid(row=0,column=1,padx=4)
    tk.Button(btnf, text="Delete", command=delete_course, bg="#dc3545", fg="white", width=10).grid(row=0,column=2,padx=4)
    tk.Button(btnf, text="Clear", command=clear_form, width=10).grid(row=0,column=3,padx=4)

    tree.bind("<<TreeviewSelect>>", on_sel)
    load_courses()

# -------------------------
# INSTRUCTORS CRUD
# -------------------------
def open_instructors():
    win = tk.Toplevel(root); win.title("Instructors"); win.geometry("600x420")
    frm = tk.Frame(win); frm.pack(pady=8)
    tk.Label(frm, text="Instructor Name").grid(row=0,column=0,padx=5,pady=5)
    i_name = tk.Entry(frm, width=30); i_name.grid(row=0,column=1)
    tk.Label(frm, text="Expertise").grid(row=1,column=0,padx=5,pady=5)
    i_exp = tk.Entry(frm, width=30); i_exp.grid(row=1,column=1)

    cols = ("instructor_id","name","expertise")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
    for c in cols: tree.heading(c, text=c)
    tree.pack(pady=10, fill="x")

    def load_instructors():
        for r in tree.get_children(): tree.delete(r)
        rows = fetch_all("SELECT instructor_id, name, expertise FROM Instructors")
        for row in rows: tree.insert("", "end", values=row)

    def add_instr():
        name = i_name.get().strip(); exp = i_exp.get().strip()
        if not (name and exp): messagebox.showwarning("Error","All fields required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("INSERT INTO Instructors (name, expertise) VALUES (?,?)", (name,exp))
        conn.commit(); conn.close()
        load_instructors(); clear_form()

    def on_sel(event=None):
        sel = tree.focus()
        if not sel: return
        v = tree.item(sel,"values")
        i_name.delete(0,tk.END); i_name.insert(0, v[1])
        i_exp.delete(0,tk.END); i_exp.insert(0, v[2])

    def update_instr():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select an instructor"); return
        iid = tree.item(sel,"values")[0]
        name = i_name.get().strip(); exp = i_exp.get().strip()
        if not (name and exp): messagebox.showwarning("Error","All fields required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("UPDATE Instructors SET name=?, expertise=? WHERE instructor_id=?", (name,exp,iid))
        conn.commit(); conn.close()
        load_instructors(); clear_form()

    def delete_instr():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select an instructor"); return
        iid = tree.item(sel,"values")[0]
        if messagebox.askyesno("Confirm","Delete selected instructor?"):
            conn = sqlite3.connect(DB); cur=conn.cursor()
            cur.execute("DELETE FROM Instructors WHERE instructor_id=?", (iid,))
            conn.commit(); conn.close()
            load_instructors(); clear_form()

    def clear_form():
        i_name.delete(0,tk.END); i_exp.delete(0,tk.END)

    btnf = tk.Frame(win); btnf.pack(pady=6)
    tk.Button(btnf, text="Add", command=add_instr, bg="#0078D7", fg="white", width=10).grid(row=0,column=0,padx=4)
    tk.Button(btnf, text="Update", command=update_instr, bg="#28a745", fg="white", width=10).grid(row=0,column=1,padx=4)
    tk.Button(btnf, text="Delete", command=delete_instr, bg="#dc3545", fg="white", width=10).grid(row=0,column=2,padx=4)
    tk.Button(btnf, text="Clear", command=clear_form, width=10).grid(row=0,column=3,padx=4)

    tree.bind("<<TreeviewSelect>>", on_sel)
    load_instructors()

# -------------------------
# RESULTS CRUD
# -------------------------
def open_results():
    win = tk.Toplevel(root); win.title("Results"); win.geometry("700x480")
    frm = tk.Frame(win); frm.pack(pady=8)
    tk.Label(frm, text="Student ID").grid(row=0,column=0,padx=5,pady=5)
    r_sid = tk.Entry(frm, width=12); r_sid.grid(row=0,column=1)
    tk.Label(frm, text="Course ID").grid(row=1,column=0,padx=5,pady=5)
    r_cid = tk.Entry(frm, width=12); r_cid.grid(row=1,column=1)
    tk.Label(frm, text="Grade").grid(row=2,column=0,padx=5,pady=5)
    r_grade = tk.Entry(frm, width=12); r_grade.grid(row=2,column=1)

    cols = ("result_id","student_id","course_id","grade")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
    for c in cols: tree.heading(c, text=c)
    tree.pack(pady=10, fill="x")

    def load_results():
        for r in tree.get_children(): tree.delete(r)
        rows = fetch_all("SELECT result_id, student_id, course_id, grade FROM Result")
        for row in rows: tree.insert("", "end", values=row)

    def add_result():
        sid = r_sid.get().strip(); cid = r_cid.get().strip(); grade = r_grade.get().strip()
        if not (sid and cid and grade): messagebox.showwarning("Error","All fields required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("INSERT INTO Result (student_id, course_id, grade) VALUES (?,?,?)", (sid,cid,grade))
        conn.commit(); conn.close()
        load_results(); clear_form()

    def on_sel(event=None):
        sel = tree.focus()
        if not sel: return
        v = tree.item(sel,"values")
        r_sid.delete(0,tk.END); r_sid.insert(0, v[1])
        r_cid.delete(0,tk.END); r_cid.insert(0, v[2])
        r_grade.delete(0,tk.END); r_grade.insert(0, v[3])

    def update_result():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select a result"); return
        rid = tree.item(sel,"values")[0]
        sid = r_sid.get().strip(); cid = r_cid.get().strip(); grade = r_grade.get().strip()
        if not (sid and cid and grade): messagebox.showwarning("Error","All fields required"); return
        conn = sqlite3.connect(DB); cur=conn.cursor()
        cur.execute("UPDATE Result SET student_id=?, course_id=?, grade=? WHERE result_id=?", (sid,cid,grade,rid))
        conn.commit(); conn.close()
        load_results(); clear_form()

    def delete_result():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Error","Select a result"); return
        rid = tree.item(sel,"values")[0]
        if messagebox.askyesno("Confirm","Delete selected result?"):
            conn = sqlite3.connect(DB); cur=conn.cursor()
            cur.execute("DELETE FROM Result WHERE result_id=?", (rid,))
            conn.commit(); conn.close()
            load_results(); clear_form()

    def clear_form():
        r_sid.delete(0,tk.END); r_cid.delete(0,tk.END); r_grade.delete(0,tk.END)

    btnf = tk.Frame(win); btnf.pack(pady=6)
    tk.Button(btnf, text="Add", command=add_result, bg="#0078D7", fg="white", width=10).grid(row=0,column=0,padx=4)
    tk.Button(btnf, text="Update", command=update_result, bg="#28a745", fg="white", width=10).grid(row=0,column=1,padx=4)
    tk.Button(btnf, text="Delete", command=delete_result, bg="#dc3545", fg="white", width=10).grid(row=0,column=2,padx=4)
    tk.Button(btnf, text="Clear", command=clear_form, width=10).grid(row=0,column=3,padx=4)

    tree.bind("<<TreeviewSelect>>", on_sel)
    load_results()

# -------------------------
# MAIN LOGIN GUI
# -------------------------
root = tk.Tk()
root.title("NVIT Login System")
root.geometry("420x380")
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
