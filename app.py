import streamlit as st

st.set_page_config(
    page_title="CoreKnow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------
# FORCE SIDEBAR VISIBLE + CLICKABLE NAV
# ---------------------------------------------------
st.markdown("""
<style>
    /* ---- 1. Force sidebar always expanded ---- */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        background: #141420 !important;
        border-right: 1px solid #2a2a3a !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }

    /* ---- 2. Hide the collapse/close button ---- */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    button[kind="header"] {
        display: none !important;
    }

    /* ---- 3. Force main content to respect sidebar ---- */
    .main .block-container,
    section.main .block-container {
        margin-left: 0 !important;
    }

    /* ---- 4. Sidebar nav container ---- */
    [data-testid="stSidebarNav"] {
        display: block !important;
        visibility: visible !important;
        padding: 0.5rem 0 !important;
    }
    [data-testid="stSidebarNav"] ul {
        padding: 0 !important;
        margin: 0 !important;
        list-style: none !important;
        display: block !important;
    }
    [data-testid="stSidebarNav"] li {
        display: block !important;
        margin: 2px 0 !important;
        padding: 0 !important;
    }

    /* ---- 5. Every nav link = big obvious tappable card ---- */
    [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: #21212d !important;
        border: 1px solid #3a3a4d !important;
        border-left: 4px solid #4d6bfe !important;
        border-radius: 10px !important;
        padding: 0.8rem 1rem !important;
        margin: 4px 8px !important;
        text-decoration: none !important;
        color: #e8e8ed !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.15s !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
        min-height: 44px !important;
        box-sizing: border-box !important;
    }
    [data-testid="stSidebarNav"] a * {
        color: #e8e8ed !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #2d2d40 !important;
        border-color: #4d6bfe !important;
        border-left-color: #7c8fff !important;
        transform: translateX(2px);
    }

    /* ---- 6. Active page = full blue, unmissable ---- */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, #4d6bfe 0%, #3a56e0 100%) !important;
        border-color: #4d6bfe !important;
        border-left-color: #ffffff !important;
        box-shadow: 0 3px 14px rgba(77,107,254,0.6) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* ---- 7. Group headers ---- */
    [data-testid="stSidebarNav"] > ul > li > div > span,
    [data-testid="stSidebarNav"] header,
    [data-testid="stSidebarNav"] p {
        color: #8b8b9e !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* ---- 8. Custom buttons in sidebar ---- */
    [data-testid="stSidebar"] .stButton > button {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: #21212d !important;
        border: 1px solid #3a3a4d !important;
        border-left: 4px solid #4d6bfe !important;
        color: #e8e8ed !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 10px !important;
        padding: 0.8rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        margin-bottom: 0.4rem !important;
        min-height: 44px !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #2d2d40 !important;
        border-color: #4d6bfe !important;
        color: #ffffff !important;
    }

    /* ---- 9. MOBILE: force sidebar to overlay, not hide ---- */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] {
            width: 85vw !important;
            min-width: 85vw !important;
            max-width: 85vw !important;
        }
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
