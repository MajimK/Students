import sqlite3
import hashlib

import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Grupo TEXT NOT NULL,
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
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest() 
    cursor.execute("SELECT * FROM teachers WHERE username = ? AND password = ?",(username,hashed_pass))
    teacher = cursor.fetchone()
    conn.close()
    return teacher is not None

def update_teacher_credentials(old_username, new_username, new_password):
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM teachers LIMIT 1")
    teacher = cursor.fetchone()
    conn.close()
    return teacher[0] if teacher else None


def Agregate_columns(column_name):
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns[1:]


def get_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY EvoPoints DESC")
    students = cursor.fetchall()
    conn.close()
    return students

def add_student(group, name):
    if name:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE Nombre = ?", (name,))
        existing = cursor.fetchone()
        
        if not existing: 
            cursor.execute("INSERT INTO students (Grupo, Nombre, EvoPoints) VALUES (?, ?, 0)", 
                          (group, name))
            conn.commit()
            conn.close()
            return True
        return False

def update_points(student_id, points):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET EvoPoints = ? WHERE id = ?", (points, student_id))
    conn.commit()
    conn.close()

def clear_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='students'")  # Reinicia el autoincrement
    conn.commit()
    conn.close()

def remove_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?",(student_id,))
    conn.commit()
    conn.close()

def update_student(name,student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET Nombre = ? WHERE id = ?", (name,student_id,))
    conn.commit()
    conn.close()
