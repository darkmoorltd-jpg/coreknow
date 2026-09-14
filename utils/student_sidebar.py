
import streamlit as st


def render_student_sidebar():
    """Optional branding block — main nav comes from st.navigation() in app.py."""

    with st.sidebar:
        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;padding:1rem 0;'>"
            "<div style='font-family:Orbitron,sans-serif;font-size:1.2rem;"
            "font-weight:900;background:linear-gradient(135deg,#00e5ff,#7c4dff);"
            "-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>"
            "COR EKNOW STUDENT</div>"
            "<div style='color:#8892b0;font-size:0.75rem;letter-spacing:2px;'>"
            "POWERED BY DARKMOOR</div>"
            "</div>",
            unsafe_allow_html=True
        )
