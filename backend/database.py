import os
import sqlite3
import io
import uuid
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "app.db")

SCHEMA = """
CREATE TABLE Department(
    Department_ID TEXT PRIMARY KEY NOT NULL,
    Department_Name TEXT NOT NULL UNIQUE,
    Location TEXT);
CREATE TABLE Employee(
    Employee_ID TEXT PRIMARY KEY NOT NULL,
    Name TEXT NOT NULL,
    Age INTEGER CHECK (Age IS NULL OR Age BETWEEN 18 AND 70),
    Gender TEXT,
    Designation TEXT,
    Experience_Years INTEGER CHECK (Experience_Years >= 0),
    Joining_Year INTEGER,
    Department_ID TEXT REFERENCES Department(Department_ID));
CREATE TABLE Salary(
    Salary_ID TEXT PRIMARY KEY NOT NULL,
    Employee_ID TEXT NOT NULL REFERENCES Employee(Employee_ID),
    Basic_Salary REAL CHECK (Basic_Salary > 0),
    Bonus REAL DEFAULT 0,
    Total_Salary REAL,
    Effective_Date TEXT);
CREATE TABLE Performance(
    Performance_ID TEXT PRIMARY KEY NOT NULL,
    Employee_ID TEXT NOT NULL REFERENCES Employee(Employee_ID),
    Performance_Score REAL CHECK (Performance_Score BETWEEN 0 AND 5),
    Review_Date TEXT);
"""

USERS = """
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_log(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploaded_files(
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_data BLOB NOT NULL,
    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")

    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(USERS)
   


def is_seeded():
    with get_conn() as c:
        return c.execute("SELECT 1 FROM sqlite_master WHERE name='Employee'").fetchone() is not None
def seed_database(d):
    nz = lambda v, f=float: None if pd.isna(v) else f(v)
    ids = {n: f"D{i:02d}" for i, n in enumerate(sorted(d["Department"].unique()), 1)}
    emp, sal, perf = [], [], []
    for i, r in enumerate(d.itertuples(index=False), 1):
        emp.append((r.Employee_ID, str(r.Name), nz(r.Age, int), str(r.Gender), str(r.Designation),
                    nz(r.Experience_Years, int), nz(r.Joining_Year, int), ids[r.Department]))
        sal.append((f"S{i:03d}", r.Employee_ID, float(r.Basic_Salary), float(r.Bonus), float(r.Total_Salary), nz(r.Effective_Date, str)))
        perf.append((f"P{i:03d}", r.Employee_ID, float(r.Performance_Score), None))
    with get_conn() as c:
        c.executescript("DROP TABLE IF EXISTS Performance; DROP TABLE IF EXISTS Salary; DROP TABLE IF EXISTS Employee; DROP TABLE IF EXISTS Department;" + SCHEMA)
        c.executemany("INSERT INTO Department VALUES (?,?,?)", [(i, n, None) for n, i in ids.items()])
        c.executemany("INSERT INTO Employee VALUES (?,?,?,?,?,?,?,?)", emp)
        c.executemany("INSERT INTO Salary VALUES (?,?,?,?,?,?)", sal)
        c.executemany("INSERT INTO Performance VALUES (?,?,?,?)", perf)
def run_query(sql, params=()):
    with get_conn() as c:
        c.execute("PRAGMA query_only = ON")
        return pd.read_sql_query(sql, c, params=params)


def employee_frame():
    return run_query("""
        SELECT e.Employee_ID, e.Name, e.Age, e.Gender, e.Designation, e.Experience_Years, e.Joining_Year,
               d.Department_Name AS Department, s.Basic_Salary, s.Bonus, s.Total_Salary, p.Performance_Score
        FROM Employee e
        JOIN Department d ON e.Department_ID = d.Department_ID
        JOIN Salary s ON e.Employee_ID = s.Employee_ID
        JOIN Performance p ON e.Employee_ID = p.Employee_ID
        ORDER BY e.Employee_ID""")
def log_activity(user_id, action):
    with get_conn() as c:
        c.execute("INSERT INTO activity_log(user_id, action) VALUES (?, ?)", (user_id, action))


def add_employee(e):
    with get_conn() as c:
        row = c.execute("SELECT Department_ID FROM Department WHERE Department_Name=?", (e["Department"],)).fetchone()
        eid = e["Employee_ID"].strip()
        c.execute("INSERT INTO Employee VALUES (?,?,?,?,?,?,?,?)", (eid, e["Name"].strip(), int(e["Age"]), e["Gender"],
                  e["Designation"].strip(), int(e["Experience_Years"]), int(e["Joining_Year"]), row[0]))
        c.execute("INSERT INTO Salary VALUES (?,?,?,?,?,?)", ("S_" + eid, eid, float(e["Basic_Salary"]), float(e["Bonus"]),
                  float(e["Basic_Salary"]) + float(e["Bonus"]), None))
        c.execute("INSERT INTO Performance VALUES (?,?,?,?)", ("P_" + eid, eid, float(e["Performance_Score"]), None))


def delete_employee(emp_id):
    with get_conn() as c:
        for t in ("Performance", "Salary", "Employee"):
            c.execute(f"DELETE FROM {t} WHERE Employee_ID=?", (emp_id,))

def save_uploaded_file(user_id, filename, file_bytes):
    """Save a user's uploaded CSV file and return its unique ID."""

    if user_id is None:
        raise ValueError("Please log in before uploading a dataset.")

    if not filename:
        raise ValueError("The uploaded file has no filename.")

    if not filename.lower().endswith(".csv"):
        raise ValueError("Only CSV files are supported.")

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    file_id = str(uuid.uuid4())

    with get_conn() as conn:
        user_exists = conn.execute(
            "SELECT 1 FROM users WHERE id = ?",
            (int(user_id),)
        ).fetchone()

        if user_exists is None:
            raise ValueError("The logged-in user could not be verified.")

        conn.execute(
            """
            INSERT INTO uploaded_files
                (id, user_id, filename, file_data)
            VALUES (?, ?, ?, ?)
            """,
            (
                file_id,
                int(user_id),
                os.path.basename(filename),
                sqlite3.Binary(file_bytes),
            ),
        )

    return file_id


def list_uploaded_files(user_id):
    """List only the files belonging to the logged-in user."""

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, filename, uploaded_at
            FROM uploaded_files
            WHERE user_id = ?
            ORDER BY uploaded_at DESC, rowid DESC
            """,
            (int(user_id),)
        ).fetchall()

    return [dict(row) for row in rows]


def get_uploaded_file(user_id, file_id):
    """Retrieve a file only when it belongs to the specified user."""

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT filename, file_data
            FROM uploaded_files
            WHERE id = ? AND user_id = ?
            """,
            (str(file_id), int(user_id))
        ).fetchone()

    if row is None:
        return None

    return {
        "filename": row["filename"],
        "file_data": bytes(row["file_data"]),
    }


def delete_uploaded_file(user_id, file_id):
    """Delete only the specified user's uploaded file."""

    with get_conn() as conn:
        cursor = conn.execute(
            """
            DELETE FROM uploaded_files
            WHERE id = ? AND user_id = ?
            """,
            (str(file_id), int(user_id))
        )

        return cursor.rowcount > 0
def recent_activity(limit=50):
    with get_conn() as c:
        q = "SELECT u.username, a.action, a.created_at FROM activity_log a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT ?"
        return [dict(r) for r in c.execute(q, (limit,))]
