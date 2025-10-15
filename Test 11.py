import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB = "nvit_relational.db"

# -------------------------
# Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Course Table
    c.execute("""CREATE TABLE IF NOT EXISTS Course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        duration TEXT NOT NULL,
        course_price REAL
    )""")

    # Instructors Table
    c.execute("""CREATE TABLE IF NOT EXISTS Instructors (
        instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        father_name TEXT,
        mother_name TEXT,
        blood_group TEXT,
        mobile_no TEXT,
        expertise TEXT
    )""")

    # Student Table
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
        FOREIGN KEY(course_id) REFERENCES Course(course_id),
        FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id)
    )""")

    # Result Table
    c.execute("""CREATE TABLE IF NOT EXISTS Result (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        course_id INTEGER,
        course_name TEXT,
        grade TEXT,
        instructor_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES Student(student_id),
        FOREIGN KEY(course_id) REFERENCES Course(course_id),
        FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id)
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
# STUDENT CRUD
# -------------------------
def open_students():
    win = tk.Toplevel(root)
    win.title("Manage Students")
    win.geometry("950x600")

    # Form Fields
    labels = ["Name", "Father Name", "Mother Name", "Address", "Blood Group", "Mobile No", "Course", "Instructor", "Batch No"]
    entries = {}
    for i, lbl in enumerate(labels):
        tk.Label(win, text=lbl+":").grid(row=i, column=0, padx=10, pady=5, sticky='w')
        if lbl in ["Course", "Instructor"]:
            combo = ttk.Combobox(win, width=30)
            combo.grid(row=i, column=1)
            entries[lbl] = combo
        else:
            ent = tk.Entry(win, width=32)
            ent.grid(row=i, column=1)
            entries[lbl] = ent

    # Load Combobox Data
    def load_combos():
        courses = fetch_all("SELECT course_id, course_name FROM Course")
        course_dict = {c[1]: c[0] for c in courses}
        entries["Course"]["values"] = list(course_dict.keys())
        instructors = fetch_all("SELECT instructor_id, name FROM Instructors")
        instr_dict = {i[1]: i[0] for i in instructors}
        entries["Instructor"]["values"] = list(instr_dict.keys())
        return course_dict, instr_dict

    course_dict, instr_dict = load_combos()

    # Treeview
    cols = ("ID","Name","Father","Mother","Address","Blood","Mobile","Course","Instructor","Batch")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
    for c in cols: tree.heading(c, text=c); tree.column(c,width=100)
    tree.grid(row=10, column=0, columnspan=4, pady=20)

    def load_students():
        tree.delete(*tree.get_children())
        data = fetch_all("""
            SELECT s.student_id, s.name, s.father_name, s.mother_name, s.address, s.blood_group, s.mobile_no,
                   c.course_name, i.name, s.batch_no
            FROM Student s
            LEFT JOIN Course c ON s.course_id=c.course_id
            LEFT JOIN Instructors i ON s.instructor_id=i.instructor_id
        """)
        for row in data:
            tree.insert("", "end", values=row)

    def clear_form():
        for lbl, widget in entries.items():
            if lbl in ["Course","Instructor"]:
                widget.set('')
            else:
                widget.delete(0, tk.END)

    def add_student():
        name = entries["Name"].get().strip()
        fname = entries["Father Name"].get().strip()
        mname = entries["Mother Name"].get().strip()
        addr = entries["Address"].get().strip()
        bg = entries["Blood Group"].get().strip()
        mob = entries["Mobile No"].get().strip()
        course = entries["Course"].get()
        instr = entries["Instructor"].get()
        batch = entries["Batch No"].get().strip()
        cid = course_dict.get(course)
        iid = instr_dict.get(instr)
        if not name: return messagebox.showwarning("Error","Name required")
        run_query("INSERT INTO Student (name,father_name,mother_name,address,blood_group,mobile_no,course_id,instructor_id,batch_no) VALUES (?,?,?,?,?,?,?,?,?)",
                  (name,fname,mname,addr,bg,mob,cid,iid,batch))
        load_students(); clear_form()

    def update_student():
        sel = tree.focus()
        if not sel: return messagebox.showwarning("Error","Select a record")
        sid = tree.item(sel,"values")[0]
        name = entries["Name"].get().strip()
        fname = entries["Father Name"].get().strip()
        mname = entries["Mother Name"].get().strip()
        addr = entries["Address"].get().strip()
        bg = entries["Blood Group"].get().strip()
        mob = entries["Mobile No"].get().strip()
        course = entries["Course"].get()
        instr = entries["Instructor"].get()
        batch = entries["Batch No"].get().strip()
        cid = course_dict.get(course)
        iid = instr_dict.get(instr)
        run_query("UPDATE Student SET name=?,father_name=?,mother_name=?,address=?,blood_group=?,mobile_no=?,course_id=?,instructor_id=?,batch_no=? WHERE student_id=?",
                  (name,fname,mname,addr,bg,mob,cid,iid,batch,sid))
        load_students(); clear_form()

    def delete_student():
        sel = tree.focus()
        if not sel: return messagebox.showwarning("Error","Select a record")
        sid = tree.item(sel,"values")[0]
        if messagebox.askyesno("Confirm","Delete this student?"):
            run_query("DELETE FROM Student WHERE student_id=?",(sid,))
            load_students(); clear_form()

    def on_select(event):
        sel = tree.focus()
        if not sel: return
        vals = tree.item(sel,"values")
        entries["Name"].delete(0, tk.END); entries["Name"].insert(0, vals[1])
        entries["Father Name"].delete(0, tk.END); entries["Father Name"].insert(0, vals[2])
        entries["Mother Name"].delete(0, tk.END); entries["Mother Name"].insert(0, vals[3])
        entries["Address"].delete(0, tk.END); entries["Address"].insert(0, vals[4])
        entries["Blood Group"].delete(0, tk.END); entries["Blood Group"].insert(0, vals[5])
        entries["Mobile No"].delete(0, tk.END); entries["Mobile No"].insert(0, vals[6])
        entries["Course"].set(vals[7] or '')
        entries["Instructor"].set(vals[8] or '')
        entries["Batch No"].delete(0, tk.END); entries["Batch No"].insert(0, vals[9])

    # Buttons
    tk.Button(win, text="Add", bg="#0078D7", fg="white", width=12, command=add_student).grid(row=9,column=0,pady=10)
    tk.Button(win, text="Update", bg="#28a745", fg="white", width=12, command=update_student).grid(row=9,column=1,pady=10)
    tk.Button(win, text="Delete", bg="#dc3545", fg="white", width=12, command=delete_student).grid(row=9,column=2,pady=10)
    tk.Button(win, text="Clear", width=12, command=clear_form).grid(row=9,column=3,pady=10)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_students()

# -------------------------
# MAIN UI
# -------------------------
root = tk.Tk()
root.title("NVIT Management System")
root.geometry("400x300")
root.config(bg="white")

tk.Label(root,text="NVIT Management System",font=("Arial",16,"bold"),bg="white").pack(pady=20)
tk.Button(root,text="Manage Students",width=25,bg="#0078D7",fg="white",command=open_students).pack(pady=10)

root.mainloop()
