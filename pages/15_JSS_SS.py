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

st.set_page_config(page_title="JSS1–SS3", page_icon="🏫", layout="wide")
apply_theme()

st.markdown('<div class="ck-title">🏫 JSS1 – SS3</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">Term-by-term curriculum · Pick your class, term and subject</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎓 CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)

st.markdown("### 🎯 Select Your Class, Term & Subject")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### 1️⃣ Class")
    student_class = st.selectbox("Class", ["JSS1","JSS2","JSS3","SS1","SS2","SS3"], label_visibility="collapsed")
with c2:
    st.markdown("#### 2️⃣ Term")
    term = st.selectbox("Term", ["First Term","Second Term","Third Term"], label_visibility="collapsed")
with c3:
    st.markdown("#### 3️⃣ Subject")
    subject = st.selectbox("Subject",
        ["Mathematics","English Language","Basic Science","Basic Technology",
         "Social Studies","Civic Education","Business Studies","Physics","Chemistry",
         "Biology","Further Mathematics","Economics","Government","Literature in English",
         "Christian Religious Studies","Islamic Religious Studies","Agricultural Science",
         "Computer Science","Geography"],
        label_visibility="collapsed")

st.markdown("---")
st.markdown("### 📚 " + student_class + " · " + term + " · " + subject)

st.info("📭 Content for **" + student_class + " · " + term + " · " + subject + "** is being prepared.")

st.markdown("#### 📝 What will appear here:")
st.markdown("- **Week 1–12** topics from the official scheme of work")
st.markdown("- **Full lesson** for each topic")
st.markdown("- **Class work** and homework")
st.markdown("- **Term exam** practice")
st.markdown("- **Progress tracker** for the term")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
