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

try:
    from utils.student_curriculum import CURRICULUM
except Exception:
    CURRICULUM = {}

st.set_page_config(page_title="JAMB", page_icon="📕", layout="wide")
apply_theme()

st.markdown('<div class="ck-title">📕 JAMB</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">UTME Preparation · Pick a subject to begin</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎓 CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)

subjects = list(CURRICULUM.keys()) if CURRICULUM else []

if not subjects:
    st.warning("📭 No subjects loaded yet.")
    st.stop()

subject = st.selectbox("📖 Select Subject", subjects, index=0)

if subject:
    topics = CURRICULUM.get(subject, [])
    st.markdown("### 📋 " + subject + " — " + str(len(topics)) + " Topics")

    for t in topics:
        objs = t.get("objectives", [])
        subs = t.get("subtopics", [])

        st.markdown(
            '<div class="topic-card">'
            '<div class="topic-title">[' + str(t["n"]).zfill(2) + '] ' + str(t["title"]) + '</div>'
            '<div class="topic-meta">📌 ' + str(len(subs)) + ' subtopics · 🎯 ' + str(len(objs)) + ' objectives</div>'
            '</div>',
            unsafe_allow_html=True
        )

        with st.expander("Open Topic " + str(t["n"]) + " →", expanded=False):
            st.markdown("#### 🎯 Learning Objectives")
            for o in objs:
                st.markdown("- " + str(o))

            st.markdown("#### 📌 Subtopics")
            for s in subs:
                st.markdown("- " + str(s))

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📖 Read Lesson", key="lesson_" + str(t["n"])):
                    st.info("📝 Full lesson content coming soon.")
            with col2:
                if st.button("✏️ Practice", key="prac_" + str(t["n"])):
                    st.info("✏️ Practice questions coming soon.")
            with col3:
                if st.button("📝 Mark Done", key="done_" + str(t["n"])):
                    st.success("✅ Progress saved (demo)")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
