
import streamlit as st


def render_student_sidebar():
    """Shared student sidebar. Uses try/except so a missing page never breaks the sidebar."""

    with st.sidebar:
        st.markdown("## CoreKnow Student")
        st.markdown("---")

        st.markdown("### Main")
        _safe_page_link("pages/10_CoreKnow_Student.py", "Home")
        _safe_page_link("pages/11_JAMB.py", "JAMB")
        _safe_page_link("pages/12_WAEC.py", "WAEC")
        _safe_page_link("pages/13_GCEAI Practice.py", "GCE")
        _safe_page_link("pages/14_NECO.py", "NECO")
        _safe_page_link("pages/15_JSS_SS.py", "JSS1-SS3")

        st.markdown("---")
        st.markdown("### Study Tools")
        _safe_page_link("pages/17_Practice.py", "Basic Practice")
        _safe_page_link("pages/18_AI_Practice.py", " (50 Qs)")
        _safe_page_link("pages/19_CoreKnow_Chat.py", "Ask CoreKnow")
        _safe_page_link("pages/20_Exam_Mode.py", "Exam Mode")

        st.markdown("---")
        st.markdown("### Knowledge Tools")
        _safe_page_link("pages/3_Deep_Search.py", "Deep Search")
        _safe_page_link("pages/4_Browse_Knowledge.py", "Browse Knowledge")
        _safe_page_link("pages/6_Drug_Discovery.py", "Drug Discovery")
        _safe_page_link("pages/7_Query.py", "Query")


def _safe_page_link(page_path, label):
    """Try st.page_link; if it fails, show a plain markdown link as fallback."""
    try:
        st.page_link(page_path, label=label, use_container_width=True)
    except Exception:
        # Fallback: convert to markdown navigation link
        slug = page_path.replace("pages/", "").replace(".py", "")
        st.markdown("- " + label)
