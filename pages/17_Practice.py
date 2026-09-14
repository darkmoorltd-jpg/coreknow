
import streamlit as st
import sys
import os
import random

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from supabase import create_client

st.set_page_config(page_title="Practice", page_icon="✏️", layout="wide")

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
    .q-card { background: #0d1117; border: 2px solid #1f2a44; border-left: 5px solid #00e5ff;
        border-radius: 14px; padding: 2rem; margin: 1rem 0; }
    .q-number { font-family: 'Orbitron', monospace; color: #ffd700; font-size: 1.1rem; font-weight: 700; }
    .q-text { font-size: 1.15rem; color: #e0e0e0; line-height: 1.7; margin: 0.8rem 0 1.5rem 0; }
    .res-correct { background: rgba(0,200,83,0.1); border: 2px solid #00c853; border-radius: 10px; padding: 1rem; margin: 0.8rem 0; }
    .res-wrong { background: rgba(255,23,68,0.1); border: 2px solid #ff1744; border-radius: 10px; padding: 1rem; margin: 0.8rem 0; }
    .stat-box { background: #0d1117; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-num { font-family: 'Orbitron', monospace; font-size: 1.8rem; color: #00e5ff; }
    .stat-lbl { color: #8892b0; font-size: 0.75rem; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_key"])
except Exception as e:
    st.error("Supabase failed: " + str(e))
    st.stop()

st.markdown('<div class="ck-title">✏️ PRACTICE MODE</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">TEST YOURSELF · INSTANT FEEDBACK</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="JAMB", use_container_width=True)
    st.page_link("pages/17_Practice.py", label="Basic Practice", use_container_width=True)
    st.page_link("pages/18_AI_Practice.py", label="AI Practice", use_container_width=True)
    st.page_link("pages/19_CoreKnow_Chat.py", label="Ask CoreKnow", use_container_width=True)
    st.page_link("pages/20_Exam_Mode.py", label="Exam Mode", use_container_width=True)

if "prac_qs" not in st.session_state: st.session_state.prac_qs = []
if "prac_idx" not in st.session_state: st.session_state.prac_idx = 0
if "prac_score" not in st.session_state: st.session_state.prac_score = 0
if "prac_answered" not in st.session_state: st.session_state.prac_answered = False
if "prac_selected" not in st.session_state: st.session_state.prac_selected = None
if "prac_history" not in st.session_state: st.session_state.prac_history = []
if "prac_finished" not in st.session_state: st.session_state.prac_finished = False

# SETUP
if not st.session_state.prac_qs:
    c1, c2, c3 = st.columns(3)
    with c1:
        exam = st.selectbox("Exam", ["JAMB", "WAEC", "GCE", "NECO"], index=0)
    try:
        s_res = supabase.table("education_syllabi").select("subject").eq("exam", exam).execute()
        subjects = sorted(set(s["subject"] for s in s_res.data)) if s_res.data else ["Chemistry"]
    except Exception:
        subjects = ["Chemistry"]
    with c2:
        subject = st.selectbox("Subject", subjects, index=0)
    try:
        t_res = supabase.table("education_syllabi").select("topic_title").eq("exam", exam).eq("subject", subject).execute()
        topics = ["All Topics"] + sorted(set(t["topic_title"] for t in t_res.data)) if t_res.data else ["All Topics"]
    except Exception:
        topics = ["All Topics"]
    with c3:
        topic_choice = st.selectbox("Topic", topics, index=0)

    num = st.slider("Number of Questions", 5, 50, 10, step=5)

    if st.button("Start Practice", type="primary", use_container_width=True):
        try:
            query = supabase.table("education_questions").select("*").eq("exam", exam).eq("subject", subject)
            if topic_choice != "All Topics":
                query = query.eq("topic", topic_choice)
            result = query.execute()
            all_q = result.data if result.data else []
            if not all_q:
                st.warning("No questions available for this filter. Try 'All Topics'.")
            else:
                random.shuffle(all_q)
                st.session_state.prac_qs = all_q[:num]
                st.session_state.prac_idx = 0
                st.session_state.prac_score = 0
                st.session_state.prac_answered = False
                st.session_state.prac_selected = None
                st.session_state.prac_history = []
                st.session_state.prac_finished = False
                st.rerun()
        except Exception as e:
            st.error("Query failed: " + str(e))

# QUIZ
elif not st.session_state.prac_finished:
    qs = st.session_state.prac_qs
    idx = st.session_state.prac_idx
    q = qs[idx]
    st.progress(idx / len(qs))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="stat-box"><div class="stat-num">' + str(idx+1) + "/" + str(len(qs)) + '</div><div class="stat-lbl">Question</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-box"><div class="stat-num">' + str(st.session_state.prac_score) + '</div><div class="stat-lbl">Correct</div></div>', unsafe_allow_html=True)
    with c3:
        pct = int((st.session_state.prac_score / (idx + 1)) * 100) if idx > 0 or st.session_state.prac_answered else 0
        st.markdown('<div class="stat-box"><div class="stat-num">' + str(pct) + '%</div><div class="stat-lbl">Accuracy</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="q-card"><div class="q-number">QUESTION ' + str(idx+1) + '</div><div class="q-text">' + str(q.get("question_text", "")) + '</div></div>', unsafe_allow_html=True)

    options = q.get("options") or []
    if isinstance(options, str):
        import json
        try:
            options = json.loads(options)
        except Exception:
            options = []

    labels = ["A", "B", "C", "D"]

    if not st.session_state.prac_answered:
        for i, opt in enumerate(options[:4]):
            if st.button(labels[i] + ". " + str(opt), key="pr_" + str(idx) + "_" + str(i), use_container_width=True):
                st.session_state.prac_selected = labels[i]
                st.session_state.prac_answered = True
                correct = str(q.get("correct_answer", "A")).upper()
                is_correct = (labels[i] == correct)
                if is_correct:
                    st.session_state.prac_score += 1
                st.session_state.prac_history.append({
                    "question": q.get("question_text", ""),
                    "selected": labels[i],
                    "correct": correct,
                    "is_correct": is_correct
                })
                st.rerun()
    else:
        correct = str(q.get("correct_answer", "A")).upper()
        is_correct = (st.session_state.prac_selected == correct)
        if is_correct:
            st.markdown('<div class="res-correct"><strong>Correct!</strong> You selected ' + str(st.session_state.prac_selected) + '</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="res-wrong"><strong>Incorrect</strong><br>You selected: ' + str(st.session_state.prac_selected) + '<br>Correct: ' + correct + '</div>', unsafe_allow_html=True)

        st.markdown("#### Options:")
        for i, opt in enumerate(options[:4]):
            mark = " [CORRECT]" if labels[i] == correct else (" [YOUR PICK]" if labels[i] == st.session_state.prac_selected else "")
            st.markdown("**" + labels[i] + ".** " + str(opt) + mark)

        if idx + 1 < len(qs):
            if st.button("Next Question", type="primary", use_container_width=True):
                st.session_state.prac_idx += 1
                st.session_state.prac_answered = False
                st.session_state.prac_selected = None
                st.rerun()
        else:
            if st.button("Finish Practice", type="primary", use_container_width=True):
                st.session_state.prac_finished = True
                st.rerun()

# RESULTS
else:
    score = st.session_state.prac_score
    total = len(st.session_state.prac_qs)
    pct = int((score / total) * 100) if total else 0
    color = "#00c853" if pct >= 70 else "#ff9800" if pct >= 50 else "#ff1744"
    st.markdown('<div class="q-card" style="text-align:center;border-left-color:' + color + ';">'
        '<div style="font-family:Orbitron,monospace;font-size:4rem;font-weight:900;color:' + color + ';">' + str(pct) + '%</div>'
        '<div style="font-size:1.3rem;">Score: ' + str(score) + ' / ' + str(total) + '</div></div>', unsafe_allow_html=True)

    st.markdown("### Question-by-Question Review")
    for i, h in enumerate(st.session_state.prac_history, 1):
        icon = "OK" if h["is_correct"] else "X"
        with st.expander("[" + icon + "] Q" + str(i) + ": " + str(h["question"])[:70]):
            st.markdown("**Your answer:** " + str(h["selected"]))
            st.markdown("**Correct answer:** " + str(h["correct"]))
            st.markdown("**Result:** " + ("Correct" if h["is_correct"] else "Incorrect"))

    c1, c2 = st.columns(2)
    with c1:
        if st.button("New Practice", use_container_width=True):
            st.session_state.prac_qs = []
            st.session_state.prac_idx = 0
            st.session_state.prac_score = 0
            st.session_state.prac_answered = False
            st.session_state.prac_selected = None
            st.session_state.prac_history = []
            st.session_state.prac_finished = False
            st.rerun()
    with c2:
        if st.button("Back to JAMB", use_container_width=True):
            st.switch_page("pages/11_JAMB.py")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
