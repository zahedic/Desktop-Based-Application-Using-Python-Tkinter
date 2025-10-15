import sqlite3
from datetime import date

DB_FILE = "SDB.db"

def create_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    # -------------------------
    # 1) students table
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        dob DATE,                 -- Date of birth (YYYY-MM-DD)
        created_at DATE DEFAULT (DATE('now'))
    );
    """)

    # -------------------------
    # 2) instructors table
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instructors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        specialization TEXT,
        hired_at DATE DEFAULT (DATE('now'))
    );
    """)

    # -------------------------
    # 3) courses table
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,     -- e.g., NVIT-PY-01
        title TEXT NOT NULL,
        description TEXT,
        duration_weeks INTEGER,        -- course length
        fee REAL,
        instructor_id INTEGER,         -- FK to instructors
        created_at DATE DEFAULT (DATE('now')),
        FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL ON UPDATE CASCADE
    );
    """)

    # -------------------------
    # 4) enrollments table (relationship: student <-> course)
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enroll_date DATE DEFAULT (DATE('now')),
        status TEXT DEFAULT 'enrolled',  -- enrolled, completed, dropped
        grade TEXT,                       -- optional
        UNIQUE(student_id, course_id),    -- prevent duplicate enrollments
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    # optional: indexes for faster lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_enroll_student ON enrollments(student_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_enroll_course ON enrollments(course_id);")

    conn.commit()
    conn.close()
    print("✅ Database and tables created (or already existed).")

def insert_sample_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # --- instructors sample ---
    instructors = [
        ("Md. Rahim", "rahim@nvit.bd", "01710000001", "Python"),
        ("Ms. Farhana", "farhana@nvit.bd", "01710000002", "Web Development"),
        ("Mr. Karim", "karim@nvit.bd", "01710000003", "Graphic Design")
    ]
    # insert ignoring duplicates by email
    for name, email, phone, spec in instructors:
        try:
            cur.execute("INSERT INTO instructors (name, email, phone, specialization) VALUES (?, ?, ?, ?)",
                        (name, email, phone, spec))
        except sqlite3.IntegrityError:
            pass

    # --- courses sample (link instructor by email lookup) ---
    # find instructor ids
    cur.execute("SELECT id, email FROM instructors")
    instr_map = {email: id_ for (id_, email) in cur.fetchall()}

    courses = [
        ("NVIT-PY-01", "Python for Beginners", "Basic Python programming", 8, 120.0, instr_map.get("rahim@nvit.bd")),
        ("NVIT-WD-01", "Web Development (HTML/CSS/JS)", "Frontend web basics", 6, 100.0, instr_map.get("farhana@nvit.bd")),
        ("NVIT-PS-01", "Photoshop Basics", "Fundamentals of Photoshop", 4, 80.0, instr_map.get("karim@nvit.bd"))
    ]
    for code, title, desc, weeks, fee, instr_id in courses:
        try:
            cur.execute("""INSERT INTO courses (code, title, description, duration_weeks, fee, instructor_id)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (code, title, desc, weeks, fee, instr_id))
        except sqlite3.IntegrityError:
            pass

    # --- students sample ---
    students = [
        ("Md", "Zahedul", "zahed@nvit.bd", "01975000001", "2005-03-15"),
        ("Jawad", "Islam", "jawad@nvit.bd", "01975000002", "2012-01-10"),
        ("Rina", "Akter", "rina@nvit.bd", "01975000003", "1998-07-22")
    ]
    for fn, ln, email, phone, dob in students:
        try:
            cur.execute("INSERT INTO students (first_name, last_name, email, phone, dob) VALUES (?, ?, ?, ?, ?)",
                        (fn, ln, email, phone, dob))
        except sqlite3.IntegrityError:
            pass

    # --- enrollments sample: link by student email / course code ---
    # get student ids and course ids
    cur.execute("SELECT id, email FROM students")
    student_map = {email: id_ for (id_, email) in cur.fetchall()}
    cur.execute("SELECT id, code FROM courses")
    course_map = {code: id_ for (id_, code) in cur.fetchall()}

    enrolls = [
        ("zahed@nvit.bd", "NVIT-PY-01", "enrolled"),
        ("jawad@nvit.bd", "NVIT-WD-01", "enrolled"),
        ("rina@nvit.bd", "NVIT-PS-01", "enrolled"),
        ("zahed@nvit.bd", "NVIT-WD-01", "enrolled")
    ]
    for s_email, c_code, status in enrolls:
        sid = student_map.get(s_email)
        cid = course_map.get(c_code)
        if sid and cid:
            try:
                cur.execute("INSERT INTO enrollments (student_id, course_id, status) VALUES (?, ?, ?)",
                            (sid, cid, status))
            except sqlite3.IntegrityError:
                pass  # duplicate enrollment ignored

    conn.commit()
    conn.close()
    print("✅ Sample data inserted (duplicates ignored).")

def demo_queries():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    print("\n-- All Students --")
    cur.execute("SELECT id, first_name, last_name, email FROM students")
    for row in cur.fetchall():
        print(row)

    print("\n-- Courses with Instructor Name --")
    cur.execute("""
        SELECT c.id, c.code, c.title, i.name as instructor
        FROM courses c
        LEFT JOIN instructors i ON c.instructor_id = i.id
    """)
    for row in cur.fetchall():
        print(row)

    print("\n-- Enrollments (student -> course) --")
    cur.execute("""
        SELECT e.id, s.first_name || ' ' || s.last_name as student, c.title as course, e.enroll_date, e.status
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
    """)
    for row in cur.fetchall():
        print(row)

    # example: get students in Python course
    print("\n-- Students enrolled in 'Python for Beginners' --")
    cur.execute("""
        SELECT s.id, s.first_name, s.email
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        WHERE c.code = ?
    """, ("NVIT-PY-01",))
    for row in cur.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    create_database()
    insert_sample_data()
    demo_queries()
