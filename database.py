import sqlite3
import os
from pathlib import Path
import hashlib
import json
from datetime import datetime

# Create database directory if it doesn't exist
db_dir = Path("data")
db_dir.mkdir(parents=True, exist_ok=True)

DB_PATH = db_dir / "users.db"

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            company TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        print(f"Database initialized successfully at {DB_PATH}")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(name, email, password, company=None):
    """Create a new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, company) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), company)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        raise ValueError("Email already registered")
    finally:
        conn.close()

def verify_user(email, password):
    """Verify user credentials and return user data if valid"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, name, email, company FROM users WHERE email = ? AND password_hash = ?",
            (email, hash_password(password))
        )
        user = cursor.fetchone()
        
        if user:
            # Update last login time
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user[0],)
            )
            conn.commit()
            
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "company": user[3]
            }
        return None
    finally:
        conn.close()

def create_session(user_id, token, expires_at):
    """Create a new session for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires_at)
        )
        conn.commit()
    finally:
        conn.close()

def get_user_by_token(token):
    """Get user data from a valid session token"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.company 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
        """, (token,))
        
        user = cursor.fetchone()
        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "company": user[3]
            }
        return None
    finally:
        conn.close()

def delete_session(token):
    """Delete a session token"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()

def cleanup_expired_sessions():
    """Remove expired sessions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
        conn.commit()
    finally:
        conn.close()

# Initialize database on module import
init_db() 