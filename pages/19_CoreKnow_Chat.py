import streamlit as st
import sys
import os

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from utils.ai_generator import chat_with_coreknow, extract_text_from_image

st.set_page_config(page_title="Ask CoreKnow", page_icon="💬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 0%, #0d1b2a 0%, #050810 100%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background: #0a0e17; border-right: 1px solid #1f2a44; }
    .ck-title { font-family: 'Orbitron', sans-serif; font-size: 2.4rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .ck-sub { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }
    .msg-user { background: #1f2a44; border-radius: 12px; padding: 1rem; margin: 0.5rem 0 0.5rem 10%; color: #e0e0e0; }
    .msg-ai { background: #0d1117; border-left: 4px solid #00e5ff; border-radius: 12px; padding: 1rem; margin: 0.5rem 10% 0.5rem 0; color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ck-title">Ask CoreKnow</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">TYPE OR UPLOAD ANY QUESTION · GET SOLUTIONS</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="JAMB", use_container_width=True)
    st.page_link("pages/17_Practice.py", label="Basic Practice", use_container_width=True)
    st.page_link("pages/18_AI_Practice.py", label="AI Practice", use_container_width=True)
    st.page_link("pages/19_CoreKnow_Chat.py", label="Ask CoreKnow", use_container_width=True)
    st.page_link("pages/20_Exam_Mode.py", label="Exam Mode", use_container_width=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_image_text" not in st.session_state:
    st.session_state.pending_image_text = ""

for msg in st.session_state.chat_history:
    st.markdown('<div class="msg-user"><strong>You:</strong><br>' + msg["q"].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="msg-ai"><strong>CoreKnow:</strong><br>' + msg["a"].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)

st.markdown("---")

with st.expander("Upload a question (image)", expanded=False):
    uploaded = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        st.info("Uploaded: " + uploaded.name)
        if st.button("Read this image"):
            with st.spinner("Reading..."):
                text = extract_text_from_image(uploaded.getvalue())
            if text:
                st.session_state.pending_image_text = text
                st.success("Extracted: " + text[:200])
            else:
                st.warning("Could not read text. Please type your question below.")

user_q = st.text_area("Type your question", placeholder="e.g., Explain ionic vs covalent bonding with examples.", height=100, label_visibility="collapsed")

c1, c2 = st.columns([3, 1])
with c2:
    if st.button("Send", type="primary", use_container_width=True) and (user_q.strip() or st.session_state.pending_image_text):
        with st.spinner("CoreKnow is thinking..."):
            answer, err = chat_with_coreknow(
                user_q or "Solve this question",
                image_text=st.session_state.pending_image_text,
                history=st.session_state.chat_history
            )
        if err:
            st.error(err)
        else:
            st.session_state.chat_history.append({
                "q": user_q or "[Uploaded image]",
                "a": answer
            })
            st.session_state.pending_image_text = ""
            st.rerun()

if st.session_state.chat_history:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
