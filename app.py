"""
app.py - Main Streamlit entry point for Hostel Management System
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

import database as db
import utils

# ─────────────────────────────────────────────
# PAGE CONFIG & GLOBAL CSS
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="HostelHub – Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
db.init_db()

# ── Custom CSS ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid #334155;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px;
    border-radius: 8px;
    transition: background 0.2s;
    cursor: pointer;
    display: block;
    font-weight: 500;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(99,102,241,0.2) !important;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.8em;
    font-weight: 600;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2em;
    font-weight: 800;
    color: #0f172a !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99,102,241,0.25) !important;
}

/* ── Page headers ── */
.page-header {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white !important;
    padding: 22px 28px;
    border-radius: 16px;
    margin-bottom: 24px;
}
.page-header h2 { margin: 0; font-size: 1.5em; font-weight: 800; }
.page-header p  { margin: 4px 0 0; opacity: 0.85; font-size: 0.9em; }

/* ── Cards ── */
.info-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.info-card h4 { margin: 0 0 6px; font-size: 1em; font-weight: 700; color: #1e293b; }
.info-card p  { margin: 0; font-size: 0.88em; color: #64748b; }

/* ── Warning banner ── */
.late-warning {
    background: linear-gradient(90deg, #fef3c7, #fde68a);
    border-left: 5px solid #f59e0b;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
    color: #78350f;
    font-weight: 600;
    font-size: 0.95em;
}

/* ── Status pills ── */
.pill-pending  { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:20px; font-size:0.8em; font-weight:700; }
.pill-approved { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:20px; font-size:0.8em; font-weight:700; }
.pill-rejected { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:0.8em; font-weight:700; }

/* ── Dataframes ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f1f5f9;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88em !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-weight: 700 !important;
    font-size: 0.95em !important;
}

/* ── Logo text ── */
.logo-text {
    font-size: 1.5em;
    font-weight: 800;
    color: #818cf8 !important;
    letter-spacing: -0.5px;
}
.logo-sub {
    font-size: 0.75em;
    color: #94a3b8 !important;
    margin-top: -4px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="logo-text">🏨 HostelHub</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Management System</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Fetch pending counts for badges
    stats = db.get_dashboard_stats()
    pending_req  = stats["pending_requests"]
    pending_comp = stats["pending_complaints"]

    nav_items = [
        ("🏠", "Dashboard"),
        ("👨‍🎓", "Students"),
        ("🚪", "Rooms"),
        ("📋", "Attendance"),
        ("📝", "Complaints"),
        ("🔑", "Entry / Exit"),
        ("⚙️", "Admin Panel"),
    ]

    for icon, label in nav_items:
        badge = ""
        if label == "Entry / Exit" and pending_req:
            badge = f"  🔴 {pending_req}"
        if label == "Complaints" and pending_comp:
            badge = f"  🔴 {pending_comp}"
        if st.button(f"{icon}  {label}{badge}", key=f"nav_{label}",
                     use_container_width=True):
            st.session_state.page = label

    st.markdown("---")
    # After-10PM warning in sidebar
    if utils.is_after_10pm():
        st.markdown(
            '<div style="background:#fef3c7;color:#78350f;padding:10px;'
            'border-radius:8px;font-size:0.82em;font-weight:600;">'
            '⚠️ After 10 PM – Attendance cutoff!</div>',
            unsafe_allow_html=True
        )

    if st.session_state.admin_logged_in:
        st.markdown(
            '<div style="background:rgba(99,102,241,0.15);padding:8px 12px;'
            'border-radius:8px;font-size:0.82em;color:#818cf8;font-weight:600;">'
            '🔓 Admin Active</div>',
            unsafe_allow_html=True
        )
        if st.button("Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

page = st.session_state.page


# ═════════════════════════════════════════════
# PAGE: DASHBOARD
# ═════════════════════════════════════════════

def page_dashboard():
    st.markdown("""
    <div class="page-header">
        <h2>🏠 Dashboard</h2>
        <p>Welcome to HostelHub – your complete hostel management solution.</p>
    </div>
    """, unsafe_allow_html=True)

    # After-10PM global banner
    if utils.is_after_10pm():
        st.markdown(
            '<div class="late-warning">⚠️ It is after 10 PM! '
            'Attendance marking is now closed for today. '
            'Any unmarked students will be recorded as Absent.</div>',
            unsafe_allow_html=True
        )

    stats = db.get_dashboard_stats()

    # Row 1 – Student stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students",    stats["total_students"])
    c2.metric("Inside Hostel",     stats["inside_students"],
              delta=f"+{stats['inside_students']}", delta_color="normal")
    c3.metric("Outside Hostel",    stats["outside_students"])
    c4.metric("Today Attendance",  stats["today_attendance"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 – Room & request stats
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total Rooms",         stats["total_rooms"])
    c6.metric("Available Rooms",     stats["available_rooms"])
    c7.metric("Pending Entry/Exit",  stats["pending_requests"],
              delta=f"Action needed" if stats["pending_requests"] else "All clear",
              delta_color="inverse" if stats["pending_requests"] else "off")
    c8.metric("Pending Complaints",  stats["pending_complaints"],
              delta=f"Action needed" if stats["pending_complaints"] else "All clear",
              delta_color="inverse" if stats["pending_complaints"] else "off")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 🔑 Recent Entry/Exit Requests")
        logs = db.get_entry_exit_logs()[:8]
        if logs:
            df = pd.DataFrame(logs)[["student_name", "action", "status", "timestamp"]]
            df.columns = ["Student", "Action", "Status", "Time"]
            df["Time"] = df["Time"].apply(utils.friendly_datetime)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No entry/exit requests yet.")

    with col_right:
        st.markdown("#### 📝 Recent Complaints")
        complaints = db.get_all_complaints()[:6]
        if complaints:
            for c in complaints:
                status_color = {"Pending": "🟡", "In Progress": "🔵", "Resolved": "🟢"}.get(c["status"], "⚪")
                st.markdown(
                    f'<div class="info-card">'
                    f'<h4>{status_color} {c["student_name"]}</h4>'
                    f'<p>{c["category"]} — {c["status"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No complaints filed yet.")


# ═════════════════════════════════════════════
# PAGE: STUDENTS
# ═════════════════════════════════════════════

def page_students():
    st.markdown("""
    <div class="page-header">
        <h2>👨‍🎓 Student Management</h2>
        <p>Add, edit, and manage all hostel residents.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 All Students", "➕ Add Student", "✏️ Edit / Delete"])

    # ── Tab 1: View ──
    with tab1:
        students = db.get_all_students()
        if students:
            df = pd.DataFrame(students)
            display_cols = ["student_id", "name", "room_number", "contact",
                            "email", "course", "join_date", "status"]
            df = df[display_cols]
            df.columns = ["ID", "Name", "Room", "Contact",
                          "Email", "Course", "Joined", "Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(students)} students")
        else:
            st.info("No students found.")

    # ── Tab 2: Add ──
    with tab2:
        st.markdown("#### Add New Student")
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                new_id     = st.text_input("Student ID *", placeholder="e.g. STU007")
                new_name   = st.text_input("Full Name *", placeholder="e.g. Anjali Mehta")
                new_contact= st.text_input("Contact *", placeholder="10-digit phone")
                new_email  = st.text_input("Email", placeholder="student@college.edu")
            with col2:
                new_course = st.selectbox("Course", utils.COURSES)
                new_date   = st.date_input("Join Date", value=date.today())
                rooms      = db.get_all_rooms()
                available  = [r["room_number"] for r in rooms
                               if r["occupied"] < r["capacity"]]
                room_choice = st.selectbox(
                    "Assign Room (or Auto)",
                    ["Auto-assign"] + available
                )

        if st.button("✅ Add Student", type="primary"):
            ok, msg = utils.validate_student_id(new_id)
            if not ok:
                st.error(msg)
            elif not new_name.strip():
                st.error("Name cannot be empty.")
            else:
                ok2, msg2 = utils.validate_phone(new_contact)
                if not ok2:
                    st.error(msg2)
                else:
                    chosen_room = None if room_choice == "Auto-assign" else room_choice
                    success, result = db.add_student(
                        new_id.strip(), new_name.strip(), new_contact.strip(),
                        new_email.strip(), new_course,
                        str(new_date), chosen_room
                    )
                    if success:
                        st.success(result)
                        st.rerun()
                    else:
                        st.error(result)

    # ── Tab 3: Edit / Delete ──
    with tab3:
        students = db.get_all_students()
        if not students:
            st.info("No students to edit.")
        else:
            options = {s["student_id"]: s["name"] for s in students}
            sel_id = st.selectbox(
                "Select Student",
                list(options.keys()),
                format_func=lambda x: f"{x} — {options[x]}"
            )
            stu = db.get_student_by_id(sel_id)
            if stu:
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    upd_name    = st.text_input("Name",    value=stu["name"])
                    upd_contact = st.text_input("Contact", value=stu["contact"] or "")
                    upd_email   = st.text_input("Email",   value=stu["email"]   or "")
                with col2:
                    idx = utils.COURSES.index(stu["course"]) if stu["course"] in utils.COURSES else 0
                upd_course = st.selectbox(
                       "Course",
                        utils.COURSES,
                             index=idx,
                       key=f"upd_course_{sel_id}"
)
                    st.markdown(f"**Room:** {stu['room_number']}")
                    st.markdown(f"**Current Status:** {stu['status']}")

                col_save, col_del = st.columns([2, 1])
                with col_save:
                    if st.button("💾 Save Changes", type="primary"):
                        ok, msg = utils.validate_phone(upd_contact)
                        if not ok:
                            st.error(msg)
                        else:
                            db.update_student(sel_id, upd_name, upd_contact,
                                              upd_email, upd_course)
                            st.success("Student updated successfully.")
                            st.rerun()
                with col_del:
                    if st.button("🗑️ Delete Student", type="secondary"):
                        success, msg = db.delete_student(sel_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)


# ═════════════════════════════════════════════
# PAGE: ROOMS
# ═════════════════════════════════════════════

def page_rooms():
    st.markdown("""
    <div class="page-header">
        <h2>🚪 Room Management</h2>
        <p>Manage room allocation, capacity, and availability.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 Room Status", "➕ Add Room"])

    with tab1:
        rooms = utils.rooms_to_display(db.get_all_rooms())
        if rooms:
            df = pd.DataFrame(rooms)
            df = df[["room_number", "floor", "capacity", "occupied",
                     "free_beds", "availability"]]
            df.columns = ["Room No.", "Floor", "Capacity", "Occupied",
                          "Free Beds", "Status"]

            # Color occupied rooms
            def highlight_full(row):
                if row["Status"] == "Full":
                    return ["background-color: #fee2e2"] * len(row)
                elif row["Free Beds"] == row["Capacity"]:
                    return ["background-color: #d1fae5"] * len(row)
                return [""] * len(row)

            styled = df.style.apply(highlight_full, axis=1)
            st.dataframe(styled, use_container_width=True, hide_index=True)

            # Summary
            total  = len(rooms)
            full   = sum(1 for r in rooms if r["availability"] == "Full")
            avail  = total - full
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Rooms",     total)
            c2.metric("Available",       avail)
            c3.metric("Full",            full)
        else:
            st.info("No rooms defined yet.")

    with tab2:
        st.markdown("#### Add New Room")
        col1, col2, col3 = st.columns(3)
        with col1:
            rn      = st.text_input("Room Number *", placeholder="e.g. 401")
        with col2:
            cap     = st.number_input("Capacity", min_value=1, max_value=10, value=2)
        with col3:
            floor   = st.number_input("Floor",    min_value=0, max_value=20, value=1)

        if st.button("➕ Add Room", type="primary"):
            ok, msg = utils.validate_room_number(rn)
            if not ok:
                st.error(msg)
            else:
                success, result = db.add_room(rn.strip(), cap, floor)
                if success:
                    st.success(result)
                    st.rerun()
                else:
                    st.error(result)

        st.markdown("---")
        st.markdown("#### 🗑️ Delete Empty Room")
        rooms = db.get_all_rooms()
        empty = [r["room_number"] for r in rooms if r["occupied"] == 0]
        if empty:
            del_rn = st.selectbox("Select empty room to delete", empty)
            if st.button("Delete Room", type="secondary"):
                success, msg = db.delete_room(del_rn)
                st.success(msg) if success else st.error(msg)
                st.rerun()
        else:
            st.info("All rooms are occupied – cannot delete any.")


# ═════════════════════════════════════════════
# PAGE: ATTENDANCE
# ═════════════════════════════════════════════

def page_attendance():
    st.markdown("""
    <div class="page-header">
        <h2>📋 Attendance System</h2>
        <p>Mark and track daily attendance for all residents.</p>
    </div>
    """, unsafe_allow_html=True)

    # After-10PM warning
    if utils.is_after_10pm():
        st.markdown(
            '<div class="late-warning">⚠️ WARNING: It is after 10 PM! '
            'Attendance for today should have been marked already. '
            'Marking now will be recorded but may be considered late.</div>',
            unsafe_allow_html=True
        )

    tab1, tab2 = st.tabs(["📅 Mark Attendance", "📊 View Records"])

    with tab1:
        sel_date = st.date_input("Select Date", value=date.today())
        date_str = str(sel_date)

        records = db.get_attendance_by_date(date_str)
        if not records:
            st.info("No students found.")
        else:
            st.markdown(f"**Marking attendance for: {sel_date.strftime('%d %B %Y')}**")
            st.markdown("---")

            # Build a form with one row per student
            statuses = {}
            for rec in records:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(
                        f"**{rec['name']}** &nbsp;<span style='color:#94a3b8;font-size:0.8em'>"
                        f"({rec['student_id']}) — Room {rec['room_number']}</span>",
                        unsafe_allow_html=True
                    )
                with col2:
                    current = rec["att_status"] if rec["att_status"] != "Not Marked" else "Present"
                    choice = st.radio(
                        label="",
                        options=["Present", "Absent"],
                        index=0 if current == "Present" else 1,
                        horizontal=True,
                        key=f"att_{rec['student_id']}_{date_str}"
                    )
                    statuses[rec["student_id"]] = choice
                with col3:
                    st.markdown(
                        utils.status_badge_html(rec["att_status"]),
                        unsafe_allow_html=True
                    )
                st.divider()

            if st.button("💾 Save Attendance", type="primary"):
                saved = 0
                for sid, status in statuses.items():
                    ok, _ = db.mark_attendance(sid, status, date_str)
                    if ok:
                        saved += 1
                st.success(f"✅ Attendance saved for {saved} student(s).")
                st.rerun()

    with tab2:
        view_date = st.date_input("View Date", value=date.today(), key="view_att")
        records = db.get_attendance_by_date(str(view_date))
        if records:
            df = pd.DataFrame(records)
            df = df[["name", "student_id", "room_number", "att_status", "marked_at"]]
            df.columns = ["Name", "ID", "Room", "Status", "Marked At"]
            df["Marked At"] = df["Marked At"].apply(utils.friendly_datetime)

            total   = len(df)
            present = (df["Status"] == "Present").sum()
            absent  = (df["Status"] == "Absent").sum()
            unmarked= (df["Status"] == "Not Marked").sum()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total",     total)
            c2.metric("Present",   present)
            c3.metric("Absent",    absent)
            c4.metric("Unmarked",  unmarked)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No data for this date.")


# ═════════════════════════════════════════════
# PAGE: COMPLAINTS
# ═════════════════════════════════════════════

def page_complaints():
    st.markdown("""
    <div class="page-header">
        <h2>📝 Complaint System</h2>
        <p>Register and track hostel complaints.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🆕 File Complaint", "📜 All Complaints"])

    with tab1:
        st.markdown("#### Register a New Complaint")
        students = db.get_all_students()
        if not students:
            st.warning("No students in the system.")
            return

        options = {s["student_id"]: s["name"] for s in students}
        sel_id = st.selectbox(
            "Your Student ID",
            list(options.keys()),
            format_func=lambda x: f"{x} — {options[x]}"
        )
        category    = st.selectbox("Category", utils.COMPLAINT_CATEGORIES)
        description = st.text_area("Describe your complaint", height=120)

        if st.button("📤 Submit Complaint", type="primary"):
            if not description.strip():
                st.error("Please provide a description.")
            else:
                success, msg = db.add_complaint(
                    sel_id, options[sel_id], category, description.strip()
                )
                st.success(msg) if success else st.error(msg)
                st.rerun()

    with tab2:
        complaints = db.get_all_complaints()
        if not complaints:
            st.info("No complaints filed yet.")
            return

        # Filter
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Pending", "In Progress", "Resolved"]
        )
        shown = complaints if filter_status == "All" else [
            c for c in complaints if c["status"] == filter_status
        ]

        for c in shown:
            color = {"Pending": "🟡", "In Progress": "🔵", "Resolved": "🟢"}.get(c["status"], "⚪")
            with st.expander(
                f"{color} #{c['id']} — {c['student_name']} | {c['category']} | {c['status']}"
            ):
                st.markdown(f"**Description:** {c['description']}")
                st.markdown(f"**Filed on:** {utils.friendly_datetime(c['created_at'])}")
                if c["updated_at"]:
                    st.markdown(f"**Last updated:** {utils.friendly_datetime(c['updated_at'])}")

                if st.session_state.admin_logged_in:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "In Progress", "Resolved"],
                        index=["Pending", "In Progress", "Resolved"].index(c["status"]),
                        key=f"comp_status_{c['id']}"
                    )
                    if st.button("Update", key=f"comp_update_{c['id']}"):
                        db.update_complaint_status(c["id"], new_status)
                        st.success("Status updated.")
                        st.rerun()
                else:
                    st.caption("🔒 Admin login required to update status.")


# ═════════════════════════════════════════════
# PAGE: ENTRY / EXIT
# ═════════════════════════════════════════════

def page_entry_exit():
    st.markdown("""
    <div class="page-header">
        <h2>🔑 Entry / Exit System</h2>
        <p>Submit entry or exit requests – all requests require admin approval.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📤 Submit Request", "📊 My Requests"])

    with tab1:
        st.markdown("""
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;
             padding:14px 18px;margin-bottom:16px;color:#1e40af;font-size:0.9em;">
        ℹ️ <strong>How it works:</strong> Submit your request below.
        It will be saved as <strong>Pending</strong> and reviewed by the hostel admin.
        Your status will only update <em>after</em> approval.
        </div>
        """, unsafe_allow_html=True)

        students = db.get_all_students()
        if not students:
            st.warning("No students found.")
            return

        options = {s["student_id"]: f"{s['name']} (Currently {s['status']})"
                   for s in students}
        sel_id = st.selectbox(
            "Select Your ID",
            list(options.keys()),
            format_func=lambda x: f"{x} — {options[x]}"
        )

        stu = db.get_student_by_id(sel_id)
        if stu:
            # Suggest opposite action
            suggested = "Exit" if stu["status"] == "Inside" else "Entry"
            action = st.radio(
                "Request Type",
                ["Entry", "Exit"],
                index=["Entry", "Exit"].index(suggested),
                horizontal=True
            )
            reason = st.text_input("Reason (optional)",
                                   placeholder="e.g. going home for the weekend")

            # Info about current state
            current_icon = "🏠" if stu["status"] == "Inside" else "🚶"
            st.markdown(
                f'<div class="info-card">'
                f'<h4>{current_icon} Current Status: {stu["status"]}</h4>'
                f'<p>After admin approval, status will change to '
                f'<strong>{"Outside" if action == "Exit" else "Inside"}</strong>.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

            if st.button(f"📤 Submit {action} Request", type="primary"):
                # Check for existing pending request
                pending = [
                    l for l in db.get_entry_exit_logs("Pending")
                    if l["student_id"] == sel_id
                ]
                if pending:
                    st.warning(
                        "⚠️ You already have a pending request. "
                        "Please wait for admin review."
                    )
                else:
                    success, msg = db.request_entry_exit(
                        sel_id, stu["name"], action, reason
                    )
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                    else:
                        st.error(msg)

    with tab2:
        students = db.get_all_students()
        if not students:
            return
        options = {s["student_id"]: s["name"] for s in students}
        view_id = st.selectbox(
            "View requests for",
            list(options.keys()),
            format_func=lambda x: f"{x} — {options[x]}",
            key="view_req_sel"
        )

        all_logs = db.get_entry_exit_logs()
        my_logs = [l for l in all_logs if l["student_id"] == view_id]

        if my_logs:
            for log in my_logs:
                status_icon = {"Pending": "⏳", "Approved": "✅", "Rejected": "❌"}.get(
                    log["status"], "•"
                )
                status_bg = {"Pending": "#fef3c7", "Approved": "#d1fae5",
                             "Rejected": "#fee2e2"}.get(log["status"], "#f8fafc")
                st.markdown(
                    f'<div style="background:{status_bg};border-radius:12px;'
                    f'padding:14px 18px;margin-bottom:10px;">'
                    f'<strong>{status_icon} {log["action"]}</strong> — '
                    f'<strong>{log["status"]}</strong><br>'
                    f'<span style="font-size:0.85em;color:#64748b;">'
                    f'Submitted: {utils.friendly_datetime(log["timestamp"])}'
                    + (f' | Reviewed: {utils.friendly_datetime(log["reviewed_at"])}'
                       if log["reviewed_at"] else "") +
                    f'</span>'
                    + (f'<br><span style="font-size:0.85em;">Reason: {log["reason"]}</span>'
                       if log["reason"] else "") +
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No requests found for this student.")


# ═════════════════════════════════════════════
# PAGE: ADMIN PANEL
# ═════════════════════════════════════════════

def page_admin():
    st.markdown("""
    <div class="page-header">
        <h2>⚙️ Admin Panel</h2>
        <p>Manage entry/exit approvals, complaints, and view system overview.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Login Gate ──────────────────────────
    if not st.session_state.admin_logged_in:
        st.markdown("#### 🔐 Admin Login")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container():
                uname = st.text_input("Username", placeholder="admin")
                pwd   = st.text_input("Password", type="password")
                if st.button("Login", type="primary", use_container_width=True):
                    if db.verify_admin(uname, pwd):
                        st.session_state.admin_logged_in = True
                        st.success("✅ Logged in as admin.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials.")
            st.caption("Default: username `admin`, password `admin123`")
        return

    # ── Admin Dashboard ──────────────────────
    stats = db.get_dashboard_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students",    stats["total_students"])
    c2.metric("Pending Requests",  stats["pending_requests"])
    c3.metric("Pending Complaints",stats["pending_complaints"])
    c4.metric("Available Rooms",   stats["available_rooms"])

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "⏳ Pending Entry/Exit",
        "📜 All Logs",
        "📝 Complaint Management",
        "👨‍🎓 Student Overview"
    ])

    # ── Tab 1: Pending Approvals ──────────────
    with tab1:
        pending = db.get_entry_exit_logs("Pending")
        if not pending:
            st.success("✅ No pending requests. All clear!")
        else:
            st.markdown(
                f'<div style="background:#fef3c7;border-radius:10px;'
                f'padding:10px 16px;margin-bottom:16px;color:#92400e;">'
                f'⏳ <strong>{len(pending)} pending request(s)</strong> require your review.</div>',
                unsafe_allow_html=True
            )
            for log in pending:
                with st.container():
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        action_icon = "🚪" if log["action"] == "Exit" else "🏠"
                        st.markdown(
                            f'<div class="info-card">'
                            f'<h4>{action_icon} {log["student_name"]} — {log["action"]} Request</h4>'
                            f'<p>Student ID: {log["student_id"]} &nbsp;|&nbsp; '
                            f'Submitted: {utils.friendly_datetime(log["timestamp"])}'
                            + (f' &nbsp;|&nbsp; Reason: {log["reason"]}' if log["reason"] else "") +
                            f'</p></div>',
                            unsafe_allow_html=True
                        )
                    with col2:
                        if st.button("✅ Approve", key=f"approve_{log['id']}",
                                     type="primary", use_container_width=True):
                            ok, msg = db.approve_entry_exit(log["id"])
                            st.success(msg) if ok else st.error(msg)
                            st.rerun()
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{log['id']}",
                                     type="secondary", use_container_width=True):
                            ok, msg = db.reject_entry_exit(log["id"])
                            st.warning(msg) if ok else st.error(msg)
                            st.rerun()

    # ── Tab 2: All Logs ───────────────────────
    with tab2:
        filter_col, _ = st.columns([2, 3])
        with filter_col:
            log_filter = st.selectbox(
                "Filter",
                ["All", "Pending", "Approved", "Rejected"]
            )

        logs = db.get_entry_exit_logs(None if log_filter == "All" else log_filter)
        if logs:
            df = pd.DataFrame(logs)
            df = df[["id", "student_name", "student_id", "action",
                     "status", "reason", "timestamp", "reviewed_at"]]
            df.columns = ["ID", "Name", "Stu.ID", "Action",
                          "Status", "Reason", "Submitted", "Reviewed At"]
            df["Submitted"]   = df["Submitted"].apply(utils.friendly_datetime)
            df["Reviewed At"] = df["Reviewed At"].apply(utils.friendly_datetime)

            # Color coding
            def color_status(val):
                colors = {
                    "Pending":  "background-color: #fef3c7; color: #92400e",
                    "Approved": "background-color: #d1fae5; color: #065f46",
                    "Rejected": "background-color: #fee2e2; color: #991b1b",
                }
                return colors.get(val, "")

            styled = df.style.applymap(color_status, subset=["Status"])
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.info("No logs found.")

    # ── Tab 3: Complaint Management ───────────
    with tab3:
        complaints = db.get_all_complaints()
        if not complaints:
            st.info("No complaints.")
        else:
            pending_c = [c for c in complaints if c["status"] == "Pending"]
            progress_c= [c for c in complaints if c["status"] == "In Progress"]
            resolved_c= [c for c in complaints if c["status"] == "Resolved"]

            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Pending",     len(pending_c))
            cc2.metric("In Progress", len(progress_c))
            cc3.metric("Resolved",    len(resolved_c))

            st.markdown("---")
            for c in complaints:
                color = {"Pending": "🟡", "In Progress": "🔵", "Resolved": "🟢"}.get(
                    c["status"], "⚪"
                )
                with st.expander(
                    f"{color} #{c['id']} — {c['student_name']} | {c['category']} | {c['status']}"
                ):
                    st.write(f"**Description:** {c['description']}")
                    st.write(f"**Filed on:** {utils.friendly_datetime(c['created_at'])}")

                    new_s = st.selectbox(
                        "Update Status",
                        ["Pending", "In Progress", "Resolved"],
                        index=["Pending", "In Progress", "Resolved"].index(c["status"]),
                        key=f"adm_comp_{c['id']}"
                    )
                    if st.button("Save", key=f"adm_comp_save_{c['id']}"):
                        db.update_complaint_status(c["id"], new_s)
                        st.success("Updated.")
                        st.rerun()

    # ── Tab 4: Student Overview ───────────────
    with tab4:
        students = db.get_all_students()
        if students:
            df = pd.DataFrame(students)
            cols = ["student_id", "name", "room_number", "contact",
                    "course", "join_date", "status"]
            df = df[cols]
            df.columns = ["ID", "Name", "Room", "Contact",
                          "Course", "Joined", "Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No students.")


# ═════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════

PAGE_MAP = {
    "Dashboard":   page_dashboard,
    "Students":    page_students,
    "Rooms":       page_rooms,
    "Attendance":  page_attendance,
    "Complaints":  page_complaints,
    "Entry / Exit":page_entry_exit,
    "Admin Panel": page_admin,
}

PAGE_MAP.get(page, page_dashboard)()
