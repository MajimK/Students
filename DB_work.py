import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Nombre TEXT NOT NULL,
                        EvoPoints INTEGER
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )''')
    
    try:
        default_pass = hashlib.sha256("admin123".encode()).hexdigest()  
        cursor.execute("INSERT INTO teachers (username, password) VALUES (?, ?)", 
                       ("admin", default_pass))
    except sqlite3.IntegrityError:
        pass  # El usuario ya existe
    conn.commit()
    conn.close()

def Verify_teacher(username, password):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest() 
    cursor.execute("SELECT * FROM teachers WHERE username = ? AND password = ?",(username,hashed_pass))
    teacher = cursor.fetchone()
    conn.close()
    return teacher is not None

def update_teacher_credentials(old_username, new_username, new_password):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(new_password.encode()).hexdigest()
    try:
        cursor.execute("UPDATE teachers SET username = ?, password = ? WHERE username = ?",
                      (new_username, hashed_pass, old_username))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  
    finally:
        conn.close()

def get_current_teacher():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM teachers LIMIT 1")
    teacher = cursor.fetchone()
    conn.close()
    return teacher[0] if teacher else None


def Agregate_columns(column_name):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(students)")
    existing_columns = [row[1] for row in cursor.fetchall()]  

    if column_name not in existing_columns:
        try:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {column_name} INTEGER")
            conn.commit()
        except sqlite3.OperationalError as e:
            pass
    conn.close()

def get_table_columns():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns[1:]


def get_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY EvoPoints DESC")
    students = cursor.fetchall()
    conn.close()
    return students

def add_student(name):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (Nombre, EvoPoints) VALUES (?, 0)", (name,))
    conn.commit()
    conn.close()

def update_points(student_id, points):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET EvoPoints = ? WHERE id = ?", (points, student_id))
    conn.commit()
    conn.close()

def clear_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='students'")  # Reinicia el autoincrement
    conn.commit()
    conn.close()