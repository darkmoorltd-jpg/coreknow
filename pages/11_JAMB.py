import streamlit as st
import sys, os

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from supabase import create_client

st.set_page_config(page_title="JAMB", page_icon="📕", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 0%, #0d1b2a 0%, #050810 100%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background: #0a0e17; border-right: 1px solid #1f2a44; }

    .ck-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 50%, #ff1744 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .ck-sub { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }

    .topic-tile {
        background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
        border: 2px solid #1f2a44;
        border-left: 5px solid #00e5ff;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        transition: all 0.3s;
    }
    .topic-tile:hover {
        border-color: #00e5ff;
        border-left-color: #ffd700;
        box-shadow: 0 0 25px rgba(0,229,255,0.25);
        transform: translateX(5px);
    }
    .topic-number {
        font-family: 'Orbitron', monospace;
        font-size: 1.5rem;
        color: #ffd700;
        font-weight: 700;
        margin-right: 0.8rem;
    }
    .topic-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #e0e0e0;
        display: inline;
    }
    .topic-meta {
        color: #8892b0;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    .status-ready { color: #00c853; font-weight: 600; }
    .status-pending { color: #ff9800; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_key"])
except Exception as e:
    st.error("Supabase connection failed: " + str(e))
    st.stop()

st.markdown('<div class="ck-title">📕 JAMB</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">UTME PREPARATION · CLICK A TOPIC TO OPEN LESSON</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎓 CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)

try:
    res = supabase.table("education_syllabi").select("id, subject, topic_number, topic_title, subtopics, learning_objectives").eq("exam", "JAMB").order("subject").order("topic_number").execute()
    all_topics = res.data if res.data else []
except Exception as e:
    st.error("Failed to load syllabus: " + str(e))
    st.stop()

if not all_topics:
    st.warning("📭 No JAMB syllabus loaded yet.")
    st.stop()

subjects = sorted(set(t["subject"] for t in all_topics))
subject = st.selectbox("📖 Select Subject", subjects, index=0)
topics = [t for t in all_topics if t["subject"] == subject]

try:
    lessons_res = supabase.table("education_lessons").select("syllabus_id").execute()
    lesson_ids = set(l["syllabus_id"] for l in lessons_res.data)
except:
    lesson_ids = set()

st.markdown("### 📋 " + subject + " — " + str(len(topics)) + " Topics")

for t in topics:
    n = t["topic_number"]
    subs = t.get("subtopics") or []
    objs = t.get("learning_objectives") or []
    ready = t["id"] in lesson_ids

    status_html = '<span class="status-ready">✅ Lesson Ready</span>' if ready else '<span class="status-pending">📝 Coming Soon</span>'

    st.markdown(
        '<div class="topic-tile">'
        '<span class="topic-number">' + str(n).zfill(2) + '</span>'
        '<span class="topic-title">' + str(t["topic_title"]) + '</span>'
        '<div class="topic-meta">📌 ' + str(len(subs)) + ' subtopics · 🎯 ' + str(len(objs)) + ' objectives · ' + status_html + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("Open →", key="open_" + str(t["id"]), use_container_width=True):
            st.session_state.selected_topic_id = t["id"]
            st.session_state.selected_exam = "JAMB"
            st.session_state.selected_subject = subject
            st.switch_page("pages/16_Topic_View.py")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
