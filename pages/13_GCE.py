import streamlit as st
import sys, os

from utils.student_sidebar import render_student_sidebar

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

st.set_page_config(page_title="GCE", page_icon="📗", layout="wide")

render_student_sidebar()
apply_theme()

st.markdown('<div class="ck-title">📗 GCE</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">Coming soon — content is being prepared</div>', unsafe_allow_html=True)

st.info("📚 This section is being populated. **JAMB → Chemistry** is fully ready with 18 topics.")
st.markdown("### 🚀 What's Coming")
st.markdown("- All subjects for GCE")
st.markdown("- Full lessons, video solutions, and practice questions")
st.markdown("- Handwritten answer grading")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
