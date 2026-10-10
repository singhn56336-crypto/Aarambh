import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import hashlib
import datetime
import pandas as pd
import numpy as np
import plotly.express as px

# 1. PAGE CONFIGURATION & STYLING
st.set_page_config(
    page_title="AARAMBH — Smart Campus Portal",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
    <style>
        .stApp { background-color: #0f172a; color: #f8fafc; }
        .card {
            background-color: #1e293b;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .card-title { color: #94a3b8; font-size: 13px; font-weight: bold; text-transform: uppercase; }
        .card-value { color: #38bdf8; font-size: 22px; font-weight: bold; margin-top: 5px; }
        .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. DATABASE HELPER FUNCTIONS (Dynamic Users & Student Metrics)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Users table expanded with performance metrics (CGPA, Attendance, etc.)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            role TEXT,
            cgpa REAL DEFAULT 7.5,
            attendance REAL DEFAULT 75.0,
            lms_progress REAL DEFAULT 70.0,
            mock_score REAL DEFAULT 70.0,
            coding_assessment REAL DEFAULT 6.0,
            created_at TEXT
        )
    ''')
    # Login History Logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            login_time TEXT
        )
    ''')
    
    # Insert default mock students if table is completely empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        default_students = [
            ("STU001", "Aarav Sharma", "aarav@campus.edu", hashlib.sha256(b"pass123").hexdigest(), "Candidate / Student", 8.5, 82.0, 82.0, 82.0, 8.0, "2026-01-10 10:00:00"),
            ("STU002", "Diya Patel", "diya@campus.edu", hashlib.sha256(b"pass123").hexdigest(), "Candidate / Student", 6.2, 50.0, 50.0, 50.0, 5.0, "2026-01-11 11:00:00"),
            ("STU003", "Rohan Verma", "rohan@campus.edu", hashlib.sha256(b"pass123").hexdigest(), "Candidate / Student", 7.8, 40.0, 40.0, 40.0, 4.0, "2026-01-12 12:00:00"),
            ("STU004", "Isha Reddy", "isha@campus.edu", hashlib.sha256(b"pass123").hexdigest(), "Candidate / Student", 9.1, 90.0, 90.0, 90.0, 9.0, "2026-01-13 09:00:00"),
            ("STU005", "Kabir Singh", "kabir@campus.edu", hashlib.sha256(b"pass123").hexdigest(), "Candidate / Student", 5.5, 35.0, 35.0, 35.0, 3.0, "2026-01-14 14:00:00"),
        ]
        c.executemany('''
            INSERT INTO users (student_id, username, email, password, role, cgpa, attendance, lms_progress, mock_score, coding_assessment, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', default_students)
        
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def register_user(username, email, password, role):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Generate unique Student ID automatically (e.g., STU006, STU007...)
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0] + 1
        student_id = f"STU{count:03d}"
        
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Default baseline scores assigned to new registered user
        c.execute(
            '''INSERT INTO users(student_id, username, email, password, role, cgpa, attendance, lms_progress, mock_score, coding_assessment, created_at) 
               VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (student_id, username, email, hash_password(password), role, 7.8, 80.0, 75.0, 70.0, 7.0, created_at)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        '''SELECT student_id, username, email, role, cgpa, attendance, lms_progress, mock_score, coding_assessment, created_at 
           FROM users WHERE username=? AND password=?''',
        (username, hash_password(password))
    )
    user = c.fetchone()
    
    if user:
        login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT INTO login_logs(username, login_time) VALUES (?,?)', (username, login_time))
        conn.commit()
        conn.close()
        return {
            "student_id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[3],
            "cgpa": user[4],
            "attendance": user[5],
            "lms_progress": user[6],
            "mock_score": user[7],
            "coding_assessment": user[8],
            "created_at": user[9],
            "last_login": login_time
        }
    conn.close()
    return None

def get_user_login_history(username):
    conn = sqlite3.connect('users.db')
    df_logs = pd.read_sql_query('SELECT login_time FROM login_logs WHERE username=? ORDER BY id DESC LIMIT 5', conn, params=(username,))
    conn.close()
    return df_logs

init_db()


# ---------------------------------------------------------
# 3. DYNAMIC STUDENT DATA LOADER FROM DATABASE
# ---------------------------------------------------------
@st.cache_data
def load_student_data():
    conn = sqlite3.connect('users.db')
    # Automatically pulls all registered candidates from database into DataFrame
    df_db = pd.read_sql_query('''
        SELECT 
            student_id AS "Student ID", 
            username AS "Name", 
            cgpa AS "CGPA", 
            attendance AS "Attendance %", 
            lms_progress AS "LMS Progress %", 
            mock_score AS "Mock Interview Score", 
            coding_assessment AS "Coding Assessment" 
        FROM users
    ''', conn)
    conn.close()
    return df_db


# ---------------------------------------------------------
# 4. CORE ENGINE: SUCCESS METRICS & RISK IDENTIFICATION
# ---------------------------------------------------------
def calculate_success_metrics(row):
    academic_score = (row['CGPA'] / 10.0) * 40
    attendance_score = (row['Attendance %'] / 100.0) * 30
    placement_score = (((row['Mock Interview Score'] + (row['Coding Assessment'] * 10)) / 2.0) / 100.0) * 30
    
    total_success_score = round(academic_score + attendance_score + placement_score, 1)
    
    risk_level = "Low Risk"
    risk_color = "green"
    if total_success_score < 55:
        risk_level = "High Risk (Immediate Intervention Required)"
        risk_color = "red"
    elif total_success_score < 75:
        risk_level = "Medium Risk (Monitor Performance)"
        risk_color = "orange"
        
    segment = "General"
    if row['CGPA'] >= 7.5 and row['Mock Interview Score'] < 50:
        segment = "High Academic / Low Placement Readiness"
    elif row['Attendance %'] < 75 and row['CGPA'] >= 7.0:
        segment = "High Potential / Low Engagement"
    elif row['CGPA'] < 6.0:
        segment = "Critical Academic Support Needed"
    else:
        segment = "Balanced Performer"
        
    return pd.Series([
        total_success_score, risk_level, risk_color, segment, 
        round(academic_score, 1), round(attendance_score, 1), round(placement_score, 1)
    ])


# ---------------------------------------------------------
# 5. SESSION STATE MANAGEMENT
# ---------------------------------------------------------
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'current_q_idx' not in st.session_state:
    st.session_state.current_q_idx = 0


# ---------------------------------------------------------
# 6. LOGIN GATEKEEPER
# ---------------------------------------------------------
if not st.session_state.is_logged_in:
    st.title("🎓 AARAMBH: Smart Campus Student Success Platform")
    st.caption("Powered by KPMG Decision Intelligence Framework")
    st.info("🔒 Please login or register to access the platform.")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register New Account"])

    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                login_user = st.text_input("Username")
                login_pass = st.text_input("Password", type="password")
                btn_login = st.form_submit_button("Login to Portal", use_container_width=True)

                if btn_login:
                    auth_data = authenticate_user(login_user, login_pass)
                    if auth_data:
                        st.session_state.is_logged_in = True
                        st.session_state.user_info = auth_data
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password!")

    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                reg_user = st.text_input("Choose Username")
                reg_email = st.text_input("Email Address")
                reg_pass = st.text_input("Choose Password", type="password")
                reg_role = st.selectbox("Select Role", ["Candidate / Student", "Interviewer", "Admin"])
                btn_reg = st.form_submit_button("Create Account & Join Student Registry", use_container_width=True)

                if btn_reg:
                    if reg_user and reg_email and reg_pass:
                        if register_user(reg_user, reg_email, reg_pass, reg_role):
                            st.success("Account successfully created and added to Student Registry! Now go to Login tab.")
                        else:
                            st.warning("Username already exists.")
                    else:
                        st.error("Please fill all fields.")

# ---------------------------------------------------------
# 7. UNLOCKED AARAMBH PORTAL (AFTER LOGIN)
# ---------------------------------------------------------
else:
    user = st.session_state.user_info

    # Load dynamic student data from database and calculate metrics
    df = load_student_data()
    df[['Success Score', 'Risk Level', 'Risk Color', 'Segment', 'Acad_Contribution', 'Att_Contribution', 'Place_Contribution']] = df.apply(calculate_success_metrics, axis=1)

    # SIDEBAR NAVIGATION
    st.sidebar.header("🎯 Navigation Hub")
    st.sidebar.markdown(f"👤 **User:** `{user['username']}`")
    st.sidebar.markdown(f"🏷️ **Role:** `{user['role']}`")
    st.sidebar.markdown("---")

    app_mode = st.sidebar.radio(
        "Go to Page:",
        ["Overview Dashboard", "Mock Interview", "Student Deep-Dive & Action Center", "My Login Profile"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.user_info = {}
        st.rerun()

    # ==================== PAGE 1: OVERVIEW DASHBOARD ====================
    if app_mode == "Overview Dashboard":
        st.header("📊 Campus Health Overview (Dynamic Student Registry)")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Monitored Students", len(df))
        col2.metric("Average Success Score", f"{df['Success Score'].mean():.1f} / 100")
        col3.metric("Students At High Risk", len(df[df['Risk Level'].str.contains("High Risk")]))
        
        st.markdown("---")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Distribution of Student Segments")
            fig1 = px.bar(df, x="Segment", title="Student Grouping for Targeted Actions", color="Segment")
            st.plotly_chart(fig1, use_container_width=True)
            
        with chart_col2:
            st.subheader("Unified Student Registry View (Includes All Registered Users)")
            st.dataframe(df[["Student ID", "Name", "CGPA", "Attendance %", "Success Score", "Risk Level"]], use_container_width=True)

    # ==================== PAGE 2: MOCK INTERVIEW ====================
    elif app_mode == "Mock Interview":
        st.header("🎥 Smart Campus AI — Mock Interview Portal")
        st.caption(f"Active Session: {user['username']}")

        questions = [
            "1. Tell me about yourself and your experience with software engineering or data projects.",
            "2. Describe a challenging technical problem you solved. What approach did you take?",
            "3. How do you handle tight deadlines or conflicting project priorities in a team?",
            "4. Where do you see yourself professionally in the next 3 to 5 years?"
        ]

        c_left, c_right = st.columns([1.2, 1])

        with c_left:
            st.subheader("📹 Live Webcam Feed & Session Recorder")
            webcam_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { background-color: #0f172a; color: white; font-family: sans-serif; margin: 0; }
                    #videoPreview { width: 100%; max-width: 640px; height: 350px; background-color: #1e293b; border: 2px solid #334155; border-radius: 12px; transform: scaleX(-1); }
                    .btn-container { margin-top: 15px; display: flex; gap: 10px; }
                    button { padding: 10px 18px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; }
                    #btnStart { background-color: #10b981; color: white; }
                    #btnStop { background-color: #ef4444; color: white; opacity: 0.5; }
                    #status { margin-top: 10px; font-size: 14px; color: #38bdf8; font-weight: bold; }
                </style>
            </head>
            <body>
                <video id="videoPreview" autoplay muted></video>
                <div id="status">STATUS: Initializing Camera...</div>
                <div class="btn-container">
                    <button id="btnStart" onclick="startRecording()">🔴 Start Recording</button>
                    <button id="btnStop" onclick="stopRecording()" disabled>⏹️ Stop & Save Session</button>
                </div>

                <script>
                    let mediaRecorder;
                    let recordedChunks = [];
                    const videoElement = document.getElementById('videoPreview');
                    const btnStart = document.getElementById('btnStart');
                    const btnStop = document.getElementById('btnStop');
                    const statusLabel = document.getElementById('status');

                    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                        .then(stream => {
                            videoElement.srcObject = stream;
                            statusLabel.innerText = "STATUS: Camera Ready";
                            statusLabel.style.color = "#94a3b8";

                            mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
                            mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
                            mediaRecorder.onstop = () => {
                                const blob = new Blob(recordedChunks, { type: 'video/mp4' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = 'interview_recording.mp4';
                                a.click();
                                statusLabel.innerText = "STATUS: ✅ Saved as interview_recording.mp4";
                                statusLabel.style.color = "#10b981";
                            };
                        })
                        .catch(err => {
                            statusLabel.innerText = "Error: Camera Access Denied!";
                            statusLabel.style.color = "#ef4444";
                        });

                    function startRecording() {
                        recordedChunks = [];
                        mediaRecorder.start();
                        statusLabel.innerText = "STATUS: 🔴 Recording Active...";
                        statusLabel.style.color = "#ef4444";
                        btnStart.disabled = true; btnStart.style.opacity = "0.5";
                        btnStop.disabled = false; btnStop.style.opacity = "1";
                    }

                    function stopRecording() {
                        mediaRecorder.stop();
                        btnStart.disabled = false; btnStart.style.opacity = "1";
                        btnStop.disabled = true; btnStop.style.opacity = "0.5";
                    }
                </script>
            </body>
            </html>
            """
            components.html(webcam_html, height=480)

        with c_right:
            st.markdown("<h4 style='color: #38bdf8;'>INTERVIEW QUESTION</h4>", unsafe_allow_html=True)
            st.info(f"**{questions[st.session_state.current_q_idx]}**")

            st.markdown("<h5 style='color: #94a3b8;'>Candidate Notes / Key Answer Points</h5>", unsafe_allow_html=True)
            st.text_area("Type notes here...", height=180, key=f"notes_{st.session_state.current_q_idx}")

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("◀️ Previous", use_container_width=True):
                    if st.session_state.current_q_idx > 0:
                        st.session_state.current_q_idx -= 1
                        st.rerun()
            with btn2:
                if st.button("Next Question ▶️", use_container_width=True):
                    if st.session_state.current_q_idx < len(questions) - 1:
                        st.session_state.current_q_idx += 1
                        st.rerun()

    # ==================== PAGE 3: STUDENT DEEP-DIVE & ACTION CENTER ====================
    elif app_mode == "Student Deep-Dive & Action Center":
        st.header("🔍 Individual Action Center & Intelligence Hub")
        
        selected_student_name = st.selectbox("Select a Student to Analyze:", df["Name"].unique())
        student_row = df[df["Name"] == selected_student_name].iloc[0]
        
        left_col, right_col = st.columns([1, 2])
        
        with left_col:
            st.markdown(f"### Profile: **{student_row['Name']}**")
            st.write(f"**Student ID:** {student_row['Student ID']}")
            st.markdown(f"**Status Flag:** :{student_row['Risk Color']}[{student_row['Risk Level']}]")
            st.markdown(f"**Assigned Action Segment:** `{student_row['Segment']}`")
            st.metric("Unified Success Score", f"{student_row['Success Score']} / 100")
            
        with right_col:
            st.subheader("⚖️ Explainable Score Breakdown")
            st.caption("This chart displays exactly how much each data category contributed to the final score.")
            
            breakdown_data = pd.DataFrame({
                "Indicator Category": ["Academic Performance", "Attendance Record", "Placement Readiness"],
                "Score Contribution": [student_row['Acad_Contribution'], student_row['Att_Contribution'], student_row['Place_Contribution']],
                "Max Possible": [40, 30, 30]
            })
            
            fig2 = px.bar(breakdown_data, x="Indicator Category", y=["Score Contribution", "Max Possible"], 
                         barmode="group", title=f"Score Composition Drivers for {selected_student_name}")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.markdown("---")
        st.subheader("🤖 Actionable Intelligence & Prescriptive Interventions")
        
        if "High Academic / Low Placement Readiness" in student_row['Segment']:
            st.info(f"💡 **Action Recommendation:** {student_row['Name']} has strong grades but is struggling with career readiness. **Action:** Mandate enrollment in Mock Technical Interview.")
        elif "Critical Academic Support Needed" in student_row['Segment'] or "High Risk" in student_row['Risk Level']:
            st.error(f"🚨 **Action Recommendation:** Critical performance collapse detected. **Action:** Auto-schedule parent-teacher meeting and trigger remedial track.")
        elif "High Potential / Low Engagement" in student_row['Segment']:
            st.warning(f"⚠️ **Action Recommendation:** High academic capacity but failing attendance. **Action:** Counselor to check for engagement issues.")
        else:
            st.success(f"🟢 **Action Recommendation:** Maintaining solid metrics. **Action:** Clear for placement drives.")

    # ==================== PAGE 4: USER LOGIN PROFILE ====================
    elif app_mode == "My Login Profile":
        st.header(f"👤 Logged-in Profile: {user['username']}")
        st.subheader("Active Session Metadata")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Student ID", user['student_id'] if 'student_id' in user else "STU-NEW")
        c2.metric("Email Address", user['email'])
        c3.metric("Role", user['role'])

        st.markdown("---")
        st.subheader("🕒 Login Logs History")
        st.dataframe(get_user_login_history(user['username']), use_container_width=True)