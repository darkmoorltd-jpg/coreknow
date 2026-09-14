import streamlit as st

st.set_page_config(
    page_title="CoreKnow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)





# ---------------------------------------------------
# TOP MENU BUTTON — tap to show/hide sidebar
# ---------------------------------------------------
st.markdown("""
<style>
    /* ============================================================
       SIDEBAR: FULLY OFF-SCREEN WHEN CLOSED
       ============================================================ */
    section[data-testid="stSidebar"] {
        background: #141420 !important;
        border-right: 1px solid #2a2a3a !important;
        transition: transform 0.25s ease, margin-left 0.25s ease !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-110%) !important;
        margin-left: -350px !important;
        pointer-events: none !important;
        opacity: 0 !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        margin-left: 0 !important;
        pointer-events: auto !important;
        opacity: 1 !important;
        width: 85vw !important;
        min-width: 85vw !important;
        max-width: 85vw !important;
        z-index: 999998 !important;
    }

    /* ============================================================
       TOP MENU BUTTON — rectangular, top of screen
       ============================================================ */

    /* The OPEN button (shown when sidebar is closed) */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        height: 52px !important;
        background: #4d6bfe !important;
        border: none !important;
        border-bottom: 2px solid #7c8fff !important;
        border-radius: 0 !important;
        padding: 0 !important;
        box-shadow: 0 4px 14px rgba(77,107,254,0.5) !important;
        cursor: pointer !important;
        z-index: 999999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        width: 100% !important;
        height: 100% !important;
        padding: 0 20px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 12px !important;
    }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "☰   MENU" !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        display: none !important;
    }

    /* The CLOSE button (shown when sidebar is open) */
    [data-testid="stSidebarCollapseButton"] {
        background: #4d6bfe !important;
        border-radius: 10px !important;
        margin: 10px 12px !important;
        padding: 6px 14px !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(77,107,254,0.6) !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        cursor: pointer !important;
        min-height: 40px !important;
        font-size: 1rem !important;
    }
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg path {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* ============================================================
       PUSH PAGE CONTENT BELOW THE TOP BAR
       ============================================================ */
    .main .block-container {
        padding-top: 70px !important;
    }

    /* ============================================================
       NAV ITEMS — cards (when sidebar is open)
       ============================================================ */
    [data-testid="stSidebarNav"] ul { padding: 0 !important; margin: 0 !important; list-style: none !important; }
    [data-testid="stSidebarNav"] li { margin: 2px 0 !important; padding: 0 !important; }
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
        min-height: 44px !important;
    }
    [data-testid="stSidebarNav"] a * { color: #e8e8ed !important; }
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNav"] a:active {
        background: #2d2d40 !important;
        border-color: #4d6bfe !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, #4d6bfe 0%, #3a56e0 100%) !important;
        border-color: #4d6bfe !important;
        border-left-color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
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
        st.Page("pages/16_Topic_View.py", title="Topic View", icon="📖"),
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
