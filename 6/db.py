import sqlite3
import hashlib

DB_NAME = "library.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            year INTEGER,
            genre TEXT,
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(login, password):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (login, password_hash) VALUES (?, ?)",
                    (login, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(login, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE login=?", (login,))
    row = cur.fetchone()
    conn.close()
    return row is not None and row[0] == hash_password(password)