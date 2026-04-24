"""
utils.py - Utility / helper functions for Hostel Management System
"""

from datetime import datetime


# ─────────────────────────────────────────────
# TIME HELPERS
# ─────────────────────────────────────────────

def is_after_10pm() -> bool:
    """Return True if current time is at or after 22:00."""
    return datetime.now().hour >= 22


def current_time_str() -> str:
    return datetime.now().strftime("%H:%M:%S")


def current_date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def current_datetime_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def friendly_datetime(dt_str: str) -> str:
    """Convert ISO datetime string to a friendly display format."""
    if not dt_str:
        return "—"
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return dt_str


# ─────────────────────────────────────────────
# STATUS BADGE HELPERS
# ─────────────────────────────────────────────

STATUS_COLORS = {
    "Pending":     ("#FEF3C7", "#92400E", "⏳"),
    "Approved":    ("#D1FAE5", "#065F46", "✅"),
    "Rejected":    ("#FEE2E2", "#991B1B", "❌"),
    "In Progress": ("#DBEAFE", "#1E40AF", "🔄"),
    "Resolved":    ("#D1FAE5", "#065F46", "✔️"),
    "Present":     ("#D1FAE5", "#065F46", "✅"),
    "Absent":      ("#FEE2E2", "#991B1B", "❌"),
    "Not Marked":  ("#F3F4F6", "#374151", "—"),
    "Inside":      ("#D1FAE5", "#065F46", "🏠"),
    "Outside":     ("#FEF3C7", "#92400E", "🚶"),
}


def status_badge_html(status: str) -> str:
    """Return an HTML span styled as a colored badge."""
    bg, fg, icon = STATUS_COLORS.get(status, ("#F3F4F6", "#374151", "•"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border-radius:12px;font-size:0.82em;font-weight:600;">'
        f'{icon} {status}</span>'
    )


# ─────────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────────

def validate_student_id(sid: str) -> tuple[bool, str]:
    if not sid or not sid.strip():
        return False, "Student ID cannot be empty."
    if len(sid) > 20:
        return False, "Student ID must be ≤ 20 characters."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    digits = phone.replace(" ", "").replace("-", "")
    if not digits.isdigit():
        return False, "Contact must contain only digits."
    if len(digits) not in (10, 11, 12):
        return False, "Contact must be 10–12 digits."
    return True, ""


def validate_room_number(rn: str) -> tuple[bool, str]:
    if not rn or not rn.strip():
        return False, "Room number cannot be empty."
    return True, ""


# ─────────────────────────────────────────────
# DATA FORMATTERS
# ─────────────────────────────────────────────

def format_occupancy(occupied: int, capacity: int) -> str:
    pct = (occupied / capacity * 100) if capacity else 0
    bar_filled = int(pct / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    return f"{bar} {occupied}/{capacity}"


def rooms_to_display(rooms: list[dict]) -> list[dict]:
    """Add computed display fields to room records."""
    out = []
    for r in rooms:
        r2 = dict(r)
        r2["availability"] = "Full" if r["occupied"] >= r["capacity"] else "Available"
        r2["free_beds"] = r["capacity"] - r["occupied"]
        out.append(r2)
    return out


COMPLAINT_CATEGORIES = [
    "Maintenance / Repairs",
    "Food & Mess",
    "Security",
    "Cleanliness",
    "Noise / Disturbance",
    "Internet / Power",
    "Other",
]

COURSES = [
    "B.Tech CSE", "B.Tech ECE", "B.Tech IT", "B.Tech Civil",
    "BCA", "MCA", "B.Sc Physics", "B.Sc Maths", "B.Sc Chemistry",
    "MBA", "M.Tech", "Other",
]
