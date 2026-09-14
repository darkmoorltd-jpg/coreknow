import streamlit as st
import sys
import os
import time

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from supabase import create_client
from utils.ai_generator import generate_exam, grade_uploaded_answers, extract_text_from_image

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 0%, #0d1b2a 0%, #050810 100%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background: #0a0e17; border-right: 1px solid #1f2a44; }
    .ck-title { font-family: 'Orbitron', sans-serif; font-size: 2.4rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #ff1744 0%, #ff8c00 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .ck-sub { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }
    .q-card { background: #0d1117; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem 1.5rem; margin: 0.5rem 0; }
    .exam-timer { font-family: Orbitron, monospace; font-size: 2rem; color: #ff1744; text-align: center; }
    .result-card { background: #0d1117; border: 2px solid #1f2a44; border-radius: 12px; padding: 1.5rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ck-title">Exam Mode</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">FULL EXAM · UPLOAD ANSWERS · AUTO-GRADED</div>', unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_key"])
except Exception as e:
    st.error("Supabase failed: " + str(e))
    st.stop()

if "exam_qs" not in st.session_state: st.session_state.exam_qs = []
if "exam_start" not in st.session_state: st.session_state.exam_start = None
if "exam_duration" not in st.session_state: st.session_state.exam_duration = 60
if "exam_grades" not in st.session_state: st.session_state.exam_grades = None
if "exam_submitted" not in st.session_state: st.session_state.exam_submitted = False

if not st.session_state.exam_qs:
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
    num = st.slider("Questions", 20, 60, 40, step=5)
    duration = st.slider("Duration (minutes)", 30, 180, 60, step=15)
    st.info("CoreKnow will generate a " + str(num) + "-question exam. Write answers on paper, then upload photos.")
    if st.button("Start Exam", type="primary", use_container_width=True):
        with st.spinner("Generating exam..."):
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
            qs, err = generate_exam(topic, lesson_text, num_questions=num)
            if err:
                st.error("Failed: " + err)
            elif qs:
                st.session_state.exam_qs = qs
                st.session_state.exam_start = time.time()
                st.session_state.exam_duration = duration
                st.session_state.exam_submitted = False
                st.session_state.exam_grades = None
                st.rerun()

elif not st.session_state.exam_submitted:
    elapsed = time.time() - st.session_state.exam_start
    remaining = (st.session_state.exam_duration * 60) - elapsed
    if remaining < 0:
        remaining = 0
    mins = int(remaining // 60)
    secs = int(remaining % 60)
    st.markdown('<div class="exam-timer">Time Left: ' + str(mins).zfill(2) + ':' + str(secs).zfill(2) + '</div>', unsafe_allow_html=True)
    st.markdown("### Exam Paper")
    st.info("Write your answers (A/B/C/D) on paper. When done, upload photos below.")
    for i, q in enumerate(st.session_state.exam_qs, 1):
        st.markdown(
            '<div class="q-card"><strong>Q' + str(i) + '.</strong> ' + q["question"] + '<br><br>'
            'A. ' + q["options"][0] + '<br>'
            'B. ' + q["options"][1] + '<br>'
            'C. ' + q["options"][2] + '<br>'
            'D. ' + q["options"][3] + '</div>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown("### Upload Answer Sheet")
    files = st.file_uploader("Upload photos of your answer sheet", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if files and st.button("Submit Exam for Grading", type="primary", use_container_width=True):
        with st.spinner("Reading your answers..."):
            extracted = ""
            for f in files:
                extracted += "\n" + extract_text_from_image(f.getvalue())
        if not extracted.strip():
            st.error("Could not read text from upload.")
        else:
            with st.spinner("Grading..."):
                grades, err = grade_uploaded_answers(extracted, st.session_state.exam_qs)
            if err:
                st.error("Grading failed: " + err)
            else:
                st.session_state.exam_grades = grades
                st.session_state.exam_submitted = True
                st.rerun()
    if st.button("Cancel Exam"):
        st.session_state.exam_qs = []
        st.session_state.exam_start = None
        st.session_state.exam_submitted = False
        st.rerun()

else:
    grades = st.session_state.exam_grades or []
    correct = sum(1 for g in grades if g.get("correct"))
    total = len(st.session_state.exam_qs)
    pct = int((correct / total) * 100) if total else 0
    color = "#00c853" if pct >= 70 else "#ff9800" if pct >= 50 else "#ff1744"
    st.markdown(
        '<div class="result-card">'
        '<div style="font-family:Orbitron,monospace;font-size:4rem;font-weight:900;color:' + color + ';">' + str(pct) + '%</div>'
        '<div style="font-size:1.3rem;">Score: ' + str(correct) + ' / ' + str(total) + '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("### Detailed Grading")
    for i, g in enumerate(grades, 1):
        q_num = g.get("q", i)
        student = g.get("student_answer", "?")
        is_correct = g.get("correct", False)
        note = g.get("note", "")
        icon = "OK" if is_correct else "X"
        q = st.session_state.exam_qs[i-1] if i-1 < len(st.session_state.exam_qs) else {}
        with st.expander("[" + icon + "] Q" + str(q_num) + ": " + str(q.get("question", ""))[:70]):
            st.markdown("**Your answer:** " + str(student))
            st.markdown("**Correct answer:** " + str(q.get("correct", "?")))
            st.markdown("**Feedback:** " + str(note))
            st.markdown("**Full solution:** " + str(q.get("solution", "N/A")))
    if st.button("Take Another Exam", use_container_width=True):
        st.session_state.exam_qs = []
        st.session_state.exam_start = None
        st.session_state.exam_submitted = False
        st.session_state.exam_grades = None
        st.rerun()

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
