
import streamlit as st

st.set_page_config(
    page_title="CoreKnow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# GROUPED NAVIGATION
# ---------------------------------------------------
pages = {
    "🧠 CoreKnow Brain": [
        st.Page("pages/1_CoreKnow_Brain.py", title="Home", icon="🏠", default=True),
    ],
    "🎓 CoreKnow Student": [
        st.Page("pages/10_CoreKnow_Student.py", title="Student Hub", icon="🎓"),
    ],
    "📚 Exams": [
        st.Page("pages/11_JAMB.py", title="JAMB", icon="📕"),
        st.Page("pages/12_WAEC.py", title="WAEC", icon="📘"),
        st.Page("pages/13_GCE.py", title="GCE", icon="📗"),
        st.Page("pages/14_NECO.py", title="NECO", icon="🏫"),
    ],
    "✏️ Study Tools": [
        st.Page("pages/17_Practice.py", title="Basic Practice", icon="✏️"),
        st.Page("pages/18_AI_Practice.py", title="AI Practice (50 Qs)", icon="🧠"),
        st.Page("pages/19_CoreKnow_Chat.py", title="Ask CoreKnow", icon="💬"),
        st.Page("pages/20_Exam_Mode.py", title="Exam Mode", icon="📝"),
    ],
    "🔬 Research Tools": [
        st.Page("research/3_Deep_Search.py", title="Deep Search", icon="🔍"),
        st.Page("research/4_Browse_Knowledge.py", title="Browse Knowledge", icon="📚"),
        st.Page("research/5_Worker_Progress.py", title="Worker Progress", icon="📊"),
        st.Page("research/6_Drug_Discovery.py", title="Drug Discovery", icon="💊"),
        st.Page("research/7_Query.py", title="Query", icon="🔎"),
        st.Page("research/8_Engineering.py", title="Engineering", icon="⚙️"),
        st.Page("research/9_Breast_Cancer.py", title="Breast Cancer", icon="🎗️"),
    ],
}

pg = st.navigation(pages)
pg.run()
