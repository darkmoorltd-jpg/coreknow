from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os
import httpx

app = FastAPI(title="CoreKnow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
DEEPSEEK_KEY = os.environ["DEEPSEEK_API_KEY"]
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/subjects")
def list_subjects(exam: str = "JAMB"):
    r = sb.table("education_syllabi").select("subject").eq("exam", exam).execute()
    subjects = sorted(set(row["subject"] for row in r.data))
    return {"exam": exam, "subjects": subjects}

@app.get("/api/subjects/{subject}/topics")
def list_topics(subject: str, exam: str = "JAMB"):
    r = sb.table("education_syllabi").select("id, topic_number, topic_title, subtopics").eq("exam", exam).eq("subject", subject).order("topic_number").execute()
    return {"subject": subject, "exam": exam, "topics": r.data}

@app.get("/api/lessons/{syllabus_id}")
def get_lesson(syllabus_id: int):
    syl = sb.table("education_syllabi").select("*").eq("id", syllabus_id).execute()
    if not syl.data:
        raise HTTPException(404, "Lesson not found")
    lesson = sb.table("education_lessons").select("*").eq("syllabus_id", syllabus_id).execute()
    return {"syllabus": syl.data[0], "lesson": lesson.data[0] if lesson.data else None}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    system = "You are CoreKnow, an AI tutor for Nigerian students preparing for JAMB, WAEC, NECO, GCE, and secondary school. Answer step by step, in simple language. Use Nigerian context. Be warm and encouraging. Never reveal what model powers you."
    messages = [{"role": "system", "content": system}]
    for h in req.history[-10:]:
        messages.append(h)
    messages.append({"role": "user", "content": req.message})
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
            json={"model": "deepseek-chat", "messages": messages, "temperature": 0.7},
        )
        data = r.json()
    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        reply = "Sorry, I could not generate a response."
    return {"reply": reply}