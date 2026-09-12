import streamlit as st
import sys, os

# Ensure repo root is on path
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from utils.student_style import apply_theme
except Exception:
    def apply_theme():
        st.markdown("""
        <style>
            .stApp { background: #0d1b2a; color: #e0e0e0; }
            header, footer { visibility: hidden; }
            .ck-title { font-size: 2.5rem; font-weight: 900; text-align: center; color: #00e5ff; }
            .ck-sub { text-align: center; color: #8892b0; margin-bottom: 2rem; }
            .topic-card { background: #111827; border-left: 4px solid #00e5ff; border-radius: 8px; padding: 1rem; margin: 0.6rem 0; }
            .topic-title { font-weight: 600; color: #e0e0e0; }
            .topic-meta { color: #8892b0; font-size: 0.85rem; }
        </style>
        """, unsafe_allow_html=True)

from supabase import create_client

st.set_page_config(page_title="CoreKnow Student", page_icon="🎓", layout="wide")
apply_theme()

SUPABASE_URL = st.secrets["supabase"]["url"]
SERVICE_KEY = st.secrets["supabase"]["service_key"]
supabase = create_client(SUPABASE_URL, SERVICE_KEY)

st.markdown('<div class="ck-title">🎓 COREKNOW STUDENT</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">AI-POWERED TUTOR FOR NIGERIAN STUDENTS</div>', unsafe_allow_html=True)

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
    total_topics = supabase.table("education_syllabi").select("*", count="exact").execute().count or 0
    total_lessons = supabase.table("education_lessons").select("*", count="exact").execute().count or 0
except:
    total_topics = total_lessons = 0

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="stat-box"><div class="stat-num">' + str(total_topics) + '</div><div class="stat-lbl">Topics</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="stat-box"><div class="stat-num">' + str(total_lessons) + '</div><div class="stat-lbl">Lessons</div></div>', unsafe_allow_html=True)

st.markdown("### 🎯 Choose Your Section")

r1 = st.columns(3)
with r1[0]:
    st.markdown('<div class="card"><div class="card-icon">📕</div><div class="card-title">JAMB</div><div class="card-sub">UTME · April/May</div></div>', unsafe_allow_html=True)
    if st.button("Open JAMB →", key="hub_jamb", use_container_width=True):
        st.switch_page("pages/11_JAMB.py")
with r1[1]:
    st.markdown('<div class="card"><div class="card-icon">📘</div><div class="card-title">WAEC</div><div class="card-sub">May/June SSCE</div></div>', unsafe_allow_html=True)
    if st.button("Open WAEC →", key="hub_waec", use_container_width=True):
        st.switch_page("pages/12_WAEC.py")
with r1[2]:
    st.markdown('<div class="card"><div class="card-icon">📗</div><div class="card-title">GCE</div><div class="card-sub">Nov/Dec SSCE</div></div>', unsafe_allow_html=True)
    if st.button("Open GCE →", key="hub_gce", use_container_width=True):
        st.switch_page("pages/13_GCE.py")

r2 = st.columns(3)
with r2[0]:
    st.markdown('<div class="card"><div class="card-icon">📙</div><div class="card-title">NECO</div><div class="card-sub">June/July SSCE</div></div>', unsafe_allow_html=True)
    if st.button("Open NECO →", key="hub_neco", use_container_width=True):
        st.switch_page("pages/14_NECO.py")
with r2[1]:
    st.markdown('<div class="card"><div class="card-icon">🏫</div><div class="card-title">JSS1 – SS3</div><div class="card-sub">Term-by-term curriculum</div></div>', unsafe_allow_html=True)
    if st.button("Open JSS1–SS3 →", key="hub_js", use_container_width=True):
        st.switch_page("pages/15_JSS_SS.py")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
