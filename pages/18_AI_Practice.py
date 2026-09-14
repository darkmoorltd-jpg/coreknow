import streamlit as st
import sys
import os
import random

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from supabase import create_client
from utils.ai_generator import generate_hard_mcqs

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 0%, #0d1b2a 0%, #050810 100%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background: #0a0e17; border-right: 1px solid #1f2a44; }
    .ck-title { font-family: 'Orbitron', sans-serif; font-size: 2.4rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .ck-sub { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }
    .q-card { background: #0d1117; border: 2px solid #1f2a44; border-left: 5px solid #ffd700;
        border-radius: 14px; padding: 2rem; margin: 1rem 0; }
    .q-number { font-family: 'Orbitron', monospace; color: #ffd700; font-size: 1.1rem; font-weight: 700; }
    .q-text { font-size: 1.15rem; color: #e0e0e0; line-height: 1.7; margin: 0.8rem 0 1.5rem 0; }
    .sol-correct { background: rgba(0,200,83,0.1); border: 2px solid #00c853; border-radius: 10px; padding: 1rem; margin: 0.8rem 0; }
    .sol-wrong { background: rgba(255,23,68,0.1); border: 2px solid #ff1744; border-radius: 10px; padding: 1rem; margin: 0.8rem 0; }
    .stat-box { background: #0d1117; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-num { font-family: 'Orbitron', monospace; font-size: 1.8rem; color: #ffd700; }
    .stat-lbl { color: #8892b0; font-size: 0.75rem; text-transform: uppercase; }
    .sol-box { background: #0a1428; border-left: 4px solid #00e5ff; border-radius: 8px; padding: 1rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_key"])
except Exception as e:
    st.error("Supabase failed: " + str(e))
    st.stop()

st.markdown('<div class="ck-title">🧠 AI PRACTICE</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">50 HARD QUESTIONS · FRESH EACH SESSION · FULL SOLUTIONS</div>', unsafe_allow_html=True)

if "ai_qs" not in st.session_state: st.session_state.ai_qs = []
if "ai_idx" not in st.session_state: st.session_state.ai_idx = 0
if "ai_score" not in st.session_state: st.session_state.ai_score = 0
if "ai_answered" not in st.session_state: st.session_state.ai_answered = False
if "ai_selected" not in st.session_state: st.session_state.ai_selected = None
if "ai_history" not in st.session_state: st.session_state.ai_history = []
if "ai_finished" not in st.session_state: st.session_state.ai_finished = False

if not st.session_state.ai_qs:
    c1, c2 = st.columns(2)
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
        topics = sorted(set(t["topic_title"] for t in t_res.data)) if t_res.data else ["Chemistry"]
    except Exception:
        topics = ["Chemistry"]
    topic = st.selectbox("Topic", topics, index=0)
    num = st.slider("Number of questions", 10, 50, 50, step=5)
    st.info("CoreKnow will generate " + str(num) + " hard unique questions. Takes ~30-60 seconds.")
    if st.button("Generate " + str(num) + " Hard Questions", type="primary", use_container_width=True):
        with st.spinner("Generating..."):
            lesson_text = ""
            try:
                syl_res = supabase.table("education_syllabi").select("id").eq("exam", exam).eq("subject", subject).eq("topic_title", topic).execute()
                if syl_res.data:
                    sid = syl_res.data[0]["id"]
                    les_res = supabase.table("education_lessons").select("lesson_text").eq("syllabus_id", sid).execute()
                    if les_res.data:
                        lesson_text = les_res.data[0]["lesson_text"] or ""
            except Exception:
                pass
            qs, err = generate_hard_mcqs(topic, lesson_text, num_questions=num, difficulty="hard")
            if err:
                st.error("Generation failed: " + err)
            elif not qs:
                st.warning("No questions returned. Try again.")
            else:
                random.shuffle(qs)
                st.session_state.ai_qs = qs[:num]
                st.session_state.ai_idx = 0
                st.session_state.ai_score = 0
                st.session_state.ai_answered = False
                st.session_state.ai_selected = None
                st.session_state.ai_history = []
                st.session_state.ai_finished = False
                st.rerun()

elif not st.session_state.ai_finished:
    qs = st.session_state.ai_qs
    idx = st.session_state.ai_idx
    q = qs[idx]
    st.progress(idx / len(qs))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="stat-box"><div class="stat-num">' + str(idx+1) + "/" + str(len(qs)) + '</div><div class="stat-lbl">Question</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-box"><div class="stat-num">' + str(st.session_state.ai_score) + '</div><div class="stat-lbl">Correct</div></div>', unsafe_allow_html=True)
    with c3:
        pct = int((st.session_state.ai_score / (idx + 1)) * 100) if idx > 0 or st.session_state.ai_answered else 0
        st.markdown('<div class="stat-box"><div class="stat-num">' + str(pct) + '%</div><div class="stat-lbl">Accuracy</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="q-card"><div class="q-number">QUESTION ' + str(idx+1) + '</div><div class="q-text">' + q["question"] + '</div></div>', unsafe_allow_html=True)
    labels = ["A", "B", "C", "D"]
    if not st.session_state.ai_answered:
        for i, opt in enumerate(q["options"][:4]):
            if st.button(labels[i] + ". " + opt, key="ai_opt_" + str(idx) + "_" + str(i), use_container_width=True):
                st.session_state.ai_selected = labels[i]
                st.session_state.ai_answered = True
                correct = q["correct"].upper()
                is_correct = (labels[i] == correct)
                if is_correct:
                    st.session_state.ai_score += 1
                st.session_state.ai_history.append({
                    "question": q["question"],
                    "selected": labels[i],
                    "correct": correct,
                    "solution": q.get("solution", ""),
                    "is_correct": is_correct
                })
                st.rerun()
    else:
        correct = q["correct"].upper()
        is_correct = (st.session_state.ai_selected == correct)
        if is_correct:
            st.markdown('<div class="sol-correct"><strong>Correct!</strong> You selected ' + str(st.session_state.ai_selected) + '</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sol-wrong"><strong>Incorrect</strong><br>You selected: ' + str(st.session_state.ai_selected) + '<br>Correct: ' + correct + '</div>', unsafe_allow_html=True)
        st.markdown("#### Options:")
        for i, opt in enumerate(q["options"][:4]):
            mark = " [CORRECT]" if labels[i] == correct else (" [YOUR PICK]" if labels[i] == st.session_state.ai_selected else "")
            st.markdown("**" + labels[i] + ".** " + opt + mark)
        st.markdown('<div class="sol-box"><strong>Full Solution:</strong><br><br>' + q.get("solution", "N/A") + '</div>', unsafe_allow_html=True)
        if idx + 1 < len(qs):
            if st.button("Next Question", type="primary", use_container_width=True):
                st.session_state.ai_idx += 1
                st.session_state.ai_answered = False
                st.session_state.ai_selected = None
                st.rerun()
        else:
            if st.button("Finish Practice", type="primary", use_container_width=True):
                st.session_state.ai_finished = True
                st.rerun()

else:
    score = st.session_state.ai_score
    total = len(st.session_state.ai_qs)
    pct = int((score / total) * 100) if total else 0
    color = "#00c853" if pct >= 70 else "#ff9800" if pct >= 50 else "#ff1744"
    st.markdown('<div class="q-card" style="text-align:center;"><div style="font-family:Orbitron,monospace;font-size:4rem;font-weight:900;color:' + color + ';">' + str(pct) + '%</div><div style="font-size:1.3rem;">Score: ' + str(score) + ' / ' + str(total) + '</div></div>', unsafe_allow_html=True)
    st.markdown("### Full Review with Solutions")
    for i, h in enumerate(st.session_state.ai_history, 1):
        icon = "OK" if h["is_correct"] else "X"
        with st.expander("[" + icon + "] Q" + str(i) + ": " + h["question"][:70]):
            st.markdown("**Your answer:** " + h["selected"] + " | **Correct:** " + h["correct"])
            st.markdown("**Solution:** " + h.get("solution", "N/A"))
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Generate New Questions", use_container_width=True):
            st.session_state.ai_qs = []
            st.session_state.ai_idx = 0
            st.session_state.ai_score = 0
            st.session_state.ai_answered = False
            st.session_state.ai_selected = None
            st.session_state.ai_history = []
            st.session_state.ai_finished = False
            st.rerun()
    with c2:
        if st.button("Back to JAMB", use_container_width=True):
            st.switch_page("pages/11_JAMB.py")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
