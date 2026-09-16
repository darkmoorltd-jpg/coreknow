"""JSS1 Learn — subject to term to topic to lesson."""
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="JSS1 Learn", page_icon="book", layout="wide")

SUPABASE_URL = "https://mzxbndfmeuewmbhwiotc.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16eGJuZGZtZXVld21iaHdpb3RjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4Nzc2MDYzMSwiZXhwIjoyMTAzMzM2NjMxfQ.exIJUdXXW6ayyfihUfT0X7UkUeLcRPvEjv9rr3B71LU"

@st.cache_resource
def get_sb():
    return create_client(SUPABASE_URL, SERVICE_KEY)

sb = get_sb()

st.markdown("""
<style>
.stApp { background: #0a0a0f; }
.topic-card {
    background: #161620;
    border: 1px solid #2d2d41;
    border-left: 4px solid #5876ff;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
}
.ex-box {
    background: #161620;
    border: 1px solid #2d2d41;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}
.ex-q { color: #ebecf5; font-size: 17px; font-weight: 600; margin-bottom: 14px; }
.badge-easy { background: rgba(0,215,130,0.13); color: #00d782; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 1px; display: inline-block; margin-bottom: 10px; }
.badge-medium { background: rgba(255,190,60,0.13); color: #ffbe3c; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 1px; display: inline-block; margin-bottom: 10px; }
.badge-hard { background: rgba(255,90,100,0.13); color: #ff5a64; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 1px; display: inline-block; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

params = st.query_params
topic_id_raw = params.get("topic_id")
subject_raw = params.get("subject")

# ===== STATE 3: Topic detail =====
if topic_id_raw:
    topic_id = int(topic_id_raw)
    syl = sb.table("education_syllabi").select("*").eq("id", topic_id).execute()
    if not syl.data:
        st.error("Topic not found.")
        st.stop()
    s = syl.data[0]

    col_a, col_b = st.columns([1, 5])
    with col_a:
        if st.button("Back", use_container_width=True):
            st.query_params.clear()
            if subject_raw:
                st.query_params["subject"] = subject_raw
            st.rerun()
    with col_b:
        st.caption(str(s.get("exam")) + " - Term " + str(s.get("term", 1)) + " - Topic " + str(s.get("topic_number")))

    st.markdown("## " + str(s.get("subject")) + " - " + str(s.get("topic_title")))

    # Concept video
    folder = "jss1/math/t1/t" + str(s.get("topic_number"))
    try:
        files = sb.storage.from_("math-videos").list(folder)
        concept = [f for f in (files or []) if f["name"] == "concept.mp4"]
        if concept:
            vurl = sb.storage.from_("math-videos").get_public_url(folder + "/concept.mp4")
            st.markdown("#### Concept Video")
            st.video(vurl)
    except Exception:
        pass

    # Lesson + exercises
    les = sb.table("education_lessons").select("*").eq("syllabus_id", topic_id).execute()
    if les.data:
        lid = les.data[0]["id"]
        st.markdown("---")
        st.markdown("## Lesson")
        st.markdown(les.data[0].get("lesson_text", ""))

        exs = sb.table("lesson_exercises").select("*").eq("lesson_id", lid).order("exercise_order").execute()
        if exs.data:
            st.markdown("---")
            st.markdown("## Practice (" + str(len(exs.data)) + " exercises)")
            st.caption("Tap an option, then open Hint or Solution.")

            for ex in exs.data:
                eid = ex["id"]
                diff = ex["difficulty"]

                st.markdown('<span class="badge-' + diff + '">' + diff.upper() + '</span>', unsafe_allow_html=True)
                st.markdown('<div class="ex-q">Q' + str(ex["exercise_order"]) + '. ' + ex["question"] + '</div>', unsafe_allow_html=True)

                opts = ex.get("options") or []
                cols = st.columns(2)
                for i, opt in enumerate(opts):
                    letter = chr(65 + i)
                    with cols[i % 2]:
                        if st.button(letter + ")  " + opt, key="btn_" + str(eid) + "_" + str(i), use_container_width=True):
                            st.session_state["ans_" + str(eid)] = i

                ans = st.session_state.get("ans_" + str(eid))
                if ans is not None:
                    if ans == ex["correct_index"]:
                        st.success("Correct! (" + chr(65 + ans) + ")")
                    else:
                        st.error("You picked " + chr(65 + ans) + ". Try again or reveal the solution.")

                c1, c2, c3 = st.columns(3)
                with c1:
                    with st.expander("Hint"):
                        st.write(ex.get("hint") or "No hint.")
                with c2:
                    with st.expander("Solution"):
                        for step in (ex.get("solution_steps") or []):
                            st.write(step)
                with c3:
                    if ex.get("video_url"):
                        with st.expander("Video"):
                            st.video(ex["video_url"])
                    else:
                        st.caption("No video")

                st.markdown("---")

    st.stop()

# ===== STATE 2: Subjects =====
all_syl = sb.table("education_syllabi").select("subject").eq("exam", "JSS1").execute()
subjects = sorted(set(r["subject"] for r in all_syl.data))

if not subject_raw:
    st.markdown("# JSS1")
    st.caption("Nigeria - Junior Secondary School Year 1")
    st.markdown("---")

    if not subjects:
        st.warning("No JSS1 subjects found.")
        st.stop()

    st.markdown("### Choose a subject")
    cols = st.columns(3)
    for i, subj in enumerate(subjects):
        with cols[i % 3]:
            cnt = sb.table("education_syllabi").select("id", count="exact").eq("exam", "JSS1").eq("subject", subj).execute().count or 0
            with st.container(border=True):
                st.markdown("### " + subj)
                st.caption(str(cnt) + " topics")
                if st.button("Open", key="subj_" + subj, use_container_width=True):
                    st.query_params["subject"] = subj
                    st.rerun()
    st.stop()

# ===== STATE 1: Terms + topics =====
subject = subject_raw

col_a, col_b = st.columns([1, 5])
with col_a:
    if st.button("Subjects", use_container_width=True):
        st.query_params.clear()
        st.rerun()
with col_b:
    st.markdown("### JSS1 - " + subject)

st.markdown("---")

topics_r = sb.table("education_syllabi").select("*").eq("exam", "JSS1").eq("subject", subject).order("topic_number").execute()
topics = topics_r.data or []

if not topics:
    st.info("No topics for " + subject + " yet.")
    st.stop()

from collections import defaultdict
by_term = defaultdict(list)
for t in topics:
    term_key = t.get("term") or 1
    try:
        term_key = int(term_key)
    except Exception:
        term_key = 1
    by_term[term_key].append(t)

terms_present = sorted(by_term.keys())
tab_labels = ["Term " + str(t) for t in terms_present]
tabs = st.tabs(tab_labels)

for i, term_num in enumerate(terms_present):
    with tabs[i]:
        st.caption(str(len(by_term[term_num])) + " topics")
        for t in by_term[term_num]:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown("**Topic " + str(t["topic_number"]) + ". " + str(t["topic_title"]) + "**")
                with c2:
                    if st.button("Open", key="t_" + str(t["id"]), use_container_width=True):
                        st.query_params["topic_id"] = str(t["id"])
                        st.query_params["subject"] = subject
                        st.rerun()
