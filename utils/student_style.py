"""CoreKnow Student — shared theme."""

def apply_theme():
    """Apply dark HUD theme to the current Streamlit page."""
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

        .stApp {
            background: radial-gradient(ellipse at 50% 50%, #0d1b2a 0%, #050810 100%);
            color: #e0e0e0;
            font-family: 'Rajdhani', sans-serif;
        }
        header, footer { visibility: hidden; }

        .ck-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 50%, #ff1744 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .ck-sub {
            text-align: center;
            color: #8892b0;
            margin-bottom: 2rem;
            letter-spacing: 2px;
        }
        .card {
            background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
            border: 2px solid #1f2a44;
            border-radius: 16px;
            padding: 2rem 1rem;
            text-align: center;
            transition: all 0.3s;
        }
        .card:hover {
            border-color: #00e5ff;
            box-shadow: 0 0 25px rgba(0,229,255,0.3);
            transform: translateY(-5px);
        }
        .card-icon { font-size: 3rem; }
        .card-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.3rem;
            color: #ffd700;
            margin-top: 0.5rem;
            font-weight: 700;
        }
        .card-sub { color: #8892b0; font-size: 0.85rem; margin-top: 0.3rem; }

        .topic-card {
            background: #0d1117;
            border-left: 4px solid #00e5ff;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 0.6rem 0;
        }
        .topic-title { font-size: 1.1rem; font-weight: 600; color: #e0e0e0; }
        .topic-meta { color: #8892b0; font-size: 0.85rem; margin-top: 0.3rem; }

        .stat-box {
            background: #0d1117;
            border: 1px solid #1f2a44;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }
        .stat-num {
            font-family: 'Orbitron', monospace;
            font-size: 1.8rem;
            color: #00e5ff;
        }
        .stat-lbl {
            color: #8892b0;
            font-size: 0.75rem;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] {
            background: #0d1117;
            border-right: 1px solid #1f2a44;
        }
    </style>
    """, unsafe_allow_html=True)
