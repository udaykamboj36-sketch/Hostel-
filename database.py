"""
database.py - SQLite database setup and all CRUD operations
for Hostel Management System
"""

import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "hostel.db"


def get_connection():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────

def init_db():
    """Create all tables if they don't exist and seed sample data."""
    conn = get_connection()
    c = conn.cursor()

    # Rooms table
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT    NOT NULL UNIQUE,
            capacity    INTEGER NOT NULL DEFAULT 2,
            occupied    INTEGER NOT NULL DEFAULT 0,
            floor       INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Students table
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id     TEXT    NOT NULL UNIQUE,
            name           TEXT    NOT NULL,
            room_number    TEXT,
            contact        TEXT,
            email          TEXT,
            course         TEXT,
            join_date      TEXT,
            status         TEXT    NOT NULL DEFAULT 'Inside',
            FOREIGN KEY (room_number) REFERENCES rooms(room_number)
        )
    """)

    # Attendance table
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Present',
            marked_at   TEXT    NOT NULL,
            UNIQUE (student_id, date)
        )
    """)

    # Complaints table
    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT    NOT NULL,
            student_name TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            description  TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'Pending',
            created_at   TEXT    NOT NULL,
            updated_at   TEXT
        )
    """)

    # Entry/Exit logs table (approval-based)
    c.execute("""
        CREATE TABLE IF NOT EXISTS entry_exit_logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT    NOT NULL,
            student_name TEXT    NOT NULL,
            action       TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'Pending',
            reason       TEXT,
            timestamp    TEXT    NOT NULL,
            reviewed_at  TEXT,
            reviewed_by  TEXT
        )
    """)

    # Admin table
    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    _seed_admin()
    _seed_sample_data()


def _seed_admin():
    """Insert default admin if not exists."""
    conn = get_connection()
    c = conn.cursor()
    pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)",
              ("admin", pw))
    conn.commit()
    conn.close()


def _seed_sample_data():
    """Insert sample rooms and students if tables are empty."""
    conn = get_connection()
    c = conn.cursor()

    # Seed rooms
    room_count = c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    if room_count == 0:
        rooms = [
            ("101", 2, 0, 1), ("102", 2, 0, 1), ("103", 3, 0, 1),
            ("201", 2, 0, 2), ("202", 2, 0, 2), ("203", 3, 0, 2),
            ("301", 4, 0, 3), ("302", 2, 0, 3),
        ]
        c.executemany(
            "INSERT INTO rooms (room_number, capacity, occupied, floor) VALUES (?,?,?,?)",
            rooms
        )

    # Seed students
    student_count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if student_count == 0:
        students = [
            ("STU001", "Arjun Sharma",    "101", "9876543210", "arjun@college.edu",   "B.Tech CSE", "2024-01-10", "Inside"),
            ("STU002", "Priya Patel",     "101", "9876543211", "priya@college.edu",   "B.Tech ECE", "2024-01-12", "Inside"),
            ("STU003", "Rahul Verma",     "102", "9876543212", "rahul@college.edu",   "BCA",        "2024-02-01", "Outside"),
            ("STU004", "Sneha Gupta",     "102", "9876543213", "sneha@college.edu",   "MBA",        "2024-02-05", "Inside"),
            ("STU005", "Vikram Singh",    "201", "9876543214", "vikram@college.edu",  "B.Sc Maths", "2024-03-01", "Inside"),
            ("STU006", "Kavya Reddy",     "202", "9876543215", "kavya@college.edu",   "B.Tech IT",  "2024-03-10", "Inside"),
        ]
        c.executemany(
            """INSERT INTO students
               (student_id, name, room_number, contact, email, course, join_date, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            students
        )
        # Update room occupancy
        for s in students:
            c.execute(
                "UPDATE rooms SET occupied = occupied + 1 WHERE room_number = ?",
                (s[2],)
            )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# ADMIN AUTH
# ─────────────────────────────────────────────

def verify_admin(username: str, password: str) -> bool:
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM admins WHERE username=? AND password=?",
        (username, pw_hash)
    ).fetchone()
    conn.close()
    return row is not None


# ─────────────────────────────────────────────
# ROOM OPERATIONS
# ─────────────────────────────────────────────

def get_all_rooms():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms ORDER BY room_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_room(room_number: str, capacity: int, floor: int):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO rooms (room_number, capacity, occupied, floor) VALUES (?,?,0,?)",
            (room_number, capacity, floor)
        )
        conn.commit()
        return True, "Room added successfully."
    except sqlite3.IntegrityError:
        return False, "Room number already exists."
    finally:
        conn.close()


def delete_room(room_number: str):
    conn = get_connection()
    occupied = conn.execute(
        "SELECT occupied FROM rooms WHERE room_number=?", (room_number,)
    ).fetchone()
    if occupied and occupied["occupied"] > 0:
        conn.close()
        return False, "Cannot delete an occupied room."
    conn.execute("DELETE FROM rooms WHERE room_number=?", (room_number,))
    conn.commit()
    conn.close()
    return True, "Room deleted."


def get_available_room():
    """Return first room with free capacity."""
    conn = get_connection()
    row = conn.execute(
        "SELECT room_number FROM rooms WHERE occupied < capacity ORDER BY room_number LIMIT 1"
    ).fetchone()
    conn.close()
    return row["room_number"] if row else None


# ─────────────────────────────────────────────
# STUDENT OPERATIONS
# ─────────────────────────────────────────────

def get_all_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_by_id(student_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE student_id=?", (student_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_student(student_id, name, contact, email, course, join_date, room_number=None):
    conn = get_connection()
    # Auto-assign room if not provided
    if not room_number:
        room_number = get_available_room()
        if not room_number:
            conn.close()
            return False, "No rooms available. Please add more rooms."

    # Check room capacity
    room = conn.execute(
        "SELECT capacity, occupied FROM rooms WHERE room_number=?", (room_number,)
    ).fetchone()
    if not room:
        conn.close()
        return False, "Room not found."
    if room["occupied"] >= room["capacity"]:
        conn.close()
        return False, f"Room {room_number} is full."

    try:
        conn.execute(
            """INSERT INTO students
               (student_id, name, room_number, contact, email, course, join_date, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (student_id, name, room_number, contact, email, course, join_date, "Inside")
        )
        conn.execute(
            "UPDATE rooms SET occupied = occupied + 1 WHERE room_number = ?",
            (room_number,)
        )
        conn.commit()
        return True, f"Student added and assigned to Room {room_number}."
    except sqlite3.IntegrityError:
        return False, "Student ID already exists."
    finally:
        conn.close()


def update_student(student_id, name, contact, email, course):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET name=?, contact=?, email=?, course=? WHERE student_id=?",
        (name, contact, email, course, student_id)
    )
    conn.commit()
    conn.close()
    return True, "Student updated."


def delete_student(student_id: str):
    conn = get_connection()
    student = conn.execute(
        "SELECT room_number FROM students WHERE student_id=?", (student_id,)
    ).fetchone()
    if student and student["room_number"]:
        conn.execute(
            "UPDATE rooms SET occupied = MAX(0, occupied - 1) WHERE room_number=?",
            (student["room_number"],)
        )
    conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    conn.commit()
    conn.close()
    return True, "Student deleted."


def update_student_status(student_id: str, status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET status=? WHERE student_id=?", (status, student_id)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# ATTENDANCE OPERATIONS
# ─────────────────────────────────────────────

def mark_attendance(student_id: str, status: str, date: str):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute(
            """INSERT INTO attendance (student_id, date, status, marked_at)
               VALUES (?,?,?,?)
               ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status, marked_at=excluded.marked_at""",
            (student_id, date, status, now)
        )
        conn.commit()
        return True, "Attendance marked."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_attendance_by_date(date: str):
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.name, s.student_id, s.room_number,
                  COALESCE(a.status, 'Not Marked') AS att_status,
                  a.marked_at
           FROM students s
           LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = ?
           ORDER BY s.name""",
        (date,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_attendance(student_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC",
        (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# COMPLAINTS OPERATIONS
# ─────────────────────────────────────────────

def add_complaint(student_id, student_name, category, description):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """INSERT INTO complaints (student_id, student_name, category, description, status, created_at)
           VALUES (?,?,?,?,?,?)""",
        (student_id, student_name, category, description, "Pending", now)
    )
    conn.commit()
    conn.close()
    return True, "Complaint registered."


def get_all_complaints():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM complaints ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_complaint_status(complaint_id: int, status: str):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE complaints SET status=?, updated_at=? WHERE id=?",
        (status, now, complaint_id)
    )
    conn.commit()
    conn.close()
    return True, f"Complaint status updated to {status}."


# ─────────────────────────────────────────────
# ENTRY / EXIT OPERATIONS
# ─────────────────────────────────────────────

def request_entry_exit(student_id: str, student_name: str, action: str, reason: str = ""):
    """Create a PENDING entry/exit request. Never auto-approve."""
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """INSERT INTO entry_exit_logs
           (student_id, student_name, action, status, reason, timestamp)
           VALUES (?,?,?,?,?,?)""",
        (student_id, student_name, action, "Pending", reason, now)
    )
    conn.commit()
    conn.close()
    return True, f"{action} request submitted. Awaiting admin approval."


def get_entry_exit_logs(status: str = None):
    conn = get_connection()
    if status:
        rows = conn.execute(
            "SELECT * FROM entry_exit_logs WHERE status=? ORDER BY timestamp DESC",
            (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM entry_exit_logs ORDER BY timestamp DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def approve_entry_exit(log_id: int, admin: str = "admin"):
    """Approve request and update student status."""
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log = conn.execute(
        "SELECT * FROM entry_exit_logs WHERE id=?", (log_id,)
    ).fetchone()
    if not log:
        conn.close()
        return False, "Request not found."

    # Update log status
    conn.execute(
        "UPDATE entry_exit_logs SET status='Approved', reviewed_at=?, reviewed_by=? WHERE id=?",
        (now, admin, log_id)
    )
    # Update student current status
    new_status = "Inside" if log["action"] == "Entry" else "Outside"
    conn.execute(
        "UPDATE students SET status=? WHERE student_id=?",
        (new_status, log["student_id"])
    )
    conn.commit()
    conn.close()
    return True, f"Request approved. Student is now {new_status}."


def reject_entry_exit(log_id: int, admin: str = "admin"):
    """Reject request. Student status unchanged."""
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE entry_exit_logs SET status='Rejected', reviewed_at=?, reviewed_by=? WHERE id=?",
        (now, admin, log_id)
    )
    conn.commit()
    conn.close()
    return True, "Request rejected. Student status unchanged."


# ─────────────────────────────────────────────
# DASHBOARD STATS
# ─────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")

    stats = {
        "total_students":    conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "inside_students":   conn.execute("SELECT COUNT(*) FROM students WHERE status='Inside'").fetchone()[0],
        "outside_students":  conn.execute("SELECT COUNT(*) FROM students WHERE status='Outside'").fetchone()[0],
        "total_rooms":       conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
        "available_rooms":   conn.execute("SELECT COUNT(*) FROM rooms WHERE occupied < capacity").fetchone()[0],
        "pending_requests":  conn.execute("SELECT COUNT(*) FROM entry_exit_logs WHERE status='Pending'").fetchone()[0],
        "pending_complaints":conn.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'").fetchone()[0],
        "today_attendance":  conn.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,)).fetchone()[0],
    }
    conn.close()
    return stats
