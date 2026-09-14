
import streamlit as st
from streamlit import session_state as ss


def render_student_sidebar():
    """Render the shared student sidebar navigation on any page."""

    with st.sidebar:
        st.markdown("## CoreKnow Student")
        st.markdown("---")

        st.markdown("### Main")
        st.page_link("pages/10_CoreKnow_Student.py", label="Home", use_container_width=True)
        st.page_link("pages/11_JAMB.py", label="JAMB", use_container_width=True)
        st.page_link("pages/12_WAEC.py", label="WAEC", use_container_width=True)
        st.page_link("pages/13_GCE.py", label="GCE", use_container_width=True)
        st.page_link("pages/14_NECO.py", label="NECO", use_container_width=True)
        st.page_link("pages/15_JSS_SS.py", label="JSS1-SS3", use_container_width=True)

        st.markdown("---")
        st.markdown("### Study Tools")
        st.page_link("pages/17_Practice.py", label="Basic Practice", use_container_width=True)
        st.page_link("pages/18_AI_Practice.py", label="AI Practice (50 Qs)", use_container_width=True)
        st.page_link("pages/19_CoreKnow_Chat.py", label="Ask CoreKnow", use_container_width=True)
        st.page_link("pages/20_Exam_Mode.py", label="Exam Mode", use_container_width=True)

        st.markdown("---")
        st.markdown("### Other Tools")
        st.page_link("app.py", label="Back to CoreKnow", use_container_width=True)
        st.page_link("pages/3_Deep_Search.py", label="Deep Search", use_container_width=True)
        st.page_link("pages/4_Browse_Knowledge.py", label="Browse Knowledge", use_container_width=True)
