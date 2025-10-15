# NVIT_management_system.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, hashlib

DB = "nvit_system.db"


# -------------------------Database Setup -------------------------

def get_conn():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # -------------------------Create Users Table -------------------------
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    # -------------------------Create Course  Table -------------------------
    c.execute("""CREATE TABLE IF NOT EXISTS Course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL UNIQUE,
        duration TEXT NOT NULL,
        course_price REAL
    )""")

    # -------------------------Create Instructors  Table -------------------------
    c.execute("""CREATE TABLE IF NOT EXISTS Instructors (
        instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        father_name TEXT,
        mother_name TEXT,
        blood_group TEXT,
        mobile_no TEXT,
        expertise TEXT
    )""")

    # -------------------------Create Student  Table -------------------------
    c.execute("""CREATE TABLE IF NOT EXISTS Student (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        father_name TEXT,
        mother_name TEXT,
        address TEXT,
        blood_group TEXT,
        mobile_no TEXT,
        course_id INTEGER,
        instructor_id INTEGER,
        batch_no TEXT,
        FOREIGN KEY(course_id) REFERENCES Course(course_id) ON DELETE SET NULL,
        FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id) ON DELETE SET NULL
    )""")

    # -------------------------Create Result Table -------------------------
    c.execute("""CREATE TABLE IF NOT EXISTS Result (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        grade TEXT,
        instructor_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
        FOREIGN KEY(course_id) REFERENCES Course(course_id) ON DELETE SET NULL,
        FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id) ON DELETE SET NULL
    )""")
    conn.commit(); conn.close()

init_db()


# -------------------------DB helpers -------------------------
def fetch_all(q, p=()):
    conn = get_conn(); cur = conn.cursor(); cur.execute(q, p)
    rows = cur.fetchall(); conn.close(); return rows

def run_query(q, p=()):
    conn = get_conn(); cur = conn.cursor(); cur.execute(q, p)
    conn.commit(); conn.close()
# ------------------------- Password hashing -----------------------

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ------------------------- Styling & Design  -----------------------

def setup_style():
    s = ttk.Style()
    try:
        s.theme_use('clam')
    except:
        pass
    BG = '#E3F2FD'
    PRIMARY = '#1565C0'
    SUCCESS = '#28a745'
    DANGER = '#C62828'
    TEXT = '#0D47A1'

    s.configure('TFrame', background=BG)
    s.configure('Header.TLabel', background=PRIMARY, foreground='white',
                font=('Helvetica', 16, 'bold'), padding=10)
    s.configure('Title.TLabel', background=BG, foreground=TEXT,
                font=('Helvetica', 26, 'bold'))
    s.configure('Sub.TLabel', background=BG, foreground=TEXT, font=('Helvetica', 10))
    s.configure('TLabel', background=BG, foreground=TEXT, font=('Helvetica', 10))
    s.configure('TEntry', padding=4)
    s.configure('TButton', padding=6, relief='flat', font=('Helvetica', 10, 'bold'))

    s.configure('Primary.TButton', background=PRIMARY, foreground='white')
    s.map('Primary.TButton', background=[('active', '#0f4a9a')])
    s.configure('Success.TButton', background=SUCCESS, foreground='white')
    s.map('Success.TButton', background=[('active', '#218838')])
    s.configure('Danger.TButton', background=DANGER, foreground='white')
    s.map('Danger.TButton', background=[('active', '#9e1f1f')])
    s.configure('Secondary.TButton', background='#ffffff', foreground=PRIMARY)
    s.map('Secondary.TButton', background=[('active', '#f0f7ff')])

setup_style()
# ------------------------- Utils  -----------------------

def center(win, w=800, h=600):
    win.update_idletasks()
    sw = win.winfo_screenwidth(); sh = win.winfo_screenheight()
    x = (sw//2) - (w//2); y = (sh//2) - (h//2)
    win.geometry(f"{w}x{h}+{x}+{y}")
# ------------------------- Register window  -----------------------
def open_register():
    reg = tk.Toplevel(root); reg.title("Register - NVIT")
    center(reg, 420, 320); reg.configure(bg='#E3F2FD')
    frm = ttk.Frame(reg, padding=12); frm.pack(fill='both', expand=True)
    ttk.Label(frm, text="Create Account", style='Header.TLabel').pack(fill='x', pady=(0,10))
    ttk.Label(frm, text="Full Name:").pack(anchor='w', pady=(6,0))
    name_e = ttk.Entry(frm, width=40); name_e.pack()
    ttk.Label(frm, text="Email:").pack(anchor='w', pady=(8,0))
    email_e = ttk.Entry(frm, width=40); email_e.pack()
    ttk.Label(frm, text="Password:").pack(anchor='w', pady=(8,0))
    pass_e = ttk.Entry(frm, width=40, show='*'); pass_e.pack()
    def register_user():
        name = name_e.get().strip(); email = email_e.get().strip(); pwd = pass_e.get().strip()
        if not (name and email and pwd):
            messagebox.showwarning("Validation", "All fields required"); return
        try:
            run_query("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name,email,hash_password(pwd)))
            messagebox.showinfo("Success", "Registration successful"); reg.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already registered")
    ttk.Button(frm, text="Register", style='Primary.TButton', command=register_user).pack(pady=12)


# ------------------------- Login  -----------------------
def login_user():
    email = login_email.get().strip(); pwd = login_password.get().strip()
    if not (email and pwd):
        messagebox.showwarning("Validation", "Email and Password required"); return
    hashed = hash_password(pwd)
    user = fetch_all("SELECT id,name FROM users WHERE email=? AND password=?", (email, hashed))
    if user:
        messagebox.showinfo("Welcome", f"Welcome {user[0][1]}!"); open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid email or password")

# ------------------------- Dashboard  -----------------------
def open_dashboard():
    dash = tk.Toplevel(root); dash.title(" New Vision IT Ltd")
    center(dash, 720, 420); dash.configure(bg='#E3F2FD')
    main = ttk.Frame(dash, padding=12); main.pack(expand=True, fill='both')
    ttk.Label(main, text="NVIT Dashboard", style='Header.TLabel').pack(fill='x', pady=(0,12))
    ttk.Label(main, text="Welcome To New Vision IT Ltd", style='Title.TLabel',font=("Helvetica", 20, "bold"),foreground="#0D47A1").pack(pady=(4,10))
    btn_frame = ttk.Frame(main); btn_frame.pack(pady=18)
    ttk.Button(btn_frame, text=" Students", width=20, style='Primary.TButton', command=open_students).grid(row=0,column=0,padx=10,pady=8)
    ttk.Button(btn_frame, text=" Courses", width=20, style='Primary.TButton', command=open_courses).grid(row=0,column=1,padx=10,pady=8)
    ttk.Button(btn_frame, text=" Instructors", width=20, style='Primary.TButton', command=open_instructors).grid(row=1,column=0,padx=10,pady=8)
    ttk.Button(btn_frame, text=" Results", width=20, style='Primary.TButton', command=open_results).grid(row=1,column=1,padx=10,pady=8)
    ttk.Label(main, text="Click On the Button", style='Sub.TLabel').pack(pady=8)
# ------------------------- Courses  -----------------------

def open_courses():
    win = tk.Toplevel(root); win.title("Manage Courses")
    center(win, 660, 480); win.configure(bg='#E3F2FD')
    frm = ttk.Frame(win, padding=12); frm.pack(expand=True, fill='both')
    ttk.Label(frm, text="Courses", style='Header.TLabel').pack(fill='x', pady=(0,10))
    form = ttk.Frame(frm); form.pack(fill='x', pady=6)
    ttk.Label(form, text="Course Name:").grid(row=0,column=0, sticky='w', padx=6, pady=6)
    cname = ttk.Entry(form, width=40); cname.grid(row=0,column=1, padx=6, pady=6)
    ttk.Label(form, text="Duration:").grid(row=1,column=0, sticky='w', padx=6, pady=6)
    cdur = ttk.Entry(form, width=40); cdur.grid(row=1,column=1, padx=6, pady=6)
    ttk.Label(form, text="Price:").grid(row=2,column=0, sticky='w', padx=6, pady=6)
    cprice = ttk.Entry(form, width=40); cprice.grid(row=2,column=1, padx=6, pady=6)
    cols = ("ID","Course Name","Duration","Price")
    tree = ttk.Treeview(frm, columns=cols, show='headings', height=9)
    for c in cols: tree.heading(c, text=c); tree.column(c, anchor='center')
    tree.pack(fill='both', padx=6, pady=8)
    def load():
        tree.delete(*tree.get_children())
        for r in fetch_all("SELECT course_id, course_name, duration, course_price FROM Course ORDER BY course_id"):
            tree.insert("", "end", values=r)
    def clear_form():
        cname.delete(0,tk.END); cdur.delete(0,tk.END); cprice.delete(0,tk.END)
    def add():
        n = cname.get().strip(); d = cdur.get().strip(); p = cprice.get().strip()
        if not (n and d): messagebox.showwarning("Validation", "Name & Duration required"); return
        try:
            run_query("INSERT INTO Course (course_name,duration,course_price) VALUES (?,?,?)", (n,d, float(p) if p else None))
            load(); clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Course name must be unique")
    def on_select(e=None):
        sel = tree.focus();
        if not sel: return
        vals = tree.item(sel,'values')
        cname.delete(0,tk.END); cname.insert(0, vals[1])
        cdur.delete(0,tk.END); cdur.insert(0, vals[2])
        cprice.delete(0,tk.END); cprice.insert(0, vals[3] if vals[3] is not None else '')
    def update_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select", "Select course to update"); return
        cid = tree.item(sel,'values')[0]
        n = cname.get().strip(); d = cdur.get().strip(); p = cprice.get().strip()
        if not (n and d): messagebox.showwarning("Validation", "Name & Duration required"); return
        try:
            run_query("UPDATE Course SET course_name=?,duration=?,course_price=? WHERE course_id=?", (n,d, float(p) if p else None, cid))
            load(); clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Course name must be unique")
    def delete_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select", "Select course to delete"); return
        cid = tree.item(sel,'values')[0]
        if messagebox.askyesno("Confirm", "Delete this course? Related students will set course to NULL."):
            run_query("DELETE FROM Course WHERE course_id=?", (cid,)); load(); clear_form()
    btnf = ttk.Frame(frm); btnf.pack(fill='x', pady=6)
    ttk.Button(btnf, text="Add", style='Primary.TButton', command=add).pack(side='left', padx=6)
    ttk.Button(btnf, text="Update", style='Success.TButton', command=update_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Delete", style='Danger.TButton', command=delete_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Clear", command=clear_form).pack(side='left', padx=6)
    ttk.Button(btnf, text="Refresh", command=load).pack(side='right', padx=6)
    tree.bind("<<TreeviewSelect>>", on_select); load()


# ------------------------- Instructors  -----------------------

def open_instructors():
    win = tk.Toplevel(root); win.title("Manage Instructors")
    center(win, 820, 520); win.configure(bg='#E3F2FD')
    frm = ttk.Frame(win, padding=12); frm.pack(expand=True, fill='both')
    ttk.Label(frm, text="Instructors", style='Header.TLabel').pack(fill='x', pady=(0,10))
    labels = ["Name","Father Name","Mother Name","Blood Group","Mobile No","Expertise"]
    entries = {}; form = ttk.Frame(frm); form.pack(fill='x', pady=6)
    for i,l in enumerate(labels):
        ttk.Label(form, text=l+':').grid(row=i,column=0, sticky='w', padx=6, pady=4)
        e = ttk.Entry(form, width=48); e.grid(row=i,column=1, padx=6, pady=4); entries[l]=e
    cols = ("ID","Name","Father","Mother","Blood","Mobile","Expertise")
    tree = ttk.Treeview(frm, columns=cols, show='headings', height=10)
    for c in cols: tree.heading(c, text=c); tree.column(c, anchor='center')
    tree.pack(fill='both', padx=6, pady=8)
    def load():
        tree.delete(*tree.get_children())
        for r in fetch_all("SELECT instructor_id, name, father_name, mother_name, blood_group, mobile_no, expertise FROM Instructors ORDER BY instructor_id"):
            tree.insert("", "end", values=r)
    def clear_form():
        for e in entries.values(): e.delete(0,tk.END)
    def add():
        vals = [entries[l].get().strip() for l in labels]
        if not vals[0]: messagebox.showwarning("Validation", "Name required"); return
        run_query("INSERT INTO Instructors (name,father_name,mother_name,blood_group,mobile_no,expertise) VALUES (?,?,?,?,?,?)", tuple(vals))
        load(); clear_form()
    def on_select(e=None):
        sel = tree.focus();
        if not sel: return
        vals = tree.item(sel,'values')
        for i,l in enumerate(labels):
            entries[l].delete(0,tk.END); entries[l].insert(0, vals[i+1] if vals[i+1] is not None else '')
    def update_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Select instructor to update"); return
        iid = tree.item(sel,'values')[0]; vals = [entries[l].get().strip() for l in labels]
        run_query("UPDATE Instructors SET name=?,father_name=?,mother_name=?,blood_group=?,mobile_no=?,expertise=? WHERE instructor_id=?", (*vals, iid))
        load(); clear_form()
    def delete_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Select instructor to delete"); return
        iid = tree.item(sel,'values')[0]
        if messagebox.askyesno("Confirm", "Delete this instructor? Related students will set instructor to NULL."):
            run_query("DELETE FROM Instructors WHERE instructor_id=?", (iid,)); load(); clear_form()
    btnf = ttk.Frame(frm); btnf.pack(fill='x', pady=6)
    ttk.Button(btnf, text="Add", style='Primary.TButton', command=add).pack(side='left', padx=6)
    ttk.Button(btnf, text="Update", style='Success.TButton', command=update_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Delete", style='Danger.TButton', command=delete_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Clear", command=clear_form).pack(side='left', padx=6)
    ttk.Button(btnf, text="Refresh", command=load).pack(side='right', padx=6)
    tree.bind("<<TreeviewSelect>>", on_select); load()

# ------------------------- Students  -----------------------

def open_students():
    win = tk.Toplevel(root); win.title("Manage Students")
    center(win, 980, 620); win.configure(bg='#E3F2FD')
    frm = ttk.Frame(win, padding=12); frm.pack(expand=True, fill='both')
    ttk.Label(frm, text="Students", style='Header.TLabel').pack(fill='x', pady=(0,10))
    labels = ["Name","Father Name","Mother Name","Address","Blood Group","Mobile No","Course","Instructor","Batch No"]
    widgets = {}; form = ttk.Frame(frm); form.pack(fill='x', pady=6)
    for i,l in enumerate(labels):
        ttk.Label(form, text=l+':').grid(row=i,column=0, sticky='w', padx=6, pady=4)
        if l in ("Course","Instructor"):
            cb = ttk.Combobox(form, width=46); cb.grid(row=i,column=1, padx=6, pady=4); widgets[l]=cb
        else:
            e = ttk.Entry(form, width=48); e.grid(row=i,column=1, padx=6, pady=4); widgets[l]=e
    cols = ("ID","Name","Father","Mother","Address","Blood","Mobile","Course","Instructor","Batch")
    tree = ttk.Treeview(frm, columns=cols, show='headings', height=12)
    for c in cols: tree.heading(c, text=c); tree.column(c, anchor='center', width=100)
    tree.pack(fill='both', padx=6, pady=8)
    def load_combos():
        courses = fetch_all("SELECT course_id, course_name FROM Course ORDER BY course_name")
        course_map = {f"{c[0]} - {c[1]}": c[0] for c in courses}
        widgets["Course"]['values'] = list(course_map.keys())
        instrs = fetch_all("SELECT instructor_id, name FROM Instructors ORDER BY name")
        instr_map = {f"{i[0]} - {i[1]}": i[0] for i in instrs}
        widgets["Instructor"]['values'] = list(instr_map.keys())
        return course_map, instr_map
    course_map, instr_map = load_combos()
    def load():
        tree.delete(*tree.get_children())
        data = fetch_all("""
            SELECT s.student_id, s.name, s.father_name, s.mother_name, s.address, s.blood_group, s.mobile_no,
                   c.course_name, i.name, s.batch_no
            FROM Student s
            LEFT JOIN Course c ON s.course_id=c.course_id
            LEFT JOIN Instructors i ON s.instructor_id=i.instructor_id
            ORDER BY s.student_id
        """)
        for r in data: tree.insert("", "end", values=r)
    def clear_form():
        for k,w in widgets.items():
            if isinstance(w, ttk.Combobox): w.set('')
            else: w.delete(0, tk.END)
    def add():
        vals = [widgets[l].get().strip() if isinstance(widgets[l], ttk.Combobox) else widgets[l].get().strip() for l in labels]
        if not vals[0]: messagebox.showwarning("Validation", "Student name required"); return
        cid = course_map.get(vals[6]); iid = instr_map.get(vals[7])
        run_query("""INSERT INTO Student (name,father_name,mother_name,address,blood_group,mobile_no,course_id,instructor_id,batch_no)
                     VALUES (?,?,?,?,?,?,?,?,?)""", (vals[0],vals[1],vals[2],vals[3],vals[4],vals[5],cid,iid,vals[8]))
        load(); clear_form()
    def on_select(e=None):
        sel = tree.focus();
        if not sel: return
        vals = tree.item(sel,'values')
        for i,l in enumerate(labels):
            w = widgets[l]
            if isinstance(w, ttk.Combobox):
                if l == "Course":
                    if vals[7]:
                        cid = fetch_all("SELECT course_id FROM Course WHERE course_name=?", (vals[7],))
                        widgets["Course"].set(f"{cid[0][0]} - {vals[7]}" if cid else '')
                    else: widgets["Course"].set('')
                else:
                    if vals[8]:
                        iid = fetch_all("SELECT instructor_id FROM Instructors WHERE name=?", (vals[8],))
                        widgets["Instructor"].set(f"{iid[0][0]} - {vals[8]}" if iid else '')
                    else: widgets["Instructor"].set('')
            else:
                w.delete(0, tk.END); w.insert(0, vals[i+1] if vals[i+1] is not None else '')
    def update_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Select a student to update"); return
        sid = tree.item(sel,'values')[0]
        vals = [widgets[l].get().strip() if isinstance(widgets[l], ttk.Combobox) else widgets[l].get().strip() for l in labels]
        cid = course_map.get(vals[6]); iid = instr_map.get(vals[7])
        run_query("""UPDATE Student SET name=?,father_name=?,mother_name=?,address=?,blood_group=?,mobile_no=?,course_id=?,instructor_id=?,batch_no=? WHERE student_id=?""",
                  (vals[0],vals[1],vals[2],vals[3],vals[4],vals[5],cid,iid,vals[8],sid))
        load(); clear_form()
    def delete_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Select a student to delete"); return
        sid = tree.item(sel,'values')[0]
        if messagebox.askyesno("Confirm", "Delete this student? Related results will be deleted."):
            run_query("DELETE FROM Student WHERE student_id=?", (sid,)); load(); clear_form()
    btnf = ttk.Frame(frm); btnf.pack(fill='x', pady=6)
    ttk.Button(btnf, text="Add", style='Primary.TButton', command=add).pack(side='left', padx=6)
    ttk.Button(btnf, text="Update", style='Success.TButton', command=update_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Delete", style='Danger.TButton', command=delete_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Clear", command=clear_form).pack(side='left', padx=6)
    ttk.Button(btnf, text="Refresh Combos", command=lambda: refresh_combos()).pack(side='right', padx=6)
    ttk.Button(btnf, text="Refresh List", command=load).pack(side='right', padx=6)
    def refresh_combos():
        nonlocal course_map, instr_map
        course_map, instr_map = load_combos()
    tree.bind("<<TreeviewSelect>>", on_select); load()

# ------------------------- Results  -----------------------

def open_results():
    win = tk.Toplevel(root); win.title("Manage Results")
    center(win, 900, 520); win.configure(bg='#E3F2FD')
    frm = ttk.Frame(win, padding=12); frm.pack(expand=True, fill='both')
    ttk.Label(frm, text="Results", style='Header.TLabel').pack(fill='x', pady=(0,10))
    form = ttk.Frame(frm); form.pack(fill='x', pady=6)
    ttk.Label(form, text="Student:").grid(row=0,column=0, sticky='w', padx=6, pady=6)
    student_cb = ttk.Combobox(form, width=48); student_cb.grid(row=0,column=1, padx=6, pady=6)
    ttk.Label(form, text="Course:").grid(row=1,column=0, sticky='w', padx=6, pady=6)
    course_cb = ttk.Combobox(form, width=48); course_cb.grid(row=1,column=1, padx=6, pady=6)
    ttk.Label(form, text="Instructor:").grid(row=2,column=0, sticky='w', padx=6, pady=6)
    instr_cb = ttk.Combobox(form, width=48); instr_cb.grid(row=2,column=1, padx=6, pady=6)
    ttk.Label(form, text="Grade:").grid(row=3,column=0, sticky='w', padx=6, pady=6)
    grade_e = ttk.Entry(form, width=20); grade_e.grid(row=3,column=1, padx=6, pady=6, sticky='w')
    cols = ("ID","Student","Course","Instructor","Grade")
    tree = ttk.Treeview(frm, columns=cols, show='headings', height=10)
    for c in cols: tree.heading(c, text=c); tree.column(c, anchor='center')
    tree.pack(fill='both', padx=6, pady=8)
    def load_combos():
        students = fetch_all("SELECT student_id, name FROM Student ORDER BY name")
        student_map = {f"{s[0]} - {s[1]}": s[0] for s in students}
        student_cb['values'] = list(student_map.keys())
        courses = fetch_all("SELECT course_id, course_name FROM Course ORDER BY course_name")
        course_map = {f"{c[0]} - {c[1]}": c[0] for c in courses}
        course_cb['values'] = list(course_map.keys())
        instrs = fetch_all("SELECT instructor_id, name FROM Instructors ORDER BY name")
        instr_map = {f"{i[0]} - {i[1]}": i[0] for i in instrs}
        instr_cb['values'] = list(instr_map.keys())
        return student_map, course_map, instr_map
    student_map, course_map, instr_map = load_combos()
    def load():
        tree.delete(*tree.get_children())
        data = fetch_all("""
            SELECT r.result_id, s.name, c.course_name, i.name, r.grade
            FROM Result r
            LEFT JOIN Student s ON r.student_id=s.student_id
            LEFT JOIN Course c ON r.course_id=c.course_id
            LEFT JOIN Instructors i ON r.instructor_id=i.instructor_id
            ORDER BY r.result_id
        """)
        for r in data: tree.insert("", "end", values=r)
    def clear_form():
        student_cb.set(''); course_cb.set(''); instr_cb.set(''); grade_e.delete(0,tk.END)
    def add():
        s = student_cb.get(); c = course_cb.get(); i = instr_cb.get(); g = grade_e.get().strip()
        if not (s and c and i and g): messagebox.showwarning("Validation", "All fields required"); return
        sid = student_map.get(s); cid = course_map.get(c); iid = instr_map.get(i)
        run_query("INSERT INTO Result (student_id,course_id,grade,instructor_id) VALUES (?,?,?,?)", (sid,cid,g,iid))
        load(); clear_form()
    def on_select(e=None):
        sel = tree.focus();
        if not sel: return
        vals = tree.item(sel,'values')
        student_key = next((k for k,v in student_map.items() if v == fetch_student_id_by_name(vals[1])), '')
        course_key = next((k for k,v in course_map.items() if v == fetch_course_id_by_name(vals[2])), '')
        instr_key = next((k for k,v in instr_map.items() if v == fetch_instructor_id_by_name(vals[3])), '')
        if student_key: student_cb.set(student_key)
        if course_key: course_cb.set(course_key)
        if instr_key: instr_cb.set(instr_key)
        grade_e.delete(0,tk.END); grade_e.insert(0, vals[4] if vals[4] is not None else '')
    def fetch_student_id_by_name(name):
        if not name: return None
        r = fetch_all("SELECT student_id FROM Student WHERE name=?", (name,))
        return r[0][0] if r else None
    def fetch_course_id_by_name(name):
        if not name: return None
        r = fetch_all("SELECT course_id FROM Course WHERE course_name=?", (name,))
        return r[0][0] if r else None
    def fetch_instructor_id_by_name(name):
        if not name: return None
        r = fetch_all("SELECT instructor_id FROM Instructors WHERE name=?", (name,))
        return r[0][0] if r else None
    def update_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Select a result to update"); return
        rid = tree.item(sel,'values')[0]
        s = student_cb.get(); c = course_cb.get(); i = instr_cb.get(); g = grade_e.get().strip()
        if not (s and c and i and g): messagebox.showwarning("Validation", "All fields required"); return
        sid = student_map.get(s); cid = course_map.get(c); iid = instr_map.get(i)
        run_query("UPDATE Result SET student_id=?,course_id=?,grade=?,instructor_id=? WHERE result_id=?", (sid,cid,g,iid,rid))
        load(); clear_form()
    def delete_rec():
        sel = tree.focus()
        if not sel: messagebox.showwarning("Select","Select a result to delete"); return
        rid = tree.item(sel,'values')[0]
        if messagebox.askyesno("Confirm","Delete this result?"): run_query("DELETE FROM Result WHERE result_id=?", (rid,)); load(); clear_form()
    btnf = ttk.Frame(frm); btnf.pack(fill='x', pady=6)
    ttk.Button(btnf, text="Add", style='Primary.TButton', command=add).pack(side='left', padx=6)
    ttk.Button(btnf, text="Update", style='Success.TButton', command=update_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Delete", style='Danger.TButton', command=delete_rec).pack(side='left', padx=6)
    ttk.Button(btnf, text="Clear", command=clear_form).pack(side='left', padx=6)
    ttk.Button(btnf, text="Refresh Combos", command=lambda: refresh_maps()).pack(side='right', padx=6)
    ttk.Button(btnf, text="Refresh List", command=load).pack(side='right', padx=6)
    def refresh_maps():
        nonlocal student_map, course_map, instr_map
        student_map, course_map, instr_map = load_combos()
    tree.bind("<<TreeviewSelect>>", on_select); load()

# ------------------------- Main Login UI (match provided design)  -----------------------

root = tk.Tk(); root.title("NVIT - Management System")
center(root, 480, 460); root.configure(bg='#E3F2FD')
main = ttk.Frame(root, padding=16); main.pack(expand=True, fill='both')
ttk.Label(main, text="NVIT", style='Title.TLabel',font=("Helvetica", 20, "bold")).pack(pady=(10,2))
ttk.Label(main, text="New Vision Information Technology Limited", style='Sub.TLabel').pack(pady=(0,16))
group = ttk.Frame(main); group.pack(pady=6)
ttk.Label(group, text="Email", font=('Helvetica',10)).pack(anchor='w')
login_email = ttk.Entry(group, width=36); login_email.pack(pady=(0,8))
underline1 = tk.Frame(group, height=1, bg='#9bbbe6'); underline1.pack(fill='x', pady=(0,8))
ttk.Label(group, text="Password", font=('Helvetica',10)).pack(anchor='w', pady=(6,0))
login_password = ttk.Entry(group, width=36, show='*'); login_password.pack(pady=(0,8))
underline2 = tk.Frame(group, height=1, bg='#9bbbe6'); underline2.pack(fill='x', pady=(0,8))
btn_frame = tk.Frame(main, bg='#E3F2FD'); btn_frame.pack(pady=10)
login_btn = ttk.Button(btn_frame, text="Login", style='Primary.TButton', command=login_user); login_btn.pack(ipadx=20, ipady=6)
ttk.Button(main, text="Create Account", style='Secondary.TButton', command=open_register).pack(pady=(10,4))
ttk.Label(main, text="(Use Create Account to register first)", style='Sub.TLabel').pack(pady=(8,0))
root.mainloop()
