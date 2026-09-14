import streamlit as st

st.set_page_config(
    page_title="CoreKnow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------
# GLOBAL SIDEBAR STYLING — runs on every page
# ---------------------------------------------------
st.markdown("""
<style>
    /* --- Sidebar container --- */
    [data-testid="stSidebar"] {
        background: #141420 !important;
        border-right: 1px solid #2a2a3a !important;
    }
    [data-testid="stSidebar"] * { color: #e8e8ed; }

    /* --- Group headers (Home, Exams, Study Tools, ...) --- */
    [data-testid="stSidebarNav"] > ul > li > div > span,
    [data-testid="stSidebarNav"] > div > div > div > div > span,
    [data-testid="stSidebarNav"] [data-testid="stMarkdownContainer"] > p {
        color: #8b8b9e !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.4px !important;
        text-transform: uppercase !important;
        padding: 0.9rem 0.6rem 0.35rem 0.6rem !important;
        margin: 0 !important;
    }

    /* --- Every nav link = solid card --- */
    [data-testid="stSidebarNav"] a {
        background: #21212d !important;
        border: 1px solid #3a3a4d !important;
        border-left: 3px solid #4d6bfe !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.85rem !important;
        margin: 3px 6px !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        text-decoration: none !important;
        transition: all 0.15s !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
        cursor: pointer !important;
        color: #e8e8ed !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #2d2d40 !important;
        border-color: #4d6bfe !important;
        border-left-color: #7c8fff !important;
        transform: translateX(2px);
        box-shadow: 0 3px 10px rgba(77,107,254,0.4) !important;
    }
    [data-testid="stSidebarNav"] a:hover span,
    [data-testid="stSidebarNav"] a:hover p,
    [data-testid="stSidebarNav"] a:hover div {
        color: #ffffff !important;
    }

    /* --- Currently active page = full blue --- */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, #4d6bfe 0%, #3a56e0 100%) !important;
        border-color: #4d6bfe !important;
        border-left-color: #ffffff !important;
        box-shadow: 0 3px 12px rgba(77,107,254,0.5) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebarNav"] a[aria-current="page"] p,
    [data-testid="stSidebarNav"] a[aria-current="page"] div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* --- Custom buttons inside sidebar (New chat, etc.) --- */
    [data-testid="stSidebar"] .stButton > button {
        background: #21212d !important;
        border: 1px solid #3a3a4d !important;
        border-left: 3px solid #4d6bfe !important;
        color: #e8e8ed !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 10px !important;
        padding: 0.7rem 0.9rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.15s !important;
        width: 100% !important;
        margin-bottom: 0.35rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #2d2d40 !important;
        border-color: #4d6bfe !important;
        color: #ffffff !important;
        transform: translateX(2px);
        box-shadow: 0 3px 10px rgba(77,107,254,0.35) !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# GROUPED NAVIGATION
# ---------------------------------------------------
pages = {
    "🏠 Home": [
        st.Page("pages/19_CoreKnow_Chat.py", title="Ask CoreKnow", icon="💬", default=True),
    ],
    "🎓 CoreKnow Student": [
        st.Page("pages/10_CoreKnow_Student.py", title="Student Hub", icon="🎓"),
    ],
    "📚 Exams": [
        st.Page("pages/11_JAMB.py", title="JAMB", icon="📕"),
        st.Page("pages/12_WAEC.py", title="WAEC", icon="📘"),
        st.Page("pages/13_GCE.py", title="GCE", icon="📗"),
        st.Page("pages/14_NECO.py", title="NECO", icon="📙"),
        st.Page("pages/15_JSS_SS.py", title="JSS1 - SS3", icon="🏫"),
    ],
    "✏️ Study Tools": [
        st.Page("pages/17_Practice.py", title="Basic Practice", icon="✏️"),
        st.Page("pages/18_AI_Practice.py", title="AI Practice (50 Qs)", icon="🧠"),
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
