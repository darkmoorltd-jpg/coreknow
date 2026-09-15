from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os
import httpx

app = FastAPI(title="CoreKnow API", version="1.0.0")


@app.get("/")
def root():
    return {
        "service": "CoreKnow API",
        "version": "1.0.0",
        "status": "live",
        "docs": "/docs",
        "endpoints": [
            "/api/health",
            "/api/subjects?exam=JAMB",
            "/api/subjects/{subject}/topics?exam=JAMB",
            "/api/lessons/{id}",
            "/api/chat  (POST)",
        ],
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://mzxbndfmeuewmbhwiotc.supabase.co"
_env_key = os.environ.get("SUPABASE_SERVICE_KEY") or ""
SUPABASE_KEY = _env_key if len(_env_key) > 200 else "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16eGJuZGZtZXVld21iaHdpb3RjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4Nzc2MDYzMSwiZXhwIjoyMTAzMzM2NjMxfQ.exIJUdXXW6ayyfihUfT0X7UkUeLcRPvEjv9rr3B71LU"
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-YOUR_DEEPSEEK_KEY")
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

@app.get("/api/debug")
def debug():
    """Diagnose Supabase connection. Safe to leave in production."""
    import traceback
    out = {
        "supabase_url_set": bool(SUPABASE_URL),
        "supabase_url_starts_https": SUPABASE_URL.startswith("https://"),
        "supabase_key_set": bool(SUPABASE_KEY),
        "supabase_key_len": len(SUPABASE_KEY) if SUPABASE_KEY else 0,
        "supabase_key_starts_eyj": SUPABASE_KEY.startswith("eyJ") if SUPABASE_KEY else False,
        "deepseek_key_set": bool(DEEPSEEK_KEY),
    }
    try:
        r = sb.table("education_syllabi").select("id").limit(1).execute()
        out["supabase_query"] = "OK"
        out["rows_returned"] = len(r.data)
        out["sample"] = r.data[0] if r.data else None
    except Exception as e:
        out["supabase_query"] = "FAILED"
        out["error_type"] = type(e).__name__
        out["error_message"] = str(e)[:500]
        out["traceback"] = traceback.format_exc()[-800:]
    return out
