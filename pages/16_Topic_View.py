import streamlit as st
import sys, os

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from supabase import create_client

st.set_page_config(page_title="Lesson", page_icon="📖", layout="wide")

# ============================================
# BEAUTIFUL STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0d1b2a 0%, #050810 100%);
        color: #e0e0e0;
    }
    header, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background: #0a0e17; border-right: 1px solid #1f2a44; }

    /* Hero header */
    .lesson-hero {
        background: linear-gradient(135deg, #0a1428 0%, #111c33 50%, #0a1428 100%);
        border: 1px solid #1f2a44;
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .lesson-hero::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #00e5ff, #7c4dff, #ff1744, transparent);
    }
    .lesson-tag {
        display: inline-block;
        background: rgba(0,229,255,0.1);
        border: 1px solid #00e5ff;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        color: #00e5ff;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
    }
    .lesson-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    .lesson-meta {
        display: flex;
        gap: 2rem;
        margin-top: 1rem;
        color: #8892b0;
        font-size: 0.9rem;
    }
    .lesson-meta span { display: flex; align-items: center; gap: 0.4rem; }

    /* Progress bar */
    .progress-bar {
        height: 6px;
        background: #0d1117;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 1rem;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00e5ff, #7c4dff);
        border-radius: 3px;
        width: 15%;
    }

    /* Sidebar cards */
    .mini-topic {
        background: #0d1117;
        border-left: 3px solid #1f2a44;
        border-radius: 6px;
        padding: 0.6rem 0.9rem;
        margin: 0.3rem 0;
        font-size: 0.85rem;
        color: #8892b0;
        transition: all 0.2s;
    }
    .mini-topic.active {
        border-left-color: #00e5ff;
        background: rgba(0,229,255,0.08);
        color: #e0e0e0;
    }
    .mini-topic:hover { border-left-color: #00e5ff; }

    /* Nav buttons */
    .nav-btn-row {
        display: flex;
        gap: 1rem;
        justify-content: space-between;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #1f2a44;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONNECT
# ============================================
try:
    supabase = create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["service_key"]
    )
except Exception as e:
    st.error("Supabase connection failed: " + str(e))
    st.stop()

# ============================================
# GET SELECTED TOPIC
# ============================================
topic_id = st.session_state.get("selected_topic_id")
exam = st.session_state.get("selected_exam", "JAMB")
subject = st.session_state.get("selected_subject", "Chemistry")

if topic_id is None:
    st.warning("No topic selected. Please go back and choose a topic.")
    if st.button("← Back to JAMB"):
        st.switch_page("pages/11_JAMB.py")
    st.stop()

# ============================================
# FETCH TOPIC + LESSON
# ============================================
try:
    topic_res = supabase.table("education_syllabi").select("*").eq("id", topic_id).execute()
    if not topic_res.data:
        st.error("Topic not found.")
        st.stop()
    topic = topic_res.data[0]
except Exception as e:
    st.error("Failed to load topic: " + str(e))
    st.stop()

# Fetch lesson
lesson_text = None
try:
    lesson_res = supabase.table("education_lessons").select("lesson_text").eq("syllabus_id", topic_id).execute()
    if lesson_res.data:
        lesson_text = lesson_res.data[0]["lesson_text"]
except:
    pass

# Fetch all topics in this subject for sidebar navigation
try:
    siblings_res = supabase.table("education_syllabi").select("id, topic_number, topic_title").eq("exam", exam).eq("subject", subject).order("topic_number").execute()
    siblings = siblings_res.data if siblings_res.data else []
except:
    siblings = []

# ============================================
# SIDEBAR NAVIGATION
# ============================================
with st.sidebar:
    st.markdown("## 🎓 " + exam + " " + subject)
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)
    st.markdown("---")
    st.markdown("### 📚 Topics")

    current_n = topic["topic_number"]
    for sib in siblings:
        is_active = sib["id"] == topic_id
        marker = "▶" if is_active else "•"
        label = str(sib["topic_number"]).zfill(2) + ". " + sib["topic_title"][:35]
        if is_active:
            st.markdown('<div class="mini-topic active">' + marker + " " + label + '</div>', unsafe_allow_html=True)
        else:
            if st.button(marker + " " + label, key="nav_" + str(sib["id"]), use_container_width=True):
                st.session_state.selected_topic_id = sib["id"]
                st.rerun()

# ============================================
# HERO HEADER
# ============================================
subs = topic.get("subtopics") or []
objs = topic.get("learning_objectives") or []

st.markdown(
    '<div class="lesson-hero">'
    '<div class="lesson-tag">' + exam + ' · ' + subject + ' · Topic ' + str(topic["topic_number"]).zfill(2) + '</div>'
    '<div class="lesson-title">' + str(topic["topic_title"]) + '</div>'
    '<div class="lesson-meta">'
    '<span>📌 ' + str(len(subs)) + ' subtopics</span>'
    '<span>🎯 ' + str(len(objs)) + ' objectives</span>'
    '<span>' + ('✅ Lesson available' if lesson_text else '📝 Coming soon') + '</span>'
    '</div>'
    '<div class="progress-bar"><div class="progress-fill"></div></div>'
    '</div>',
    unsafe_allow_html=True
)

# ============================================
# TABS: Lesson, Objectives, Practice
# ============================================
tab1, tab2, tab3 = st.tabs(["📖 Lesson", "🎯 Objectives & Subtopics", "✏️ Practice"])

with tab1:
    if lesson_text:
        st.markdown(lesson_text)
    else:
        st.info("📝 Full lesson content is being prepared. Check back soon!")
        st.markdown("### 📌 What will appear here")
        st.markdown("- Complete explanation of every subtopic")
        st.markdown("- Worked examples with step-by-step solutions")
        st.markdown("- Formulas and symbol definitions")
        st.markdown("- Common JAMB traps and how to avoid them")

with tab2:
    st.markdown("### 🎯 Learning Objectives")
    for obj in objs:
        st.markdown("- " + str(obj))

    st.markdown("### 📌 Subtopics Covered")
    for s in subs:
        st.markdown("- " + str(s))

    if topic.get("contents_notes"):
        st.markdown("### 📝 Notes")
        st.markdown(str(topic["contents_notes"]))

with tab3:
    st.markdown("### ✏️ Practice Questions")
    st.info("🧠 Practice mode coming soon — AI-generated MCQs with instant grading.")
    if st.button("Generate 5 Practice Questions", type="primary", use_container_width=True):
        st.info("This will use DeepSeek API to generate questions. Coming soon.")

# ============================================
# BOTTOM NAVIGATION
# ============================================
current_idx = next((i for i, s in enumerate(siblings) if s["id"] == topic_id), None)

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if current_idx is not None and current_idx > 0:
        prev_topic = siblings[current_idx - 1]
        if st.button("← Prev: " + prev_topic["topic_title"][:25], use_container_width=True):
            st.session_state.selected_topic_id = prev_topic["id"]
            st.rerun()

with col2:
    if st.button("📚 All Topics", use_container_width=True):
        st.switch_page("pages/11_JAMB.py")

with col3:
    if current_idx is not None and current_idx < len(siblings) - 1:
        next_topic = siblings[current_idx + 1]
        if st.button("Next: " + next_topic["topic_title"][:25] + " →", use_container_width=True):
            st.session_state.selected_topic_id = next_topic["id"]
            st.rerun()

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
