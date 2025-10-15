import sqlite3
from tkinter import *
from tkinter import messagebox

# ---------- Database Setup ----------
conn = sqlite3.connect("nvit.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    duration TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS instructors (
    instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    enroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    instructor_id INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id),
    FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id)
)
""")

conn.commit()

# ---------- Tkinter GUI Setup ----------
root = Tk()
root.title("NVIT Management System")
root.geometry("500x500")
root.config(bg="#eaf4fc")

title = Label(root, text="🎓 NVIT Management System", font=("Arial", 18, "bold"), bg="#eaf4fc", fg="#003366")
title.pack(pady=10)

# ---------- Input Section ----------
frame = Frame(root, bg="#eaf4fc")
frame.pack(pady=10)

Label(frame, text="Student Name:", bg="#eaf4fc").grid(row=0, column=0, padx=10, pady=5, sticky=E)
Label(frame, text="Email:", bg="#eaf4fc").grid(row=1, column=0, padx=10, pady=5, sticky=E)
Label(frame, text="Course Name:", bg="#eaf4fc").grid(row=2, column=0, padx=10, pady=5, sticky=E)
Label(frame, text="Instructor Name:", bg="#eaf4fc").grid(row=3, column=0, padx=10, pady=5, sticky=E)

entry_student = Entry(frame, width=30)
entry_email = Entry(frame, width=30)
entry_course = Entry(frame, width=30)
entry_instructor = Entry(frame, width=30)

entry_student.grid(row=0, column=1, padx=10, pady=5)
entry_email.grid(row=1, column=1, padx=10, pady=5)
entry_course.grid(row=2, column=1, padx=10, pady=5)
entry_instructor.grid(row=3, column=1, padx=10, pady=5)

# ---------- Functions ----------
def add_data():
    student = entry_student.get()
    email = entry_email.get()
    course = entry_course.get()
    instructor = entry_instructor.get()

    if student == "" or email == "" or course == "" or instructor == "":
        messagebox.showwarning("Input Error", "Please fill all fields!")
        return

    try:
        # Insert student
        cursor.execute("INSERT INTO students (name, email) VALUES (?, ?)", (student, email))
        student_id = cursor.lastrowid

        # Insert course
        cursor.execute("INSERT INTO courses (course_name, duration) VALUES (?, ?)", (course, "3 Months"))
        course_id = cursor.lastrowid

        # Insert instructor
        cursor.execute("INSERT INTO instructors (name, subject) VALUES (?, ?)", (instructor, course))
        instructor_id = cursor.lastrowid

        # Enroll student
        cursor.execute("INSERT INTO enrollments (student_id, course_id, instructor_id) VALUES (?, ?, ?)",
                       (student_id, course_id, instructor_id))

        conn.commit()
        messagebox.showinfo("Success", "Student enrolled successfully!")

        entry_student.delete(0, END)
        entry_email.delete(0, END)
        entry_course.delete(0, END)
        entry_instructor.delete(0, END)

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "This email already exists!")

def show_data():
    cursor.execute("""
        SELECT s.name, s.email, c.course_name, i.name
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        JOIN instructors i ON e.instructor_id = i.instructor_id
    """)
    records = cursor.fetchall()

    if len(records) == 0:
        messagebox.showinfo("Info", "No data found!")
    else:
        info = ""
        for row in records:
            info += f"Student: {row[0]} | Email: {row[1]}\nCourse: {row[2]} | Instructor: {row[3]}\n\n"
        messagebox.showinfo("Enrollment List", info)

# ---------- Buttons ----------
btn_add = Button(root, text="Add Enrollment", command=add_data, bg="#007acc", fg="white", width=20)
btn_show = Button(root, text="Show All", command=show_data, bg="#009933", fg="white", width=20)

btn_add.pack(pady=10)
btn_show.pack(pady=10)

root.mainloop()
