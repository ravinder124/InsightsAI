import sqlite3
import bcrypt
import os
from datetime import datetime

def init_db():
    """Initialize the database with users and user_queries tables"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_queries table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            inquiry_type TEXT NOT NULL,
            message TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    return conn

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(username, email, password):
    """Create a new user account"""
    try:
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      (username, email, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def user_exists(username, email):
    """Check if a user already exists"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_password = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    return False

def get_user(username):
    conn = get_db_connection()
    cur = conn.execute('SELECT id, username FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    return user 

def save_contact_query(first_name, last_name, email, inquiry_type, message):
    """Save a contact form submission to the database"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_queries (first_name, last_name, email, inquiry_type, message) 
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, inquiry_type, message))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving contact query: {e}")
        return False

def get_all_contact_queries():
    """Get all contact form submissions (for admin purposes)"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_queries ORDER BY submitted_at DESC')
        queries = cursor.fetchall()
        conn.close()
        return queries
    except Exception as e:
        print(f"Error fetching contact queries: {e}")
        return []

# Initialize database when module is imported
init_db() 