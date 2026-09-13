import streamlit as st
import sys, os

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from utils.student_style import apply_theme
except Exception:
    def apply_theme():
        st.markdown("<style>.stApp{background:#0d1b2a;color:#e0e0e0;} header,footer{visibility:hidden;} .ck-title{font-size:2.5rem;font-weight:900;text-align:center;color:#00e5ff;} .ck-sub{text-align:center;color:#8892b0;margin-bottom:2rem;} .topic-card{background:#111827;border-left:4px solid #00e5ff;border-radius:8px;padding:1rem;margin:0.6rem 0;} .topic-title{font-weight:600;color:#e0e0e0;} .topic-meta{color:#8892b0;font-size:0.85rem;}</style>", unsafe_allow_html=True)

from supabase import create_client

st.set_page_config(page_title="JAMB", page_icon="📕", layout="wide")
apply_theme()

# Connect to Supabase
try:
    supabase = create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["service_key"]
    )
except Exception as e:
    st.error("Supabase connection failed: " + str(e))
    st.stop()

st.markdown('<div class="ck-title">📕 JAMB</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">UTME Preparation · Pick a subject to begin</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎓 CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)

# Load all JAMB topics from Supabase
try:
    res = supabase.table("education_syllabi").select("id, subject, topic_number, topic_title, subtopics, learning_objectives").eq("exam", "JAMB").order("subject").order("topic_number").execute()
    all_topics = res.data if res.data else []
except Exception as e:
    st.error("Failed to load syllabus: " + str(e))
    st.stop()

if not all_topics:
    st.warning("📭 No JAMB syllabus loaded yet.")
    st.info("Run the ingestion cell in Colab to load the syllabus.")
    st.stop()

# Group topics by subject
subjects = sorted(set(t["subject"] for t in all_topics))

# Subject selector
subject = st.selectbox("📖 Select Subject", subjects, index=0)

# Filter topics for this subject
topics = [t for t in all_topics if t["subject"] == subject]

# Load lessons map
try:
    lessons_res = supabase.table("education_lessons").select("syllabus_id, lesson_text").execute()
    lesson_map = {l["syllabus_id"]: l["lesson_text"] for l in lessons_res.data}
except:
    lesson_map = {}

st.markdown("### 📋 " + subject + " — " + str(len(topics)) + " Topics")

# Render each topic
for t in topics:
    n = t["topic_number"]
    subs = t.get("subtopics") or []
    objs = t.get("learning_objectives") or []
    has_lesson = t["id"] in lesson_map

    status = "✅ Lesson Ready" if has_lesson else "📝 Coming Soon"

    st.markdown(
        '<div class="topic-card">'
        '<div class="topic-title">[' + str(n).zfill(2) + '] ' + str(t["topic_title"]) + '</div>'
        '<div class="topic-meta">📌 ' + str(len(subs)) + ' subtopics · 🎯 ' + str(len(objs)) + ' objectives · ' + status + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.expander("Open Topic " + str(n) + " →", expanded=False):
        st.markdown("#### 🎯 Learning Objectives")
        for obj in objs:
            st.markdown("- " + str(obj))

        st.markdown("#### 📌 Subtopics")
        for s in subs:
            st.markdown("- " + str(s))

        # Render the lesson if it exists
        if has_lesson:
            st.markdown("---")
            st.markdown("#### 📖 Full Lesson")
            st.markdown(lesson_map[t["id"]])
        else:
            st.info("📝 Full lesson content coming soon.")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
