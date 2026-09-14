
import streamlit as st
from utils.student_sidebar import render_student_sidebar

st.set_page_config(
    page_title="CoreKnow Student",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# GROUPED NAVIGATION
# ---------------------------------------------------
pages = {
    "CoreKnow Student": [
        st.Page("pages/10_CoreKnow_Student.py", title="Home", icon="🏠", default=True),
    ],
    "Exams": [
        st.Page("pages/11_JAMB.py", title="JAMB", icon="📕"),
        st.Page("pages/12_WAEC.py", title="WAEC", icon="📘"),
        st.Page("pages/13_GCE.py", title="GCE", icon="📗"),
        st.Page("pages/14_NECO.py", title="NECO", icon="📙"),
        st.Page("pages/15_JSS_SS.py", title="JSS1 - SS3", icon="🏫"),
    ],
    "Study Tools": [
        st.Page("pages/17_Practice.py", title="Basic Practice", icon="✏️"),
        st.Page("pages/18_AI_Practice.py", title="AI Practice (50 Qs)", icon="🧠"),
        st.Page("pages/19_CoreKnow_Chat.py", title="Ask CoreKnow", icon="💬"),
        st.Page("pages/20_Exam_Mode.py", title="Exam Mode", icon="📝"),
    ],
}

pg = st.navigation(pages)
pg.run()
