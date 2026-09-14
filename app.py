import streamlit as st

st.set_page_config(
    page_title="CoreKnow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------
# SIDEBAR — fully hidden when closed, full when open
# ---------------------------------------------------
st.markdown("""
<style>
    /* =========================================================
       CLOSED STATE — sidebar completely off-screen
       ========================================================= */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
        margin-left: -320px !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* =========================================================
       OPEN STATE — sidebar full width, standard Streamlit
       ========================================================= */
    section[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        margin-left: 0 !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background: #141420 !important;
        border-right: 1px solid #2a2a3a !important;
        z-index: 999998 !important;
    }

    @media (max-width: 768px) {
        section[data-testid="stSidebar"][aria-expanded="true"] {
            width: 85vw !important;
            min-width: 85vw !important;
            max-width: 85vw !important;
        }
    }

    /* =========================================================
       TOGGLE BUTTON — always floating top-left, big, blue
       ========================================================= */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 999999 !important;
        background: #4d6bfe !important;
        border: 2px solid #7c8fff !important;
        border-radius: 12px !important;
        padding: 6px !important;
        box-shadow: 0 4px 16px rgba(77,107,254,0.7) !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1.4rem !important;
        padding: 6px 10px !important;
        cursor: pointer !important;
        min-height: 40px !important;
        min-width: 40px !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg path {
        fill: #ffffff !important;
        color: #ffffff !important;
        width: 26px !important;
        height: 26px !important;
    }

    /* =========================================================
       CLOSE BUTTON — inside sidebar, big, blue, easy to tap
       ========================================================= */
    [data-testid="stSidebarCollapseButton"] {
        display: block !important;
        visibility: visible !important;
        background: #4d6bfe !important;
        border: 2px solid #7c8fff !important;
        border-radius: 12px !important;
        margin: 10px !important;
        padding: 4px !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(77,107,254,0.6) !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        cursor: pointer !important;
        min-height: 40px !important;
        min-width: 40px !important;
    }
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg path {
        fill: #ffffff !important;
        color: #ffffff !important;
        width: 22px !important;
        height: 22px !important;
    }

    /* =========================================================
       MAIN CONTENT — full width when sidebar closed
       ========================================================= */
    section.main,
    .main {
        margin-left: 0 !important;
        transition: margin-left 0.2s !important;
    }

    /* =========================================================
       NAV ITEMS — cards when sidebar is open
       ========================================================= */
    [data-testid="stSidebarNav"] ul {
        padding: 0 !important;
        margin: 0 !important;
        list-style: none !important;
    }
    [data-testid="stSidebarNav"] li {
        margin: 2px 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
        min-height: 44px !important;
    }
    [data-testid="stSidebarNav"] a * {
        color: #e8e8ed !important;
    }
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNav"] a:active {
        background: #2d2d40 !important;
        border-color: #4d6bfe !important;
    }

    /* Active page = full blue */
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

    /* Group headers */
    [data-testid="stSidebarNav"] p {
        color: #8b8b9e !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }

    /* Custom buttons in sidebar */
    [data-testid="stSidebar"] .stButton > button {
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
