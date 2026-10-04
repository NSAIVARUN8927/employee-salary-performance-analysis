import hashlib
import hmac
import os
import re
import sqlite3

from .database import get_conn, init_db, log_activity


def _hash(password, salt_hex):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000).hex()


def register(username, email, full_name, password):
    username, email = username.strip(), email.strip().lower()
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        return False, "Username must be 3-20 characters: letters, numbers or underscores."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    init_db()
    salt = os.urandom(16).hex()
    try:
        with get_conn() as c:
            role = "admin" if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0 else "user"
            cur = c.execute("INSERT INTO users(username, email, full_name, password_hash, salt, role) VALUES (?,?,?,?,?,?)",
                            (username, email, full_name.strip(), _hash(password, salt), salt, role))
        log_activity(cur.lastrowid, "registered")
        return True, "Account created. You can now sign in."
    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."


def login(username, password):
    init_db()
    with get_conn() as c:
        row = c.execute("SELECT * FROM users WHERE username=?", (username.strip(),)).fetchone()
    if row and hmac.compare_digest(row["password_hash"], _hash(password, row["salt"])):
        log_activity(row["id"], "signed in")
        return dict(row)
    return None
