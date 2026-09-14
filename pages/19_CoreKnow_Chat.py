
import streamlit as st
import sys
import os
import uuid
from datetime import datetime

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from utils.ai_generator import chat_with_coreknow, extract_text_from_image

st.set_page_config(
    page_title="CoreKnow Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CoreKnow Chat Theme
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ==== CoreKnow blue palette ==== */
    :root {
        --ds-bg: #1a1a1f;
        --ds-sidebar: #141420;
        --ds-bubble-user: #2b2b3a;
        --ds-bubble-ai: transparent;
        --ds-accent: #4d6bfe;
        --ds-accent-hover: #3a56e0;
        --ds-border: #2a2a3a;
        --ds-text: #e8e8ed;
        --ds-text-dim: #8b8b9e;
        --ds-code-bg: #0f0f18;
    }

    /* ==== App background ==== */
    .stApp { background: #1a1a1f; color: #e8e8ed; }
    header, footer { visibility: hidden; }

    /* ==== Main content width ==== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 180px !important;
        max-width: 820px !important;
        margin: 0 auto !important;
    }

    /* ==== Sidebar ==== */
    [data-testid="stSidebar"] {
        background: #141420 !important;
        border-right: 1px solid #2a2a3a !important;
        min-width: 260px !important;
    }
    [data-testid="stSidebar"] * { color: #e8e8ed; }

    /* ==== Sidebar buttons ==== */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid #2a2a3a !important;
        color: #e8e8ed !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.15s;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #1e1e2e !important;
        border-color: #4d6bfe !important;
    }

    /* ============================================
       WELCOME SCREEN
       ============================================ */
    .ds-welcome {
        text-align: center;
        padding: 5rem 1rem 3rem 1rem;
    }
    .ds-logo-big {
        font-size: 4rem;
        animation: dsFloat 3s ease-in-out infinite;
        display: inline-block;
    }
    @keyframes dsFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    .ds-title {
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #4d6bfe 0%, #7c8fff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0 0 0;
    }
    .ds-subtitle {
        color: #8b8b9e;
        font-size: 1.05rem;
        margin-top: 0.6rem;
        font-weight: 400;
    }

    /* ==== Suggestion cards ==== */
    .ds-suggestions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        max-width: 720px;
        margin: 3rem auto 0 auto;
    }
    .ds-card {
        background: #21212d;
        border: 1px solid #2a2a3a;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        text-align: left;
        transition: all 0.15s;
        cursor: pointer;
    }
    .ds-card:hover {
        background: #2a2a3a;
        border-color: #4d6bfe;
    }
    .ds-card-icon { font-size: 1.1rem; margin-bottom: 0.3rem; }
    .ds-card-title {
        color: #e8e8ed;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .ds-card-sub {
        color: #8b8b9e;
        font-size: 0.78rem;
        margin-top: 0.15rem;
    }

    /* ============================================
       CHAT MESSAGES
       ============================================ */
    .ds-user-row {
        display: flex;
        justify-content: flex-end;
        margin: 1.2rem 0;
    }
    .ds-user-bubble {
        background: #2b2b3a;
        color: #e8e8ed;
        padding: 0.75rem 1.1rem;
        border-radius: 14px;
        max-width: 78%;
        font-size: 0.95rem;
        line-height: 1.6;
        word-wrap: break-word;
    }

    .ds-ai-row {
        display: flex;
        justify-content: flex-start;
        margin: 1.2rem 0;
        gap: 0.9rem;
    }
    .ds-ai-avatar {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: linear-gradient(135deg, #4d6bfe, #7c8fff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
        color: white;
        font-weight: 700;
    }
    .ds-ai-bubble {
        color: #e8e8ed;
        font-size: 0.95rem;
        line-height: 1.75;
        max-width: 85%;
        word-wrap: break-word;
    }
    .ds-ai-bubble p { margin: 0.6rem 0; }
    .ds-ai-bubble strong { color: #e8e8ed; font-weight: 600; }
    .ds-ai-bubble ul, .ds-ai-bubble ol { margin: 0.5rem 0; padding-left: 1.4rem; }
    .ds-ai-bubble li { margin: 0.25rem 0; }
    .ds-ai-bubble code {
        background: #0f0f18;
        padding: 2px 7px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #7c8fff;
        border: 1px solid #2a2a3a;
    }
    .ds-ai-bubble pre {
        background: #0f0f18;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        overflow-x: auto;
        border: 1px solid #2a2a3a;
        margin: 0.8rem 0;
    }
    .ds-ai-bubble pre code {
        background: transparent;
        padding: 0;
        color: #7c8fff;
        border: none;
        font-size: 0.85rem;
    }
    .ds-ai-bubble h1, .ds-ai-bubble h2, .ds-ai-bubble h3 {
        color: #e8e8ed;
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
    }
    .ds-ai-bubble h1 { font-size: 1.3rem; }
    .ds-ai-bubble h2 { font-size: 1.15rem; }
    .ds-ai-bubble h3 { font-size: 1rem; }
    .ds-ai-bubble table {
        border-collapse: collapse;
        margin: 0.8rem 0;
        font-size: 0.9rem;
    }
    .ds-ai-bubble table th {
        background: #21212d;
        padding: 6px 12px;
        border: 1px solid #2a2a3a;
        font-weight: 600;
    }
    .ds-ai-bubble table td {
        padding: 6px 12px;
        border: 1px solid #2a2a3a;
    }

    /* ==== Thinking indicator ==== */
    .ds-thinking {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #8b8b9e;
        font-size: 0.9rem;
        padding: 0.5rem 0;
    }
    .ds-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #4d6bfe;
        animation: dsBounce 1.4s infinite ease-in-out both;
    }
    .ds-dot:nth-child(2) { animation-delay: -0.32s; }
    .ds-dot:nth-child(3) { animation-delay: -0.16s; }
    @keyframes dsBounce {
        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ============================================
       INPUT BOX (fixed bottom)
       ============================================ */
    .ds-input-wrap {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, #1a1a1f 65%, transparent);
        padding: 2rem 1rem 1.5rem 1rem;
        z-index: 998;
        pointer-events: none;
    }
    .ds-input-inner {
        max-width: 820px;
        margin: 0 auto;
        pointer-events: auto;
    }

    /* ==== Text area ==== */
    .stTextArea textarea {
        background: #21212d !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 12px !important;
        color: #e8e8ed !important;
        font-size: 0.95rem !important;
        padding: 0.9rem 1.1rem !important;
        resize: none !important;
        min-height: 52px !important;
        max-height: 200px !important;
        transition: all 0.15s !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea:focus {
        border-color: #4d6bfe !important;
        box-shadow: 0 0 0 3px rgba(77, 107, 254, 0.15) !important;
        background: #252532 !important;
    }
    .stTextArea textarea::placeholder {
        color: #6b6b80 !important;
    }

    /* ==== Send button ==== */
    .stButton > button {
        background: #4d6bfe !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        padding: 0.65rem 1.4rem !important;
        transition: all 0.15s;
        font-size: 0.9rem !important;
    }
    .stButton > button:hover {
        background: #3a56e0 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(77, 107, 254, 0.3);
    }

    /* ==== Upload popover button ==== */
    .stPopover > button {
        background: transparent !important;
        border: 1px solid #2a2a3a !important;
        color: #8b8b9e !important;
        padding: 0.65rem 1rem !important;
        border-radius: 10px !important;
    }
    .stPopover > button:hover {
        background: #21212d !important;
        border-color: #4d6bfe !important;
        color: #e8e8ed !important;
    }

    /* ==== Scrollbar ==== */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #1a1a1f; }
    ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a3a4a; }

    /* ==== File uploader cleanup ==== */
    [data-testid="stFileUploader"] label { display: none; }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent;
        border: none;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None
if "pending_image_text" not in st.session_state:
    st.session_state.pending_image_text = ""
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 0 1rem 0; text-align: center;">
        <div style="font-size: 1.8rem;">🧠</div>
        <div style="font-weight: 700; font-size: 1.15rem; color: #e8e8ed; margin-top: 0.3rem;">
            CoreKnow
        </div>
        <div style="color: #6b6b80; font-size: 0.7rem; letter-spacing: 1.5px; margin-top: 0.15rem;">
            AI KNOWLEDGE ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✏️  New chat", use_container_width=True, key="new_chat"):
        if st.session_state.messages:
            if st.session_state.current_conv_id is None:
                st.session_state.current_conv_id = str(uuid.uuid4())[:8]
            st.session_state.conversations.insert(0, {
                "id": st.session_state.current_conv_id,
                "title": st.session_state.messages[0]["content"][:40] + "...",
                "messages": st.session_state.messages.copy(),
                "time": datetime.now().strftime("%H:%M"),
            })
        st.session_state.messages = []
        st.session_state.current_conv_id = None
        st.rerun()

    st.markdown("---")

    if st.session_state.conversations:
        st.markdown(
            '<div style="color:#6b6b80;font-size:0.72rem;letter-spacing:1.5px;'
            'text-transform:uppercase;margin: 0.5rem 0 0.5rem 0;">Recent</div>',
            unsafe_allow_html=True
        )
        for conv in st.session_state.conversations[:10]:
            if st.button("💬  " + conv["title"], key="conv_" + conv["id"], use_container_width=True):
                if st.session_state.messages and st.session_state.current_conv_id is None:
                    st.session_state.conversations.insert(0, {
                        "id": str(uuid.uuid4())[:8],
                        "title": st.session_state.messages[0]["content"][:40] + "...",
                        "messages": st.session_state.messages.copy(),
                        "time": datetime.now().strftime("%H:%M"),
                    })
                st.session_state.messages = conv["messages"].copy()
                st.session_state.current_conv_id = conv["id"]
                st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="color:#6b6b80;font-size:0.7rem;text-align:center;">'
        'Powered by Darkmoor Ltd</div>',
        unsafe_allow_html=True
    )


# ============================================
# MAIN AREA
# ============================================
if not st.session_state.messages:
    # ============ WELCOME SCREEN ============
    st.markdown("""
    <div class="ds-welcome">
        <div class="ds-logo-big">🧠</div>
        <div class="ds-title">CoreKnow</div>
        <div class="ds-subtitle">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion cards
    suggestions = [
        ("📐", "Solve a math problem", "Step-by-step explanations"),
        ("🧪", "Balance a chemistry equation", "With full reasoning"),
        ("📝", "Answer a JAMB question", "Get the complete solution"),
        ("📚", "Explain a concept", "Any subject, any level"),
    ]

    cols = st.columns(2)
    for i, (icon, title, sub) in enumerate(suggestions):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="ds-card">
                <div class="ds-card-icon">{icon}</div>
                <div class="ds-card-title">{title}</div>
                <div class="ds-card-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Choose", key="sug_" + str(i), use_container_width=True):
                st.session_state.pending_prompt = title
                st.rerun()

else:
    # ============ CHAT MESSAGES ============
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            safe_text = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                '<div class="ds-user-row">'
                '<div class="ds-user-bubble">' + safe_text + '</div>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="ds-ai-row">'
                '<div class="ds-ai-avatar">🧠</div>'
                '<div class="ds-ai-bubble">' + msg["content"] + '</div>'
                '</div>',
                unsafe_allow_html=True
            )


# ============================================
# INPUT AREA (fixed bottom)
# ============================================
st.markdown('<div class="ds-input-wrap"><div class="ds-input-inner">', unsafe_allow_html=True)

col_upload, col_input, col_send = st.columns([0.6, 8, 1.4])

with col_upload:
    with st.popover("📎", use_container_width=True):
        st.markdown("**Upload a question**")
        uploaded = st.file_uploader(
            "Image or PDF",
            type=["jpg", "jpeg", "png", "pdf"],
            label_visibility="collapsed",
            key="chat_upload"
        )
        if uploaded is not None:
            with st.spinner("Reading..."):
                text = extract_text_from_image(uploaded.getvalue())
            if text:
                st.session_state.pending_image_text = text
                st.success("Read: " + text[:100])
            else:
                st.warning("Could not read. Please type your question.")

with col_input:
    user_input = st.text_area(
        "Message",
        value=st.session_state.pending_prompt,
        placeholder="Message CoreKnow...",
        label_visibility="collapsed",
        height=54,
        key="chat_input"
    )

with col_send:
    send = st.button("Send", use_container_width=True, key="send_btn")

st.markdown('</div></div>', unsafe_allow_html=True)


# ============================================
# SEND HANDLER
# ============================================
def do_send(question, image_text=""):
    display_q = question or "[Uploaded question]"
    st.session_state.messages.append({"role": "user", "content": display_q})

    # Add thinking placeholder
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            '<div class="ds-thinking">'
            '<span class="ds-dot"></span>'
            '<span class="ds-dot"></span>'
            '<span class="ds-dot"></span>'
            '<span style="margin-left: 0.5rem;">CoreKnow is thinking...</span>'
            '</div>'
        )
    })
    st.rerun()

def process_response(question, image_text=""):
    """Called after rerun to actually fetch the response."""
    history = []
    # Collect prior exchanges (skip placeholder)
    msgs = st.session_state.messages[:-1]  # skip placeholder
    for i in range(0, len(msgs) - 1, 2):
        if i + 1 < len(msgs):
            history.append({
                "q": msgs[i]["content"],
                "a": msgs[i + 1]["content"]
            })

    answer, err = chat_with_coreknow(question, image_text=image_text, history=history)
    if err:
        answer = "⚠️ Error: " + err

    # Replace placeholder with real answer
    st.session_state.messages[-1] = {"role": "assistant", "content": answer}
    st.session_state.pending_image_text = ""
    st.session_state.pending_prompt = ""


# Detect and send
if send and (user_input.strip() or st.session_state.pending_image_text):
    do_send(user_input.strip(), image_text=st.session_state.pending_image_text)
elif st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = ""
    do_send(prompt)

# Process placeholder if last message is thinking
if st.session_state.messages and st.session_state.messages[-1].get("content", "").startswith('<div class="ds-thinking">'):
    # Get the user's actual question
    user_q = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else ""
    process_response(user_q, image_text=st.session_state.pending_image_text)
    st.rerun()
