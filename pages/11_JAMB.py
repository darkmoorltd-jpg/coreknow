import streamlit as st
from utils.student_style import apply_theme
from supabase import create_client

st.set_page_config(page_title="JAMB", page_icon="📚", layout="wide")
apply_theme()

SUPABASE_URL = st.secrets["supabase"]["url"]
SERVICE_KEY = st.secrets["supabase"]["service_key"]
supabase = create_client(SUPABASE_URL, SERVICE_KEY)

EXAM_NAME = "JAMB"

st.markdown('<div class="ck-title">📚 ' + EXAM_NAME + '</div>', unsafe_allow_html=True)
st.markdown('<div class="ck-sub">Select a subject to begin learning</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎓 CoreKnow Student")
    st.markdown("---")
    st.page_link("pages/10_CoreKnow_Student.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/11_JAMB.py", label="📕 JAMB", use_container_width=True)
    st.page_link("pages/12_WAEC.py", label="📘 WAEC", use_container_width=True)
    st.page_link("pages/13_GCE.py", label="📗 GCE", use_container_width=True)
    st.page_link("pages/14_NECO.py", label="📙 NECO", use_container_width=True)
    st.page_link("pages/15_JSS_SS.py", label="🏫 JSS1–SS3", use_container_width=True)

# Fetch subjects
try:
    subjects_res = supabase.table("education_syllabi").select("subject").eq("exam", EXAM_NAME).execute()
    subjects = sorted(list(set([s["subject"] for s in subjects_res.data])))
except Exception as e:
    subjects = []

if not subjects:
    st.warning("📭 No subjects yet for " + EXAM_NAME + ". Content is being added.")
    st.info("Try **JAMB → Chemistry** — it's fully loaded with 18 topics and lessons.")
    st.stop()

subject = st.selectbox("📖 Select Subject", subjects, index=0)

if subject:
    st.markdown("### 📋 " + subject + " Topics")

    try:
        topics_res = supabase.table("education_syllabi") \
            .select("id, topic_number, topic_title, subtopics, learning_objectives, contents_notes") \
            .eq("exam", EXAM_NAME) \
            .eq("subject", subject) \
            .order("topic_number") \
            .execute()
        topics = topics_res.data
    except:
        topics = []

    if not topics:
        st.info("No topics yet for " + subject + ". Coming soon.")
    else:
        try:
            lessons_res = supabase.table("education_lessons").select("syllabus_id, lesson_text").execute()
            lesson_map = {l["syllabus_id"]: l["lesson_text"] for l in lessons_res.data}
        except:
            lesson_map = {}

        for t in topics:
            has_lesson = t["id"] in lesson_map
            subs = t.get("subtopics") or []
            objs = t.get("learning_objectives") or []
            status = "✅ Lesson ready" if has_lesson else "📝 Lesson coming soon"

            st.markdown(
                '<div class="topic-card">'
                '<div class="topic-title">[' + str(t["topic_number"]).zfill(2) + '] ' + str(t["topic_title"]) + '</div>'
                '<div class="topic-meta">📌 ' + str(len(subs)) + ' subtopics · 🎯 ' + str(len(objs)) + ' objectives · ' + status + '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            with st.expander("Open Topic " + str(t["topic_number"]) + " →", expanded=False):
                st.markdown("#### 🎯 Learning Objectives")
                for obj in objs:
                    st.markdown("- " + str(obj))

                st.markdown("#### 📌 Subtopics")
                for sub in subs:
                    st.markdown("- " + str(sub))

                if has_lesson:
                    st.markdown("---")
                    st.markdown("#### 📖 Full Lesson")
                    st.markdown(lesson_map[t["id"]])
                    st.markdown("---")
                    if st.button("Generate 5 Practice Questions", key="gen_" + str(t["id"])):
                        st.info("🧠 Question generator coming soon")
                else:
                    st.info("📝 Lesson content coming soon.")

                if st.button("Mark as Studied", key="studied_" + str(t["id"])):
                    st.success("✅ Progress saved! (Coming soon)")

st.markdown("---")
st.caption("CoreKnow Student · Powered by Darkmoor Ltd")
