import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# Page Configuration
st.set_page_config(
    page_title="Smart Campus AI — Mock Interview",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .stApp { background-color: #0f172a; color: #f8fafc; }
        .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE MANAGEMENT
# ---------------------------------------------------------
if 'current_q_idx' not in st.session_state:
    st.session_state.current_q_idx = 0

questions = [
    "1. Tell me about yourself and your experience with software engineering or data projects.",
    "2. Describe a challenging technical problem you solved. What approach did you take?",
    "3. How do you handle tight deadlines or conflicting project priorities in a team?",
    "4. Where do you see yourself professionally in the next 3 to 5 years?"
]

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("⚙️ System Controls")
st.sidebar.markdown("---")
option = st.sidebar.radio("Navigation", ["🎥 Mock Interview Portal", "📁 Saved Recordings"])

# ---------------------------------------------------------
# MOCK INTERVIEW PORTAL (PAGE 1)
# ---------------------------------------------------------
if option == "🎥 Mock Interview Portal":
    st.title("Smart Campus AI — Mock Interview Portal")
    
    col1, col2 = st.columns([1.2, 1])

    # LEFT SIDE: HTML5 WEBCAM & AUDIO/VIDEO RECORDER (EMBEDDED DIRECTLY IN STREAMLIT)
    with col1:
        st.subheader("📹 Live Webcam Feed & Recording")
        
        # Embedded HTML/JS MediaRecorder (Runs in-browser)
        webcam_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { background-color: #0f172a; color: white; font-family: sans-serif; margin: 0; }
                #videoPreview { width: 100%; max-width: 640px; height: 380px; background-color: #1e293b; border: 2px solid #334155; border-radius: 12px; transform: scaleX(-1); }
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

                // Access User Webcam & Microphone
                navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                    .then(stream => {
                        videoElement.srcObject = stream;
                        statusLabel.innerText = "STATUS: Camera & Microphone Ready";
                        statusLabel.style.color = "#94a3b8";

                        mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });

                        mediaRecorder.ondataavailable = event => {
                            if (event.data.size > 0) recordedChunks.push(event.data);
                        };

                        mediaRecorder.onstop = () => {
                            const blob = new Blob(recordedChunks, { type: 'video/mp4' });
                            const url = URL.createObjectURL(blob);
                            
                            // Download recorded MP4 file
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = 'interview_recording.mp4';
                            a.click();

                            statusLabel.innerText = "STATUS: ✅ Session Saved as interview_recording.mp4";
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
                    btnStart.disabled = true;
                    btnStart.style.opacity = "0.5";
                    btnStop.disabled = false;
                    btnStop.style.opacity = "1";
                }

                function stopRecording() {
                    mediaRecorder.stop();
                    btnStart.disabled = false;
                    btnStart.style.opacity = "1";
                    btnStop.disabled = true;
                    btnStop.style.opacity = "0.5";
                }
            </script>
        </body>
        </html>
        """
        
        # Render Component inside Streamlit Layout
        components.html(webcam_html, height=520)

    # RIGHT SIDE: QUESTION NAVIGATION AND CANDIDATE NOTES
    with col2:
        st.markdown("<h4 style='color: #38bdf8;'>INTERVIEW QUESTION</h4>", unsafe_allow_html=True)
        
        # Render Question Box
        st.info(f"**{questions[st.session_state.current_q_idx]}**")

        st.markdown("<h5 style='color: #94a3b8;'>Candidate Notes / Key Answer Points</h5>", unsafe_allow_html=True)
        notes = st.text_area(
            "Type bullet points or thoughts for your answer here...",
            height=200,
            key=f"notes_{st.session_state.current_q_idx}"
        )

        # Prev / Next Navigation Buttons
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("◀️ Previous Question", use_container_width=True):
                if st.session_state.current_q_idx > 0:
                    st.session_state.current_q_idx -= 1
                    st.rerun()

        with btn_col2:
            if st.button("Next Question ▶️", use_container_width=True):
                if st.session_state.current_q_idx < len(questions) - 1:
                    st.session_state.current_q_idx += 1
                    st.rerun()

# ---------------------------------------------------------
# SAVED RECORDINGS PAGE (PAGE 2)
# ---------------------------------------------------------
elif option == "📁 Saved Recordings":
    st.title("📁 Interview Recordings")
    st.write("Aapki recorded MP4 videos yahan preview karne ke liye available hongi.")
    
    if os.path.exists("interview_recording.mp4"):
        st.video("interview_recording.mp4")
    else:
        st.info("Abhi tak koi recording save nahi hui hai.")