
import streamlit as st
from utils.student_style import apply_theme
from supabase import create_client

st.set_page_config(page_title="CoreKnow Student", page_icon="🎓", layout="wide")
apply_theme()

SUPABASE_URL = st.secrets["supabase"]["url"]
SERVICE_KEY = st.secrets["supabase"]["service_key"]
supabase = create_client(SUPABASE_URL, SERVICE_KEY)

st.markdown('<div class="ck-title">🎓 COREKNOW STUDENT</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">AI-POWERED TUTOR FOR NIGERIAN STUDENTS</div>', unsafe_allow_html=True)

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

# Stats
try:
    total_topics = supabase.table("education_syllabi").select("*", count="exact").execute().count or 0
    total_lessons = supabase.table("education_lessons").select("*", count="exact").execute().count or 0
    total_questions = supabase.table("education_questions").select("*", count="exact").execute().count or 0
except:
    total_topics = total_lessons = total_questions = 0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{total_topics}</div><div class="stat-lbl">Topics</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{total_lessons}</div><div class="stat-lbl">Lessons</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{total_questions}</div><div class="stat-lbl">Questions</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🎯 Choose Your Exam or Class")

# Row 1: JAMB, WAEC, GCE
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📕</div>
        <div class="card-title">JAMB</div>
        <div class="card-sub">UTME · April/May</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open JAMB →", key="btn_jamb", use_container_width=True):
        st.switch_page("pages/11_JAMB.py")

with r1c2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📘</div>
        <div class="card-title">WAEC</div>
        <div class="card-sub">May/June SSCE</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open WAEC →", key="btn_waec", use_container_width=True):
        st.switch_page("pages/12_WAEC.py")

with r1c3:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📗</div>
        <div class="card-title">GCE</div>
        <div class="card-sub">Nov/Dec SSCE</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open GCE →", key="btn_gce", use_container_width=True):
        st.switch_page("pages/13_GCE.py")

# Row 2: NECO, JSS1-SS3
r2c1, r2c2, _ = st.columns(3)
with r2c1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📙</div>
        <div class="card-title">NECO</div>
        <div class="card-sub">June/July SSCE</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open NECO →", key="btn_neco", use_container_width=True):
        st.switch_page("pages/14_NECO.py")

with r2c2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">🏫</div>
        <div class="card-title">JSS1 – SS3</div>
        <div class="card-sub">School curriculum by term</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open JSS1–SS3 →", key="btn_js", use_container_width=True):
        st.switch_page("pages/15_JSS_SS.py")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
