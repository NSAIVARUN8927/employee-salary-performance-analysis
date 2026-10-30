import hashlib
import hmac
import os
import re
import sqlite3

from .database import get_conn, init_db, log_activity


def _hash(password, salt_hex):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), 200_000
    ).hex()


def get_user(login_id):
    """Return a local user by username or email, without checking a password."""
    init_db()
    login_id = (login_id or "").strip()
    if not login_id:
        return None

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (login_id, login_id.lower()),
        ).fetchone()
    return dict(row) if row else None


def record_login(user):
    """Record a successful Firebase-authenticated login in the local activity log."""
    if user and user.get("id") is not None:
        log_activity(user["id"], "signed in")


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
        with get_conn() as conn:
            role = "admin" if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0 else "user"
            cur = conn.execute(
                "INSERT INTO users(username, email, full_name, password_hash, salt, role) VALUES (?,?,?,?,?,?)",
                (username, email, full_name.strip(), _hash(password, salt), salt, role),
            )
        log_activity(cur.lastrowid, "registered")
        return True, "Account created. You can now sign in."
    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."


def login(username, password):
    init_db()
    user = get_user(username)
    if user and hmac.compare_digest(
        user["password_hash"], _hash(password, user["salt"])
    ):
        log_activity(user["id"], "signed in")
        return user
    return None
