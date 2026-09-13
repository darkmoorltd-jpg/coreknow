import streamlit as st
import sys, os

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from utils.student_style import apply_theme
except Exception:
    def apply_theme():
        st.markdown("<style>.stApp{background:#0d1b2a;color:#e0e0e0;} header,footer{visibility:hidden;} .ck-title{font-size:2.5rem;font-weight:900;text-align:center;color:#00e5ff;} .ck-sub{text-align:center;color:#8892b0;margin-bottom:2rem;}</style>", unsafe_allow_html=True)

try:
    from utils.student_curriculum import CURRICULUM
except Exception:
    CURRICULUM = {}

st.set_page_config(page_title="WAEC", page_icon="📘", layout="wide")
apply_theme()

st.markdown('<div class="ck-title">📘 WAEC</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">Coming soon — content is being prepared</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎓 CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)

st.info("📚 This section is being populated. **JAMB → Chemistry** is fully ready with 18 topics.")
st.markdown("### 🚀 What's Coming")
st.markdown("- All subjects for WAEC")
st.markdown("- Full lessons, video solutions, and practice questions")
st.markdown("- Handwritten answer grading")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
