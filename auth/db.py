"""
auth/db.py — User authentication DB utilities for SAP Warehouse Agent.

Handles all user-related database operations:
  - Users table initialisation
  - Account creation with bcrypt password hashing
  - Credential verification with constant-time comparison

This module is intentionally Streamlit-free so it can be tested or
reused independently of the UI layer.
"""

import sqlite3

import bcrypt

# Shared DB path — must match the path used by the LangGraph checkpointer
DB_PATH = "checkpoints.db"


# ---------------------------------------------------------------------------
# Table management
# ---------------------------------------------------------------------------

def init_users_table() -> None:
    """Creates the `users` table in SQLite if it does not already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

def user_exists(username: str) -> bool:
    """Returns True if an account with the given email already exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username.lower().strip(),),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_user(username: str, password: str) -> None:
    """
    Hashes `password` with bcrypt and inserts a new user row.

    Raises:
        sqlite3.IntegrityError: if the username (email) is already registered.
    """
    hashed = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username.lower().strip(), hashed),
    )
    conn.commit()
    conn.close()


def verify_user(username: str, password: str) -> bool:
    """
    Returns True if `username` exists and `password` matches the stored hash.

    Uses bcrypt.checkpw for a constant-time comparison that resists
    timing-based attacks even in a local deployment.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username.lower().strip(),),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    return bcrypt.checkpw(password.encode("utf-8"), row[0].encode("utf-8"))
