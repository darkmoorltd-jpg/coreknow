import streamlit as st
import sys
import os
import uuid
from datetime import datetime

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from utils.ai_generator import chat_with_coreknow, extract_text_from_image

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="CoreKnow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CHATGPT-STYLE THEME
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* App background */
    .stApp { background: #0f0f0f; color: #ececec; }
    header, footer { visibility: hidden; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #171717;
        border-right: 1px solid #2a2a2a;
    }
    [data-testid="stSidebar"] * { color: #ececec; }

    /* Remove default streamlit padding */
    .block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 900px !important; }

    /* WELCOME / HERO */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
        text-align: center;
        padding: 2rem;
    }
    .brain-logo {
        font-size: 5rem;
        animation: brainPulse 3s ease-in-out infinite;
        filter: drop-shadow(0 0 30px rgba(0, 229, 255, 0.6));
    }
    @keyframes brainPulse {
        0%, 100% { transform: scale(1); filter: drop-shadow(0 0 30px rgba(0, 229, 255, 0.6)); }
        50% { transform: scale(1.08); filter: drop-shadow(0 0 50px rgba(0, 229, 255, 0.9)); }
    }
    .welcome-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 1.5rem;
        background: linear-gradient(135deg, #00e5ff, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .welcome-sub {
        color: #8e8ea0;
        margin-top: 0.5rem;
        font-size: 1rem;
    }

    /* SUGGESTION CARDS */
    .suggestion-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        max-width: 700px;
        margin: 2rem auto 0 auto;
    }
    .suggestion-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    .suggestion-card:hover {
        background: #212121;
        border-color: #00e5ff;
        transform: translateY(-1px);
    }
    .suggestion-title {
        color: #ececec;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .suggestion-sub {
        color: #8e8ea0;
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }

    /* CHAT MESSAGES */
    .chat-row-user {
        display: flex;
        justify-content: flex-end;
        padding: 1rem 0;
        gap: 1rem;
    }
    .chat-row-ai {
        display: flex;
        justify-content: flex-start;
        padding: 1rem 0;
        gap: 1rem;
    }
    .chat-avatar-user {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7c4dff, #00e5ff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        color: #0f0f0f;
        flex-shrink: 0;
    }
    .chat-avatar-ai {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00e5ff, #00c853);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .bubble-user {
        background: #2f2f2f;
        border-radius: 16px;
        padding: 0.85rem 1.1rem;
        max-width: 75%;
        color: #ececec;
        font-size: 0.95rem;
        line-height: 1.6;
        word-wrap: break-word;
    }
    .bubble-ai {
        background: transparent;
        padding: 0.85rem 0;
        max-width: 85%;
        color: #ececec;
        font-size: 0.95rem;
        line-height: 1.7;
        word-wrap: break-word;
    }
    .bubble-ai p { margin: 0.5rem 0; }
    .bubble-ai code {
        background: #1a1a1a;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #00e5ff;
    }
    .bubble-ai pre {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid #2a2a2a;
    }
    .bubble-ai pre code {
        background: transparent;
        padding: 0;
        color: #00e5ff;
    }

    /* TIMESTAMP */
    .timestamp {
        font-size: 0.7rem;
        color: #6b6b80;
        margin-top: 0.3rem;
    }

    /* INPUT BOX */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, #0f0f0f 60%, transparent);
        padding: 1.5rem 1rem 2rem 1rem;
        z-index: 999;
    }

    /* Make the text area look like ChatGPT */
    .stTextArea textarea {
        background: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 14px !important;
        color: #ececec !important;
        font-size: 0.95rem !important;
        padding: 1rem 1.2rem !important;
        resize: none !important;
        min-height: 56px !important;
        transition: border-color 0.2s;
    }
    .stTextArea textarea:focus {
        border-color: #00e5ff !important;
        box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.15) !important;
    }

    /* Send button */
    .stButton > button {
        background: #00e5ff !important;
        color: #0f0f0f !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #00c8dd !important;
        transform: translateY(-1px);
    }

    /* Sidebar "New chat" button */
    .new-chat-btn > button {
        background: transparent !important;
        border: 1px solid #2a2a2a !important;
        color: #ececec !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 10px !important;
    }
    .new-chat-btn > button:hover {
        background: #212121 !important;
        border-color: #00e5ff !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f0f0f; }
    ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }

    /* Hide streamlit default file uploader look */
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
    # Brain logo + branding
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size: 2.5rem;">🧠</div>
        <div style="font-family: 'Inter'; font-weight: 800; font-size: 1.3rem;
                    background: linear-gradient(135deg, #00e5ff, #7c4dff);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            CoreKnow
        </div>
        <div style="color: #6b6b80; font-size: 0.7rem; letter-spacing: 2px; margin-top: 0.2rem;">
            AI KNOWLEDGE ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New chat
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕  New chat", use_container_width=True, key="new_chat"):
        if st.session_state.messages:
            # Save current conversation
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
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Recent conversations
    if st.session_state.conversations:
        st.markdown(
            '<div style="color:#6b6b80;font-size:0.75rem;letter-spacing:1.5px;'
            'text-transform:uppercase;margin-bottom:0.5rem;">Recent</div>',
            unsafe_allow_html=True
        )
        for conv in st.session_state.conversations[:10]:
            if st.button("💬 " + conv["title"], key="conv_" + conv["id"], use_container_width=True):
                # Save current first
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

    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;'
        'color:#6b6b80;font-size:0.7rem;">Powered by Darkmoor Ltd</div>',
        unsafe_allow_html=True
    )


# ============================================
# MAIN — WELCOME OR CHAT
# ============================================
if not st.session_state.messages:
    # WELCOME SCREEN
    st.markdown("""
    <div class="welcome-container">
        <div class="brain-logo">🧠</div>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-sub">Ask anything. Upload a photo. Get answers.</div>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion cards
    suggestions = [
        ("📐 Solve a math problem", "Explain step by step"),
        ("🧪 Chemistry equation", "Balance and explain"),
        ("📝 JAMB question", "Get a full solution"),
        ("📚 Learn a topic", "Any subject, any level"),
    ]

    cols = st.columns(2)
    for i, (title, sub) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(title + "\n\n" + sub, key="sug_" + str(i), use_container_width=True):
                st.session_state.pending_prompt = title.split(" ", 1)[1]

else:
    # CHAT MESSAGES
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                '<div class="chat-row-user">'
                '<div class="bubble-user">' + msg["content"].replace("<", "&lt;").replace(">", "&gt;") + '</div>'
                '<div class="chat-avatar-user">You</div>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="chat-row-ai">'
                '<div class="chat-avatar-ai">🧠</div>'
                '<div class="bubble-ai">' + msg["content"] + '</div>'
                '</div>',
                unsafe_allow_html=True
            )

    st.markdown('<div style="height:120px;"></div>', unsafe_allow_html=True)


# ============================================
# INPUT AREA (fixed at bottom)
# ============================================
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Upload + Text input row
col_upload, col_input, col_send = st.columns([0.5, 7, 1.5])

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
                st.warning("Could not read text. Please type your question.")

with col_input:
    user_input = st.text_area(
        "Message",
        value=st.session_state.pending_prompt,
        placeholder="Ask anything...",
        label_visibility="collapsed",
        height=56,
        key="chat_input"
    )

with col_send:
    send = st.button("Send ➤", use_container_width=True, key="send_btn")

st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# HANDLE SEND
# ============================================
def do_send(question, image_text=""):
    # Add user message
    display_q = question or "[Uploaded question]"
    st.session_state.messages.append({"role": "user", "content": display_q})

    # Placeholder for AI response
    placeholder = st.empty()
    placeholder.markdown(
        '<div class="chat-row-ai">'
        '<div class="chat-avatar-ai">🧠</div>'
        '<div class="bubble-ai">🧠 Thinking...</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # Build history
    history = []
    for i in range(0, len(st.session_state.messages) - 1, 2):
        if i + 1 < len(st.session_state.messages):
            history.append({
                "q": st.session_state.messages[i]["content"],
                "a": st.session_state.messages[i + 1]["content"]
            })

    # Get AI response
    answer, err = chat_with_coreknow(question, image_text=image_text, history=history)

    if err:
        answer = "⚠️ Error: " + err

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.pending_image_text = ""
    st.session_state.pending_prompt = ""
    st.rerun()


if send and (user_input.strip() or st.session_state.pending_image_text):
    do_send(
        user_input.strip(),
        image_text=st.session_state.pending_image_text
    )
elif st.session_state.pending_prompt and not send:
    # Auto-send when suggestion clicked
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = ""
    do_send(prompt)
