import sqlite3
import hashlib
import os
import datetime

# --- DATABASE SETUP ---
DB_FILE = "user_data.db"

def make_hashes(password):
    """Hashes a password using SHA256 for secure storage."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Checks if a plain text password matches its hashed version."""
    return make_hashes(password) == hashed_text

def create_connection():
    """Establishes a connection to the SQLite database file."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
    return conn

def create_tables():
    """Creates all necessary tables if they don't already exist."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            # User table
            c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            ''')
            # PDF table
            c.execute('''
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE
            )
            ''')
            # --- NEW: Feedback table ---
            c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                feedback INTEGER NOT NULL -- 1 for thumbs up, -1 for thumbs down
            )
            ''')
            # --- END NEW ---
            conn.commit()

            # Add default admin
            c.execute("SELECT * FROM users WHERE username = 'admin'")
            if not c.fetchone():
                hashed_password = make_hashes('admin')
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          ('admin', hashed_password, 'admin'))
                conn.commit()

        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

def add_user(username, password, role="student"):
    """Adds a new user to the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            hashed_password = make_hashes(password)
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, hashed_password, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            conn.close()

def get_user(username):
    """Retrieves a user's data from the database by their username."""
    conn = create_connection()
    user_data = None
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_data = c.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
        finally:
            conn.close()
    return user_data

def add_pdf_record(filename):
    """Adds a record of a processed PDF to the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("INSERT INTO pdfs (filename) VALUES (?)", (filename,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

def is_pdf_processed(filename):
    """Checks if a PDF has already been processed and logged in the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("SELECT 1 FROM pdfs WHERE filename = ?", (filename,))
            return c.fetchone() is not None
        finally:
            conn.close()
    return False

def get_all_pdfs():
    """Retrieves the names of all processed PDF files, ordered alphabetically."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("SELECT filename FROM pdfs ORDER BY filename ASC")
            return c.fetchall()
        finally:
            conn.close()
    return []

def get_all_students():
    """Retrieves the usernames of all users with the 'student' role."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE role = 'student' ORDER BY username ASC")
            return c.fetchall()
        finally:
            conn.close()
    return []

def delete_user(username):
    """Deletes a user from the database by their username."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()

def clear_all_pdfs():
    """Deletes all records from the 'pdfs' table."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("DELETE FROM pdfs")
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing PDF records: {e}")
            return False
        finally:
            conn.close()

# --- NEW: Function to add feedback ---
def add_feedback(username, query, response, feedback):
    """Adds a feedback record to the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO feedback (timestamp, username, query, response, feedback) VALUES (?, ?, ?, ?, ?)",
                      (timestamp, username, query, response, feedback))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding feedback: {e}")
            return False
        finally:
            conn.close()
