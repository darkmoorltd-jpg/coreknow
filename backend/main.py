from fastapi import FastAPI, HTTPException, Request
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

class TrackRequest(BaseModel):
    event: str
    user_id: str = ""
    data: dict = {}


@app.post("/api/track")
async def track(req: TrackRequest):
    try:
        sb.table("analytics_events").insert({
            "event": req.event,
            "user_id": req.user_id,
            "data": req.data,
        }).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


class PaymentRequest(BaseModel):
    user_id: str
    amount: int
    currency: str = "NGN"
    plan: str = "monthly"
    reference: str = ""
    status: str = "pending"


@app.get("/api/payments/history/{user_id}")
def payment_history(user_id: str):
    try:
        r = sb.table("payments") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        return {"payments": r.data}
    except Exception as e:
        return {"payments": [], "error": str(e)[:200]}


@app.post("/api/payments")
async def create_payment(req: PaymentRequest):
    try:
        r = sb.table("payments").insert({
            "user_id": req.user_id,
            "amount": req.amount,
            "currency": req.currency,
            "plan": req.plan,
            "reference": req.reference,
            "status": req.status,
        }).execute()
        return {"ok": True, "payment": r.data[0] if r.data else None}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/payments/status/{user_id}")
def payment_status(user_id: str):
    """Check if user has an active subscription."""
    try:
        r = sb.table("payments") \
            .select("*", count="exact") \
            .eq("user_id", user_id) \
            .eq("status", "paid") \
            .execute()
        active = r.count > 0 if r.count else False
        return {"active": active, "count": r.count}
    except Exception as e:
        return {"active": False, "error": str(e)[:200]}




PAYSTACK_KEY = os.environ.get("PAYSTACK_SECRET_KEY") or ""


class InitSubRequest(BaseModel):
    user_id: str
    email: str
    tier: str = "pro"
    referral_code: str = ""
    discount_code: str = ""


@app.get("/api/access/{user_id}")
def get_access(user_id: str):
    try:
        r = sb.rpc("has_premium_access", {"p_user_id": user_id}).execute()
        has = bool(r.data) if r.data is not None else False
        sub = sb.table("subscriptions").select("*").eq("user_id", user_id).execute()
        return {
            "hasAccess": has,
            "subscription": sub.data[0] if sub.data else None,
        }
    except Exception as e:
        return {"hasAccess": False, "error": str(e)[:200]}


@app.post("/api/subscribe/init")
def init_subscription(req: InitSubRequest):
    if not PAYSTACK_KEY:
        return {"ok": False, "error": "PAYSTACK_SECRET_KEY not set"}

    amount = 500000  # N5000 in kobo
    if req.tier == "school":
        amount = 50000000  # N500,000 in kobo

    if req.discount_code:
        try:
            d = sb.table("discount_codes").select("*").eq("code", req.discount_code).eq("active", True).execute()
            if d.data:
                code = d.data[0]
                if code["discount_type"] == "percent":
                    amount = int(amount * (100 - code["discount_value"]) / 100)
                else:
                    amount = max(0, amount - code["discount_value"] * 100)
        except Exception:
            pass

    if req.referral_code:
        try:
            rc = sb.table("referral_codes").select("*").eq("code", req.referral_code).execute()
            if rc.data:
                amount = max(0, amount - rc.data[0]["discount_amount"] * 100)
        except Exception:
            pass

    import time as _t
    ref = "CKN-" + req.user_id[:8] + "-" + str(int(_t.time()))

    try:
        resp = httpx.post(
            "https://api.paystack.co/transaction/initialize",
            headers={"Authorization": "Bearer " + PAYSTACK_KEY},
            json={
                "email": req.email,
                "amount": amount,
                "reference": ref,
                "metadata": {
                    "user_id": req.user_id,
                    "tier": req.tier,
                    "referral_code": req.referral_code,
                },
            },
            timeout=30,
        )
        data = resp.json()
        if not data.get("status"):
            return {"ok": False, "error": data.get("message", "Paystack error")}

        sb.table("payments").insert({
            "user_id": req.user_id,
            "amount": amount // 100,
            "currency": "NGN",
            "plan": req.tier,
            "reference": ref,
            "status": "pending",
            "paystack_ref": ref,
        }).execute()

        return {
            "ok": True,
            "authorization_url": data["data"]["authorization_url"],
            "reference": ref,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


class VerifyRequest(BaseModel):
    reference: str


@app.post("/api/subscribe/verify")
def verify_subscription(req: VerifyRequest):
    if not PAYSTACK_KEY:
        return {"ok": False, "error": "PAYSTACK_SECRET_KEY not set"}

    try:
        resp = httpx.get(
            "https://api.paystack.co/transaction/verify/" + req.reference,
            headers={"Authorization": "Bearer " + PAYSTACK_KEY},
            timeout=30,
        )
        data = resp.json()
        if not data.get("status") or data["data"]["status"] != "success":
            return {"ok": False, "error": "Payment not successful"}

        meta = data["data"].get("metadata", {})
        user_id = meta.get("user_id", "")
        tier = meta.get("tier", "pro")
        ref_code = meta.get("referral_code", "")

        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30)

        sb.table("payments").update({
            "status": "paid",
            "verified_at": now.isoformat(),
        }).eq("reference", req.reference).execute()

        existing = sb.table("subscriptions").select("*").eq("user_id", user_id).execute()
        if existing.data:
            sb.table("subscriptions").update({
                "tier": tier,
                "status": "active",
                "current_period_ends_at": period_end.isoformat(),
                "updated_at": now.isoformat(),
            }).eq("user_id", user_id).execute()
        else:
            sb.table("subscriptions").insert({
                "user_id": user_id,
                "tier": tier,
                "status": "active",
                "current_period_ends_at": period_end.isoformat(),
            }).execute()

        if ref_code:
            try:
                rc = sb.table("referral_codes").select("*").eq("code", ref_code).execute()
                if rc.data:
                    referrer = rc.data[0]["user_id"]
                    sb.table("referral_uses").insert({
                        "code": ref_code,
                        "referrer_id": referrer,
                        "referee_id": user_id,
                    }).execute()
                    sb.table("referral_codes").update({
                        "uses": rc.data[0]["uses"] + 1,
                    }).eq("code", ref_code).execute()
            except Exception:
                pass

        return {"ok": True, "tier": tier, "period_end": period_end.isoformat()}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.post("/api/paystack/webhook")
async def paystack_webhook(request: Request):
    import hmac, hashlib, json as _json
    body = await request.body()
    sig = request.headers.get("x-paystack-signature", "")
    if not PAYSTACK_KEY:
        return {"ok": False}
    expected = hmac.new(PAYSTACK_KEY.encode(), body, hashlib.sha512).hexdigest()
    if sig != expected:
        raise HTTPException(400, "Invalid signature")

    data = _json.loads(body)
    if data.get("event") == "charge.success":
        ref = data["data"]["reference"]
        sb.table("payments").update({"status": "paid"}).eq("reference", ref).execute()

    return {"ok": True}



@app.post("/api/trial/start")
def start_trial(req: InitSubRequest):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=7)
    existing = sb.table("subscriptions").select("*").eq("user_id", req.user_id).execute()
    if existing.data:
        row = existing.data[0]
        if row.get("trial_ends_at"):
            return {"ok": False, "error": "Trial already used"}
        sb.table("subscriptions").update({
            "tier": "pro",
            "status": "trial",
            "trial_ends_at": trial_end.isoformat(),
        }).eq("user_id", req.user_id).execute()
    else:
        sb.table("subscriptions").insert({
            "user_id": req.user_id,
            "tier": "pro",
            "status": "trial",
            "trial_ends_at": trial_end.isoformat(),
        }).execute()
    return {"ok": True, "trial_ends_at": trial_end.isoformat()}



@app.get("/api/referrals/my-code/{user_id}")
def my_referral_code(user_id: str):
    import secrets
    try:
        r = sb.table("referral_codes").select("*").eq("user_id", user_id).execute()
        if r.data:
            return {"code": r.data[0]["code"], "uses": r.data[0]["uses"]}
        code = "CKN" + secrets.token_hex(3).upper()
        sb.table("referral_codes").insert({
            "user_id": user_id,
            "code": code,
        }).execute()
        return {"code": code, "uses": 0}
    except Exception as e:
        return {"code": "", "error": str(e)[:200]}


@app.post("/api/referrals/validate")
def validate_referral(req: InitSubRequest):
    try:
        r = sb.table("referral_codes").select("*").eq("code", req.referral_code.upper()).execute()
        if not r.data:
            return {"valid": False, "error": "Invalid code"}
        row = r.data[0]
        if row["uses"] >= row["max_uses"]:
            return {"valid": False, "error": "Code expired"}
        return {"valid": True, "discount": row["discount_amount"]}
    except Exception as e:
        return {"valid": False, "error": str(e)[:200]}



class SchoolRequest(BaseModel):
    school_name: str
    contact_email: str
    contact_phone: str = ""
    max_students: int = 100
    user_id: str


@app.post("/api/school/create")
def create_school(req: SchoolRequest):
    import secrets, time as _t
    try:
        code = "SCH" + secrets.token_hex(4).upper()
        ref = "SCH-" + str(int(_t.time()))
        sb.table("school_licenses").insert({
            "school_name": req.school_name,
            "contact_email": req.contact_email,
            "contact_phone": req.contact_phone,
            "max_students": req.max_students,
            "price": 500000,
            "active": False,
        }).execute()
        return {"ok": True, "reference": ref, "code": code}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.post("/api/school/join")
def join_school(req: InitSubRequest):
    try:
        code = req.referral_code  # reuse field for school code
        r = sb.table("school_licenses").select("*").eq("active", True).execute()
        match = None
        for lic in r.data:
            if lic["contact_email"].endswith("@" + code) or code in lic["school_name"].upper().replace(" ", ""):
                match = lic
                break
        if not match:
            return {"ok": False, "error": "Invalid school code"}
        if match["students_used"] >= match["max_students"]:
            return {"ok": False, "error": "License full"}
        sb.table("school_members").insert({
            "license_id": match["id"],
            "user_id": req.user_id,
        }).execute()
        sb.table("school_licenses").update({
            "students_used": match["students_used"] + 1,
        }).eq("id", match["id"]).execute()
        sb.table("subscriptions").upsert({
            "user_id": req.user_id,
            "tier": "school",
            "status": "active",
        }).execute()
        return {"ok": True, "school": match["school_name"]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}



# ============================================
# STREAKS
# ============================================
@app.post("/api/streaks/touch/{user_id}")
def touch_user_streak(user_id: str):
    try:
        r = sb.rpc("touch_streak", {"p_user_id": user_id}).execute()
        return {"ok": True, "streak": r.data[0] if r.data else None}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/streaks/{user_id}")
def get_user_streak(user_id: str):
    try:
        r = sb.table("streaks").select("*").eq("user_id", user_id).execute()
        return {"streak": r.data[0] if r.data else None}
    except Exception as e:
        return {"streak": None, "error": str(e)[:200]}


# ============================================
# BOOKMARKS
# ============================================
class BookmarkRequest(BaseModel):
    user_id: str
    lesson_id: int


@app.post("/api/bookmarks/toggle")
def toggle_bookmark(req: BookmarkRequest):
    try:
        existing = sb.table("bookmarks").select("*") \
            .eq("user_id", req.user_id).eq("lesson_id", req.lesson_id).execute()
        if existing.data:
            sb.table("bookmarks").delete() \
                .eq("user_id", req.user_id).eq("lesson_id", req.lesson_id).execute()
            return {"ok": True, "bookmarked": False}
        sb.table("bookmarks").insert({"user_id": req.user_id, "lesson_id": req.lesson_id}).execute()
        return {"ok": True, "bookmarked": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/bookmarks/{user_id}")
def list_bookmarks(user_id: str):
    try:
        bm = sb.table("bookmarks").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        ids = [b["lesson_id"] for b in bm.data]
        if not ids:
            return {"bookmarks": []}
        lessons = sb.table("education_lessons").select("id, topic_title").in_("id", ids).execute()
        lessons_map = {l["id"]: l for l in lessons.data}
        out = []
        for b in bm.data:
            if b["lesson_id"] in lessons_map:
                out.append({"lesson_id": b["lesson_id"], "topic_title": lessons_map[b["lesson_id"]]["topic_title"], "bookmarked_at": b["created_at"]})
        return {"bookmarks": out}
    except Exception as e:
        return {"bookmarks": [], "error": str(e)[:200]}


# ============================================
# NOTES
# ============================================
class NoteRequest(BaseModel):
    user_id: str
    lesson_id: int
    content: str


@app.post("/api/notes/save")
def save_note(req: NoteRequest):
    try:
        from datetime import datetime, timezone
        existing = sb.table("notes").select("*") \
            .eq("user_id", req.user_id).eq("lesson_id", req.lesson_id).execute()
        if existing.data:
            sb.table("notes").update({
                "content": req.content,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            sb.table("notes").insert({"user_id": req.user_id, "lesson_id": req.lesson_id, "content": req.content}).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/notes/{user_id}/{lesson_id}")
def get_note(user_id: str, lesson_id: int):
    try:
        r = sb.table("notes").select("*").eq("user_id", user_id).eq("lesson_id", lesson_id).execute()
        return {"note": r.data[0] if r.data else None}
    except Exception as e:
        return {"note": None, "error": str(e)[:200]}


# ============================================
# MCQ BANK
# ============================================
@app.get("/api/mcqs")
def list_mcqs(subject: str = "Chemistry", topic: int = 0, limit: int = 10):
    try:
        q = sb.table("mcqs").select("*").eq("subject", subject)
        if topic > 0:
            q = q.eq("topic_number", topic)
        r = q.limit(limit).execute()
        return {"mcqs": r.data}
    except Exception as e:
        return {"mcqs": [], "error": str(e)[:200]}


# ============================================
# REMINDER SETTINGS
# ============================================
class ReminderRequest(BaseModel):
    user_id: str
    enabled: bool = True
    hour: int = 19
    minute: int = 0


@app.post("/api/reminders/save")
def save_reminder(req: ReminderRequest):
    try:
        sb.table("reminder_settings").upsert({
            "user_id": req.user_id,
            "enabled": req.enabled,
            "hour": req.hour,
            "minute": req.minute,
        }).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/reminders/{user_id}")
def get_reminder(user_id: str):
    try:
        r = sb.table("reminder_settings").select("*").eq("user_id", user_id).execute()
        return {"reminder": r.data[0] if r.data else None}
    except Exception as e:
        return {"reminder": None, "error": str(e)[:200]}


# ============================================
# BADGES
# ============================================
@app.get("/api/badges/{user_id}")
def get_badges(user_id: str):
    try:
        r = sb.table("badges").select("*").eq("user_id", user_id).execute()
        return {"badges": r.data}
    except Exception as e:
        return {"badges": [], "error": str(e)[:200]}


class BadgeAward(BaseModel):
    user_id: str
    badge_key: str


@app.post("/api/badges/award")
def award_badge(req: BadgeAward):
    try:
        sb.table("badges").upsert({"user_id": req.user_id, "badge_key": req.badge_key}, on_conflict="user_id,badge_key").execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


# ============================================
# PARENT DASHBOARD
# ============================================
class ParentLinkRequest(BaseModel):
    parent_id: str
    child_email: str


@app.post("/api/parent/link")
def link_parent(req: ParentLinkRequest):
    try:
        users = sb.auth.admin.list_users()
        child = None
        for u in users:
            if u.email and u.email.lower() == req.child_email.lower():
                child = u
                break
        if not child:
            return {"ok": False, "error": "Child account not found"}
        sb.table("parent_links").upsert({"parent_id": req.parent_id, "child_id": child.id, "status": "active"}, on_conflict="parent_id,child_id").execute()
        return {"ok": True, "child_id": child.id}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/parent/dashboard/{parent_id}")
def parent_dashboard(parent_id: str):
    try:
        links = sb.table("parent_links").select("*").eq("parent_id", parent_id).execute()
        children = []
        for link in links.data:
            cid = link["child_id"]
            streak = sb.table("streaks").select("*").eq("user_id", cid).execute()
            badges = sb.table("badges").select("*").eq("user_id", cid).execute()
            children.append({
                "child_id": cid,
                "streak": streak.data[0] if streak.data else None,
                "badge_count": len(badges.data),
            })
        return {"children": children}
    except Exception as e:
        return {"children": [], "error": str(e)[:200]}



# ============================================
# FORMULA SHEETS
# ============================================
@app.get("/api/formulas")
def list_formulas(subject: str = ""):
    try:
        q = sb.table("formula_sheets").select("*")
        if subject:
            q = q.eq("subject", subject)
        r = q.order("subject").execute()
        return {"sheets": r.data}
    except Exception as e:
        return {"sheets": [], "error": str(e)[:200]}


# ============================================
# PAST QUESTIONS
# ============================================
@app.get("/api/past-questions")
def list_past(exam: str = "JAMB", subject: str = "", year: int = 0, limit: int = 20):
    try:
        q = sb.table("past_questions").select("*").eq("exam", exam)
        if subject:
            q = q.eq("subject", subject)
        if year > 0:
            q = q.eq("year", year)
        r = q.order("year", desc=True).limit(limit).execute()
        return {"questions": r.data}
    except Exception as e:
        return {"questions": [], "error": str(e)[:200]}


@app.get("/api/past-questions/years")
def past_years(exam: str = "JAMB", subject: str = ""):
    try:
        q = sb.table("past_questions").select("year").eq("exam", exam)
        if subject:
            q = q.eq("subject", subject)
        r = q.execute()
        years = sorted(set(row["year"] for row in r.data), reverse=True)
        return {"years": years}
    except Exception as e:
        return {"years": [], "error": str(e)[:200]}


# ============================================
# AI QUESTION GENERATION
# ============================================
class GenRequest(BaseModel):
    subject: str
    topic_number: int
    topic_title: str
    count: int = 10
    user_id: str = ""


@app.post("/api/ai/questions/generate")
async def generate_questions(req: GenRequest):
    if not DEEPSEEK_KEY:
        return {"ok": False, "error": "DEEPSEEK_API_KEY not set"}

    prompt = (
        "Generate " + str(req.count) + " JAMB-style multiple choice questions on '" + req.topic_title +
        "' for Nigerian students. Return ONLY a JSON array. Each object: "
        '{"question":"...","options":["A","B","C","D"],"correct_index":0-3,"explanation":"why"}.'
        " Make them exam-quality, no repeats, mix difficulties."
    )

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a JAMB exam question writer. Return valid JSON only, no markdown."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.8,
                },
            )
            data = r.json()

        raw = data["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        import json as _j
        questions = _j.loads(raw)

        inserted = []
        for q in questions[:req.count]:
            try:
                row = sb.table("mcqs").insert({
                    "subject": req.subject,
                    "topic_number": req.topic_number,
                    "question": q["question"],
                    "options": q["options"],
                    "correct_index": q["correct_index"],
                    "explanation": q.get("explanation", ""),
                    "source": "ai",
                }).execute()
                if row.data:
                    inserted.append(row.data[0])
            except Exception:
                pass

        sb.table("ai_generation_log").insert({
            "user_id": req.user_id,
            "questions_generated": len(inserted),
        }).execute()

        return {"ok": True, "questions": inserted}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


# ============================================
# BULK LESSON IMPORT
# ============================================
class ImportRequest(BaseModel):
    exam: str
    subject: str
    topic_number: int
    topic_title: str
    lesson_text: str
    subtopics: list = []


@app.post("/api/import/lesson")
def import_lesson(req: ImportRequest):
    try:
        existing = sb.table("education_syllabi").select("id") \
            .eq("exam", req.exam).eq("subject", req.subject) \
            .eq("topic_number", req.topic_number).execute()

        if existing.data:
            syl_id = existing.data[0]["id"]
            sb.table("education_syllabi").update({
                "topic_title": req.topic_title,
                "subtopics": req.subtopics,
            }).eq("id", syl_id).execute()
        else:
            ins = sb.table("education_syllabi").insert({
                "exam": req.exam,
                "subject": req.subject,
                "topic_number": req.topic_number,
                "topic_title": req.topic_title,
                "subtopics": req.subtopics,
            }).execute()
            syl_id = ins.data[0]["id"]

        les = sb.table("education_lessons").select("id") \
            .eq("syllabus_id", syl_id).execute()
        if les.data:
            sb.table("education_lessons").update({
                "lesson_text": req.lesson_text,
                "topic_title": req.topic_title,
            }).eq("id", les.data[0]["id"]).execute()
            lesson_id = les.data[0]["id"]
        else:
            ins2 = sb.table("education_lessons").insert({
                "syllabus_id": syl_id,
                "topic_title": req.topic_title,
                "lesson_text": req.lesson_text,
            }).execute()
            lesson_id = ins2.data[0]["id"]

        return {"ok": True, "syllabus_id": syl_id, "lesson_id": lesson_id}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


@app.get("/api/import/stats")
def import_stats():
    try:
        syl = sb.table("education_syllabi").select("id", count="exact").execute()
        les = sb.table("education_lessons").select("id", count="exact").execute()
        mcq = sb.table("mcqs").select("id", count="exact").execute()
        return {
            "syllabi": syl.count or 0,
            "lessons": les.count or 0,
            "mcqs": mcq.count or 0,
        }
    except Exception as e:
        return {"error": str(e)[:200]}



# ============================================
# AI PHOTO / HOMEWORK SCANNER
# ============================================
class ScanRequest(BaseModel):
    user_id: str = ""
    text: str
    language: str = "en"


@app.post("/api/scan/ask")
async def scan_ask(req: ScanRequest):
    if not DEEPSEEK_KEY:
        return {"ok": False, "error": "DEEPSEEK not configured"}

    lang_note = ""
    if req.language == "pidgin":
        lang_note = " Answer in Nigerian Pidgin English."
    elif req.language == "yoruba":
        lang_note = " Answer in Yoruba."
    elif req.language == "igbo":
        lang_note = " Answer in Igbo."
    elif req.language == "hausa":
        lang_note = " Answer in Hausa."

    system = (
        "You are CoreKnow, an AI tutor for Nigerian students. "
        "Read the question (possibly OCR'd from a photo) and solve it step by step. "
        "Be clear and encouraging." + lang_note
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": req.text},
                    ],
                    "temperature": 0.7,
                },
            )
            data = r.json()

        answer = data["choices"][0]["message"]["content"]
        try:
            sb.table("photo_scans").insert({
                "user_id": req.user_id,
                "extracted_text": req.text,
                "ai_answer": answer,
            }).execute()
        except Exception:
            pass
        return {"ok": True, "answer": answer}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


# ============================================
# AI MEMORY
# ============================================
@app.post("/api/memory/save")
def save_memory(req: ScanRequest):
    try:
        sb.table("ai_memory").insert({
            "user_id": req.user_id,
            "topic": req.language,
            "question": req.text[:500],
            "answer": "",
        }).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/memory/{user_id}")
def get_memory(user_id: str, limit: int = 20):
    try:
        r = sb.table("ai_memory").select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit).execute()
        return {"history": r.data}
    except Exception as e:
        return {"history": [], "error": str(e)[:200]}


# ============================================
# WEAK TOPICS
# ============================================
class WeakRequest(BaseModel):
    user_id: str
    subject: str
    topic: str
    correct: bool


@app.post("/api/weak/record")
def record_weak(req: WeakRequest):
    try:
        ex = sb.table("weak_topics").select("*") \
            .eq("user_id", req.user_id) \
            .eq("subject", req.subject) \
            .eq("topic", req.topic).execute()
        if ex.data:
            row = ex.data[0]
            new_attempts = row["attempts"] + 1
            new_correct = row["correct"] + (1 if req.correct else 0)
            acc = round(new_correct / new_attempts * 100, 2)
            sb.table("weak_topics").update({
                "attempts": new_attempts,
                "correct": new_correct,
                "accuracy": acc,
            }).eq("id", row["id"]).execute()
        else:
            sb.table("weak_topics").insert({
                "user_id": req.user_id,
                "subject": req.subject,
                "topic": req.topic,
                "attempts": 1,
                "correct": 1 if req.correct else 0,
                "accuracy": 100.0 if req.correct else 0.0,
            }).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/weak/{user_id}")
def get_weak(user_id: str):
    try:
        r = sb.table("weak_topics").select("*") \
            .eq("user_id", user_id) \
            .order("accuracy").execute()
        return {"topics": r.data}
    except Exception as e:
        return {"topics": [], "error": str(e)[:200]}


# ============================================
# PARENT EMAIL (weekly report)
# ============================================
@app.post("/api/parent/email-report/{parent_id}")
def email_report(parent_id: str):
    try:
        links = sb.table("parent_links").select("*") \
            .eq("parent_id", parent_id).execute()
        if not links.data:
            return {"ok": False, "error": "No linked children"}

        report = []
        for link in links.data:
            cid = link["child_id"]
            streak = sb.table("streaks").select("*").eq("user_id", cid).execute()
            weak = sb.table("weak_topics").select("*").eq("user_id", cid).order("accuracy").limit(3).execute()
            report.append({
                "child_id": cid,
                "streak": streak.data[0] if streak.data else None,
                "weakest_topics": weak.data,
            })
            try:
                sb.table("parent_links").update({
                    "last_email_at": "now()",
                }).eq("id", link["id"]).execute()
            except Exception:
                pass

        return {"ok": True, "report": report}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.post("/api/parent/set-frequency")
def set_frequency(req: ScanRequest):
    try:
        sb.table("parent_links").update({"email_frequency": req.text}) \
            .eq("parent_id", req.user_id).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


# ============================================
# LANGUAGE PREFERENCE
# ============================================
@app.post("/api/language/set")
def set_language(req: ScanRequest):
    try:
        sb.table("subscriptions").upsert({"user_id": req.user_id, "language": req.text}).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}



# ============================================
# PUSH TOKENS
# ============================================
class PushTokenRequest(BaseModel):
    user_id: str
    token: str
    platform: str = "android"


@app.post("/api/push/register")
def register_push(req: PushTokenRequest):
    try:
        sb.table("push_tokens").upsert({
            "user_id": req.user_id,
            "token": req.token,
            "platform": req.platform,
        }, on_conflict="user_id,token").execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


class PushSendRequest(BaseModel):
    title: str
    body: str
    user_ids: list = []


@app.post("/api/push/send")
async def send_push(req: PushSendRequest):
    try:
        if req.user_ids:
            tokens_r = sb.table("push_tokens").select("token").in_("user_id", req.user_ids).execute()
        else:
            tokens_r = sb.table("push_tokens").select("token").execute()

        tokens = [t["token"] for t in tokens_r.data if t.get("token", "").startswith("ExponentPushToken")]
        if not tokens:
            return {"ok": True, "sent": 0}

        messages = [{"to": t, "title": req.title, "body": req.body, "sound": "default"} for t in tokens[:100]]

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://exp.host/--/api/v2/push/send",
                json=messages,
                headers={"Content-Type": "application/json"},
            )
        return {"ok": True, "sent": len(messages)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


# ============================================
# LEADERBOARD
# ============================================
@app.get("/api/leaderboard")
def leaderboard(limit: int = 50):
    try:
        from datetime import date
        wk = date.today()
        wk = wk.fromordinal(wk.toordinal() - wk.weekday())
        r = sb.table("leaderboard_weekly").select("*") \
            .eq("week_start", wk.isoformat()) \
            .order("score", desc=True) \
            .limit(limit).execute()
        return {"week_start": wk.isoformat(), "leaderboard": r.data}
    except Exception as e:
        return {"leaderboard": [], "error": str(e)[:200]}


class PointsRequest(BaseModel):
    user_id: str
    points: int


@app.post("/api/leaderboard/add-points")
def add_points(req: PointsRequest):
    try:
        sb.rpc("update_leaderboard", {"p_user_id": req.user_id, "p_points": req.points}).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


# ============================================
# THEME + BIOMETRIC
# ============================================
class PrefRequest(BaseModel):
    user_id: str
    theme: str = "dark"
    biometric_enabled: bool = False


@app.post("/api/prefs/save")
def save_prefs(req: PrefRequest):
    try:
        sb.table("subscriptions").upsert({
            "user_id": req.user_id,
            "theme": req.theme,
            "biometric_enabled": req.biometric_enabled,
        }).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@app.get("/api/prefs/{user_id}")
def get_prefs(user_id: str):
    try:
        r = sb.table("subscriptions").select("theme, biometric_enabled").eq("user_id", user_id).execute()
        if r.data:
            return {"theme": r.data[0].get("theme", "dark"), "biometric_enabled": r.data[0].get("biometric_enabled", False)}
        return {"theme": "dark", "biometric_enabled": False}
    except Exception as e:
        return {"theme": "dark", "biometric_enabled": False}


# ============================================
# ERROR TRACKING
# ============================================
class ErrorRequest(BaseModel):
    user_id: str = ""
    message: str
    stack: str = ""
    platform: str = ""
    app_version: str = ""


@app.post("/api/errors/report")
def report_error(req: ErrorRequest):
    try:
        sb.table("app_errors").insert({
            "user_id": req.user_id,
            "message": req.message[:1000],
            "stack": req.stack[:2000],
            "platform": req.platform,
            "app_version": req.app_version,
        }).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False}


@app.get("/api/errors/recent")
def recent_errors(limit: int = 50):
    try:
        r = sb.table("app_errors").select("*").order("created_at", desc=True).limit(limit).execute()
        return {"errors": r.data}
    except Exception as e:
        return {"errors": [], "error": str(e)[:200]}


# ============================================
# ANALYTICS SUMMARY
# ============================================
@app.get("/api/analytics/summary")
def analytics_summary():
    try:
        users = sb.table("subscriptions").select("user_id", count="exact").execute()
        paid = sb.table("payments").select("id", count="exact").eq("status", "paid").execute()
        lessons = sb.table("education_lessons").select("id", count="exact").execute()
        mcqs = sb.table("mcqs").select("id", count="exact").execute()
        errors_24h = sb.table("app_errors").select("id", count="exact").execute()
        return {
            "users": users.count or 0,
            "paid_transactions": paid.count or 0,
            "total_lessons": lessons.count or 0,
            "total_mcqs": mcqs.count or 0,
            "errors_logged": errors_24h.count or 0,
        }
    except Exception as e:
        return {"error": str(e)[:200]}



# ============================================
# VOICE QUERIES
# ============================================
class VoiceAskRequest(BaseModel):
    user_id: str = ""
    transcript: str
    language: str = "en"
    duration_ms: int = 0


@app.post("/api/voice/ask")
async def voice_ask(req: VoiceAskRequest):
    if not DEEPSEEK_KEY:
        return {"ok": False, "error": "DEEPSEEK not configured"}

    system = (
        "You are CoreKnow, an AI tutor for Nigerian students. "
        "The user asked by voice. Answer clearly, step by step."
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": req.transcript},
                    ],
                    "temperature": 0.7,
                },
            )
            data = r.json()

        answer = data["choices"][0]["message"]["content"]
        try:
            sb.table("voice_history").insert({
                "user_id": req.user_id,
                "transcript": req.transcript,
                "ai_answer": answer,
                "language": req.language,
                "duration_ms": req.duration_ms,
            }).execute()
        except Exception:
            pass
        return {"ok": True, "answer": answer}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


@app.get("/api/voice/history/{user_id}")
def voice_history(user_id: str, limit: int = 30):
    try:
        r = sb.table("voice_history").select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit).execute()
        return {"history": r.data}
    except Exception as e:
        return {"history": [], "error": str(e)[:200]}


# ============================================
# ELI5 MODE
# ============================================
class Eli5Request(BaseModel):
    concept: str
    subject: str = ""


@app.post("/api/eli5")
async def eli5(req: Eli5Request):
    if not DEEPSEEK_KEY:
        return {"ok": False, "error": "DEEPSEEK not configured"}

    prompt = (
        "Explain '" + req.concept + "' in the simplest possible way, "
        "as if to a 10-year-old Nigerian child. Use everyday Nigerian examples "
        "(food, football, market, family). Keep it under 200 words. "
        "Use short sentences. End with a one-line summary in bold."
    )

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You explain hard things simply."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.8,
                },
            )
            data = r.json()
        return {"ok": True, "explanation": data["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


# ============================================
# ESSAY GRADING
# ============================================
class EssayRequest(BaseModel):
    user_id: str = ""
    subject: str
    essay_text: str
    max_score: int = 100


@app.post("/api/essay/grade")
async def grade_essay(req: EssayRequest):
    if not DEEPSEEK_KEY:
        return {"ok": False, "error": "DEEPSEEK not configured"}

    prompt = (
        "You are a JAMB/WAEC examiner. Grade this " + req.subject + " essay out of " + str(req.max_score) + ". "
        "Return ONLY JSON: "
        '{"score": number, "feedback": "2-3 sentences", "strengths": ["..."], "improvements": ["..."]}. '
        "Be fair and encouraging.\n\nESSAY:\n" + req.essay_text
    )

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a strict but fair Nigerian examiner. Return JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            data = r.json()

        raw = data["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        import json as _j
        result = _j.loads(raw)

        sb.table("essay_grades").insert({
            "user_id": req.user_id,
            "subject": req.subject,
            "essay_text": req.essay_text[:5000],
            "score": int(result.get("score", 0)),
            "max_score": req.max_score,
            "feedback": result.get("feedback", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
        }).execute()

        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


# ============================================
# CAPTIONS
# ============================================
@app.get("/api/captions/{lesson_id}")
def get_captions(lesson_id: int):
    try:
        r = sb.table("lesson_captions").select("*").eq("lesson_id", lesson_id).execute()
        if r.data:
            return {"captions": r.data[0]["captions"]}
        return {"captions": []}
    except Exception as e:
        return {"captions": [], "error": str(e)[:200]}


class CaptionGenRequest(BaseModel):
    lesson_id: int
    lesson_title: str
    lesson_text: str


@app.post("/api/captions/generate")
async def generate_captions(req: CaptionGenRequest):
    if not DEEPSEEK_KEY:
        return {"ok": False, "error": "DEEPSEEK not configured"}

    prompt = (
        "Create 30 short captions (max 12 words each) from this lesson. "
        "Return ONLY JSON array of strings. Lesson title: " + req.lesson_title + ". "
        "Lesson excerpt:\n" + req.lesson_text[:4000]
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + DEEPSEEK_KEY},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Return valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.6,
                },
            )
            data = r.json()

        raw = data["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        import json as _j
        captions = _j.loads(raw)

        sb.table("lesson_captions").upsert({
            "lesson_id": req.lesson_id,
            "captions": captions,
        }, on_conflict="lesson_id").execute()

        return {"ok": True, "captions": captions}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}



# ============================================
# OFFLINE BUNDLE
# ============================================
@app.get('/api/offline/bundle/{lesson_id}')
def offline_bundle(lesson_id: int, data_saver: bool = False):
    try:
        les = sb.table('education_lessons').select('*').eq('id', lesson_id).execute()
        if not les.data:
            return {'ok': False, 'error': 'Lesson not found'}
        lesson = les.data[0]

        syl = sb.table('education_syllabi').select('*').eq('id', lesson.get('syllabus_id')).execute()
        topic_num = syl.data[0]['topic_number'] if syl.data else 0
        mcq = sb.table('mcqs').select('*').eq('topic_number', topic_num).limit(20).execute()

        text = lesson.get('lesson_text', '')
        video_urls = []
        import re as _re
        for line in text.split(chr(10)):
            if 'Watch Video' in line and 'http' in line:
                m = _re.search(r'\(([^)]+)\)', line)
                if m:
                    video_urls.append(m.group(1))

        return {
            'ok': True,
            'lesson': {
                'id': lesson['id'],
                'title': lesson.get('topic_title', ''),
                'text': text,
            },
            'syllabus': syl.data[0] if syl.data else None,
            'videos': [] if data_saver else video_urls,
            'mcqs': mcq.data if mcq else [],
            'version': 1,
        }
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}


@app.get('/api/offline/manifest/{user_id}')
def offline_manifest(user_id: str):
    try:
        r = sb.table('content_versions').select('lesson_id, version, updated_at').execute()
        return {'versions': r.data}
    except Exception as e:
        return {'versions': [], 'error': str(e)[:200]}


class OfflineTrackRequest(BaseModel):
    user_id: str
    lesson_id: int
    size_kb: int = 0


@app.post('/api/offline/track')
def track_download(req: OfflineTrackRequest):
    try:
        sb.table('offline_downloads').upsert({
            'user_id': req.user_id,
            'lesson_id': req.lesson_id,
            'size_kb': req.size_kb,
        }, on_conflict='user_id,lesson_id').execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/offline/list/{user_id}')
def list_downloads(user_id: str):
    try:
        r = sb.table('offline_downloads').select('*').eq('user_id', user_id).order('downloaded_at', desc=True).execute()
        return {'downloads': r.data}
    except Exception as e:
        return {'downloads': [], 'error': str(e)[:200]}


@app.delete('/api/offline/remove/{user_id}/{lesson_id}')
def remove_download(user_id: str, lesson_id: int):
    try:
        sb.table('offline_downloads').delete().eq('user_id', user_id).eq('lesson_id', lesson_id).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


class DataSaverRequest(BaseModel):
    user_id: str
    data_saver: bool
    auto_download_wifi: bool = True


@app.post('/api/prefs/data-saver')
def set_data_saver(req: DataSaverRequest):
    try:
        sb.table('subscriptions').upsert({
            'user_id': req.user_id,
            'data_saver': req.data_saver,
            'auto_download_wifi': req.auto_download_wifi,
        }).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.post('/api/sync/touch/{user_id}')
def touch_sync(user_id: str, items: int = 0):
    try:
        sb.table('sync_log').insert({
            'user_id': user_id,
            'items_synced': items,
        }).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/sync/last/{user_id}')
def last_sync(user_id: str):
    try:
        r = sb.table('sync_log').select('*').eq('user_id', user_id).order('last_sync_at', desc=True).limit(1).execute()
        return {'last_sync': r.data[0] if r.data else None}
    except Exception as e:
        return {'last_sync': None, 'error': str(e)[:200]}



# ============================================
# IN-MEMORY RATE LIMITER
# ============================================
_rate_buckets = {}

def _rate_check(key: str, limit: int, window_sec: int) -> bool:
    import time
    now = time.time()
    bucket = _rate_buckets.get(key, [])
    bucket = [t for t in bucket if now - t < window_sec]
    if len(bucket) >= limit:
        _rate_buckets[key] = bucket
        return False
    bucket.append(now)
    _rate_buckets[key] = bucket
    return True


@app.middleware('http')
async def rate_limit_middleware(request, call_next):
    path = request.url.path
    if path.startswith('/api/'):
        client_ip = request.client.host if request.client else 'anon'
        if path.startswith('/api/chat') or path.startswith('/api/scan') or path.startswith('/api/ai/'):
            if not _rate_check(client_ip + ':' + path.split('/')[2], 20, 60):
                from fastapi.responses import JSONResponse
                return JSONResponse({'detail': 'Too many requests. Slow down.'}, status_code=429)
        else:
            if not _rate_check(client_ip, 200, 60):
                from fastapi.responses import JSONResponse
                return JSONResponse({'detail': 'Rate limit exceeded.'}, status_code=429)
    return await call_next(request)


# ============================================
# PASSWORD RESET
# ============================================
class PasswordResetRequest(BaseModel):
    email: str


@app.post('/api/auth/forgot-password')
def forgot_password(req: PasswordResetRequest):
    import secrets
    from datetime import datetime, timedelta, timezone
    try:
        users = sb.auth.admin.list_users()
        user = None
        for u in users:
            if u.email and u.email.lower() == req.email.lower():
                user = u
                break
        if not user:
            return {'ok': True, 'message': 'If that email exists, a code has been sent.'}
        code = secrets.token_hex(3).upper()
        expires = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        sb.table('password_resets').insert({
            'user_id': user.id,
            'email': req.email.lower(),
            'code': code,
            'expires_at': expires,
        }).execute()
        dev_mode = not os.environ.get('RESEND_API_KEY')
        result = {'ok': True, 'message': 'Check your email for the reset code.'}
        if dev_mode:
            result['dev_code'] = code
        return result
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


class PasswordResetConfirm(BaseModel):
    email: str
    code: str
    new_password: str


@app.post('/api/auth/reset-password')
def reset_password(req: PasswordResetConfirm):
    from datetime import datetime, timezone
    try:
        r = sb.table('password_resets').select('*') \
            .eq('email', req.email.lower()).eq('code', req.code.upper()) \
            .eq('used', False).order('created_at', desc=True).limit(1).execute()
        if not r.data:
            return {'ok': False, 'error': 'Invalid or used code'}
        row = r.data[0]
        exp = datetime.fromisoformat(row['expires_at'].replace('Z', '+00:00'))
        if exp < datetime.now(timezone.utc):
            return {'ok': False, 'error': 'Code expired'}
        sb.auth.admin.update_user_by_id(row['user_id'], {'password': req.new_password})
        sb.table('password_resets').update({'used': True}).eq('id', row['id']).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# EMAIL VERIFICATION
# ============================================
class VerifyRequest(BaseModel):
    user_id: str
    email: str


@app.post('/api/auth/send-verification')
def send_verification(req: VerifyRequest):
    import secrets
    from datetime import datetime, timedelta, timezone
    try:
        code = secrets.token_hex(3).upper()
        expires = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        sb.table('email_verifications').insert({
            'user_id': req.user_id,
            'email': req.email.lower(),
            'code': code,
            'expires_at': expires,
        }).execute()
        dev_mode = not os.environ.get('RESEND_API_KEY')
        result = {'ok': True}
        if dev_mode:
            result['dev_code'] = code
        return result
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


class VerifyConfirm(BaseModel):
    user_id: str
    code: str


@app.post('/api/auth/verify-email')
def verify_email(req: VerifyConfirm):
    try:
        r = sb.table('email_verifications').select('*') \
            .eq('user_id', req.user_id).eq('code', req.code.upper()) \
            .eq('verified', False).order('created_at', desc=True).limit(1).execute()
        if not r.data:
            return {'ok': False, 'error': 'Invalid code'}
        sb.table('email_verifications').update({'verified': True}).eq('id', r.data[0]['id']).execute()
        sb.table('subscriptions').upsert({'user_id': req.user_id, 'email_verified': True}).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# A/B TESTING
# ============================================
@app.get('/api/ab/variant/{test_key}/{user_id}')
def get_variant(test_key: str, user_id: str):
    try:
        t = sb.table('ab_tests').select('*').eq('test_key', test_key).eq('active', True).execute()
        if not t.data:
            return {'variant': 'a'}
        variants = t.data[0]['variants']
        ex = sb.table('ab_assignments').select('*').eq('test_key', test_key).eq('user_id', user_id).execute()
        if ex.data:
            return {'variant': ex.data[0]['variant']}
        h = 0
        for ch in (test_key + user_id):
            h = (h * 31 + ord(ch)) % 1000
        idx = h % len(variants)
        variant = variants[idx]
        sb.table('ab_assignments').insert({'test_key': test_key, 'user_id': user_id, 'variant': variant}).execute()
        return {'variant': variant}
    except Exception as e:
        return {'variant': 'a', 'error': str(e)[:200]}


@app.post('/api/ab/convert/{test_key}/{user_id}')
def ab_convert(test_key: str, user_id: str):
    try:
        sb.table('ab_assignments').update({'converted': True}) \
            .eq('test_key', test_key).eq('user_id', user_id).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/ab/results')
def ab_results():
    try:
        tests = sb.table('ab_tests').select('*').execute()
        out = []
        for t in tests.data:
            a = sb.table('ab_assignments').select('*').eq('test_key', t['test_key']).execute()
            counts = {}
            for row in a.data:
                v = row['variant']
                if v not in counts:
                    counts[v] = {'assigned': 0, 'converted': 0}
                counts[v]['assigned'] += 1
                if row.get('converted'):
                    counts[v]['converted'] += 1
            out.append({'test_key': t['test_key'], 'variants': counts})
        return {'results': out}
    except Exception as e:
        return {'results': [], 'error': str(e)[:200]}



# ============================================
# ADMIN CHECK
# ============================================
def _is_admin(user_id: str) -> bool:
    try:
        r = sb.table('subscriptions').select('is_admin').eq('user_id', user_id).execute()
        return bool(r.data and r.data[0].get('is_admin'))
    except Exception:
        return False


# ============================================
# ADMIN: LIST LESSONS
# ============================================
@app.get('/api/admin/lessons')
def admin_list_lessons(admin_id: str):
    if not _is_admin(admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        les = sb.table('education_lessons').select('*').order('id', desc=True).execute()
        syl_map = {}
        syl = sb.table('education_syllabi').select('id, exam, subject, topic_number, topic_title').execute()
        for s in syl.data:
            syl_map[s['id']] = s
        out = []
        for l in les.data:
            s = syl_map.get(l.get('syllabus_id'), {})
            out.append({
                'id': l['id'],
                'syllabus_id': l.get('syllabus_id'),
                'title': l.get('topic_title'),
                'status': l.get('status', 'published'),
                'version': l.get('version', 1),
                'exam': s.get('exam'),
                'subject': s.get('subject'),
                'topic_number': s.get('topic_number'),
            })
        return {'ok': True, 'lessons': out}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# ADMIN: CREATE + EDIT
# ============================================
class LessonSaveRequest(BaseModel):
    admin_id: str
    lesson_id: int = 0
    syllabus_id: int = 0
    exam: str = 'JAMB'
    subject: str = 'Chemistry'
    topic_number: int = 0
    topic_title: str
    lesson_text: str
    status: str = 'published'
    note: str = ''


@app.post('/api/admin/lesson/save')
def admin_save_lesson(req: LessonSaveRequest):
    if not _is_admin(req.admin_id):
        return {'ok': False, 'error': 'Not admin'}
    from datetime import datetime, timezone
    try:
        syl_id = req.syllabus_id
        if not syl_id and req.topic_number > 0:
            ex = sb.table('education_syllabi').select('id') \
                .eq('exam', req.exam).eq('subject', req.subject) \
                .eq('topic_number', req.topic_number).execute()
            if ex.data:
                syl_id = ex.data[0]['id']
            else:
                ins = sb.table('education_syllabi').insert({
                    'exam': req.exam,
                    'subject': req.subject,
                    'topic_number': req.topic_number,
                    'topic_title': req.topic_title,
                }).execute()
                syl_id = ins.data[0]['id']

        if req.lesson_id > 0:
            cur = sb.table('education_lessons').select('*').eq('id', req.lesson_id).execute()
            if cur.data:
                cur_v = cur.data[0].get('version', 1)
                sb.table('lesson_versions').insert({
                    'lesson_id': req.lesson_id,
                    'version': cur_v,
                    'lesson_text': cur.data[0].get('lesson_text', ''),
                    'topic_title': cur.data[0].get('topic_title', ''),
                    'saved_by': req.admin_id,
                    'note': 'auto-snapshot before edit',
                }).execute()
                new_v = cur_v + 1
                sb.table('education_lessons').update({
                    'lesson_text': req.lesson_text,
                    'topic_title': req.topic_title,
                    'status': req.status,
                    'version': new_v,
                }).eq('id', req.lesson_id).execute()
                sb.table('content_versions').upsert({
                    'lesson_id': req.lesson_id,
                    'version': new_v,
                }).execute()
                return {'ok': True, 'lesson_id': req.lesson_id, 'version': new_v}
        ins2 = sb.table('education_lessons').insert({
            'syllabus_id': syl_id,
            'topic_title': req.topic_title,
            'lesson_text': req.lesson_text,
            'status': req.status,
            'version': 1,
        }).execute()
        new_id = ins2.data[0]['id']
        sb.table('content_versions').upsert({
            'lesson_id': new_id,
            'version': 1,
        }).execute()
        return {'ok': True, 'lesson_id': new_id, 'version': 1}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}


# ============================================
# ADMIN: BULK IMPORT
# ============================================
class BulkImportRequest(BaseModel):
    admin_id: str
    exam: str = 'JAMB'
    subject: str = 'Chemistry'
    start_topic: int = 7
    items: list = []


@app.post('/api/admin/bulk-import')
def admin_bulk_import(req: BulkImportRequest):
    if not _is_admin(req.admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        created = 0
        failed = 0
        for i, item in enumerate(req.items):
            try:
                topic_num = req.start_topic + i
                title = item.get('title', 'Topic ' + str(topic_num))
                text = item.get('text', '')
                ex = sb.table('education_syllabi').select('id') \
                    .eq('exam', req.exam).eq('subject', req.subject) \
                    .eq('topic_number', topic_num).execute()
                if ex.data:
                    syl_id = ex.data[0]['id']
                else:
                    ins = sb.table('education_syllabi').insert({
                        'exam': req.exam,
                        'subject': req.subject,
                        'topic_number': topic_num,
                        'topic_title': title,
                    }).execute()
                    syl_id = ins.data[0]['id']
                les = sb.table('education_lessons').select('id') \
                    .eq('syllabus_id', syl_id).execute()
                if les.data:
                    sb.table('education_lessons').update({
                        'lesson_text': text,
                        'topic_title': title,
                    }).eq('id', les.data[0]['id']).execute()
                else:
                    sb.table('education_lessons').insert({
                        'syllabus_id': syl_id,
                        'topic_title': title,
                        'lesson_text': text,
                        'status': 'published',
                        'version': 1,
                    }).execute()
                created += 1
            except Exception:
                failed += 1
        return {'ok': True, 'created': created, 'failed': failed}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}


# ============================================
# ADMIN: VERSION HISTORY
# ============================================
@app.get('/api/admin/lesson/{lesson_id}/versions')
def admin_versions(lesson_id: int, admin_id: str):
    if not _is_admin(admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        r = sb.table('lesson_versions').select('*').eq('lesson_id', lesson_id).order('version', desc=True).execute()
        return {'ok': True, 'versions': r.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


class RollbackRequest(BaseModel):
    admin_id: str
    version: int


@app.post('/api/admin/lesson/{lesson_id}/rollback')
def admin_rollback(lesson_id: int, req: RollbackRequest):
    if not _is_admin(req.admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        r = sb.table('lesson_versions').select('*') \
            .eq('lesson_id', lesson_id).eq('version', req.version).execute()
        if not r.data:
            return {'ok': False, 'error': 'Version not found'}
        v = r.data[0]
        sb.table('education_lessons').update({
            'lesson_text': v['lesson_text'],
            'topic_title': v['topic_title'],
        }).eq('id', lesson_id).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# ADMIN: SCHEDULE
# ============================================
class ScheduleRequest(BaseModel):
    admin_id: str
    lesson_id: int
    publish_at: str


@app.post('/api/admin/schedule')
def admin_schedule(req: ScheduleRequest):
    if not _is_admin(req.admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        sb.table('lesson_schedules').insert({
            'lesson_id': req.lesson_id,
            'publish_at': req.publish_at,
            'created_by': req.admin_id,
        }).execute()
        sb.table('education_lessons').update({'status': 'scheduled'}).eq('id', req.lesson_id).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/admin/schedules')
def admin_schedules(admin_id: str):
    if not _is_admin(admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        r = sb.table('lesson_schedules').select('*').eq('published', False).order('publish_at').execute()
        return {'ok': True, 'schedules': r.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# ADMIN: CONTENT ANALYTICS
# ============================================
@app.get('/api/admin/analytics')
def admin_analytics(admin_id: str):
    if not _is_admin(admin_id):
        return {'ok': False, 'error': 'Not admin'}
    try:
        reads = sb.table('lesson_reads').select('*').execute()
        counts = {}
        for r in reads.data:
            lid = r['lesson_id']
            if lid not in counts:
                counts[lid] = {'reads': 0, 'completed': 0, 'total_seconds': 0}
            counts[lid]['reads'] += 1
            if r.get('completed'):
                counts[lid]['completed'] += 1
            counts[lid]['total_seconds'] += r.get('seconds_spent', 0)
        sorted_rows = sorted(counts.items(), key=lambda x: -x[1]['reads'])[:20]
        lessons = sb.table('education_lessons').select('id, topic_title').execute()
        name_map = {l['id']: l['topic_title'] for l in lessons.data}
        out = []
        for lid, agg in sorted_rows:
            out.append({
                'lesson_id': lid,
                'title': name_map.get(lid, 'Unknown'),
                'reads': agg['reads'],
                'completed': agg['completed'],
                'avg_seconds': int(agg['total_seconds'] / agg['reads']) if agg['reads'] > 0 else 0,
            })
        return {'ok': True, 'top': out}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# TRACK A READ (any user)
# ============================================
class ReadTrackRequest(BaseModel):
    user_id: str = ''
    lesson_id: int
    seconds_spent: int = 0
    completed: bool = False


@app.post('/api/lesson/read')
def track_read(req: ReadTrackRequest):
    try:
        sb.table('lesson_reads').insert({
            'user_id': req.user_id,
            'lesson_id': req.lesson_id,
            'seconds_spent': req.seconds_spent,
            'completed': req.completed,
        }).execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}



# ============================================
# SCHOOL: CLASSES
# ============================================
class ClassCreateRequest(BaseModel):
    school_license_id: int
    admin_id: str
    name: str
    level: str = ''
    teacher_id: str = ''


@app.post('/api/school/class/create')
def school_class_create(req: ClassCreateRequest):
    import secrets
    try:
        code = secrets.token_hex(3).upper()
        r = sb.table('classes').insert({
            'school_license_id': req.school_license_id,
            'name': req.name,
            'level': req.level,
            'teacher_id': req.teacher_id or req.admin_id,
            'join_code': code,
        }).execute()
        return {'ok': True, 'class': r.data[0] if r.data else None}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/school/classes')
def school_list_classes(school_license_id: int = 0, teacher_id: str = ''):
    try:
        q = sb.table('classes').select('*').eq('active', True)
        if school_license_id > 0:
            q = q.eq('school_license_id', school_license_id)
        if teacher_id:
            q = q.eq('teacher_id', teacher_id)
        r = q.order('created_at', desc=True).execute()
        return {'ok': True, 'classes': r.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


class ClassJoinRequest(BaseModel):
    join_code: str
    user_id: str
    full_name: str = ''


@app.post('/api/school/class/join')
def school_class_join(req: ClassJoinRequest):
    try:
        cls = sb.table('classes').select('*').eq('join_code', req.join_code.upper()).eq('active', True).execute()
        if not cls.data:
            return {'ok': False, 'error': 'Invalid code'}
        class_row = cls.data[0]
        existing = sb.table('class_members').select('id').eq('class_id', class_row['id']).eq('user_id', req.user_id).execute()
        if not existing.data:
            sb.table('class_members').insert({
                'class_id': class_row['id'],
                'user_id': req.user_id,
                'full_name': req.full_name,
                'role': 'student',
            }).execute()
        return {'ok': True, 'class': {'id': class_row['id'], 'name': class_row['name'], 'level': class_row['level']}}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/school/class/{class_id}/members')
def school_class_members(class_id: int):
    try:
        r = sb.table('class_members').select('*').eq('class_id', class_id).order('joined_at').execute()
        return {'ok': True, 'members': r.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# SCHOOL: ASSIGNMENTS
# ============================================
class AssignmentCreateRequest(BaseModel):
    class_id: int
    teacher_id: str
    title: str
    description: str = ''
    subject: str = 'Chemistry'
    topic_number: int = 0
    due_at: str = ''
    max_score: int = 100


@app.post('/api/school/assignment/create')
def school_assignment_create(req: AssignmentCreateRequest):
    try:
        payload = {
            'class_id': req.class_id,
            'teacher_id': req.teacher_id,
            'title': req.title,
            'description': req.description,
            'subject': req.subject,
            'topic_number': req.topic_number,
            'max_score': req.max_score,
        }
        if req.due_at:
            payload['due_at'] = req.due_at
        r = sb.table('assignments').insert(payload).execute()
        return {'ok': True, 'assignment': r.data[0] if r.data else None}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/school/assignments/{class_id}')
def school_assignment_list(class_id: int):
    try:
        r = sb.table('assignments').select('*').eq('class_id', class_id).order('created_at', desc=True).execute()
        return {'ok': True, 'assignments': r.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/school/assignment/{assignment_id}')
def school_assignment_detail(assignment_id: int):
    try:
        a = sb.table('assignments').select('*').eq('id', assignment_id).execute()
        subs = sb.table('assignment_submissions').select('*').eq('assignment_id', assignment_id).execute()
        return {'ok': True, 'assignment': a.data[0] if a.data else None, 'submissions': subs.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


class SubmitRequest(BaseModel):
    assignment_id: int
    student_id: str
    text: str


@app.post('/api/school/assignment/submit')
async def school_assignment_submit(req: SubmitRequest):
    if not DEEPSEEK_KEY:
        return {'ok': False, 'error': 'AI not configured'}
    try:
        a = sb.table('assignments').select('*').eq('id', req.assignment_id).execute()
        if not a.data:
            return {'ok': False, 'error': 'Assignment not found'}
        subject = a.data[0].get('subject', 'Chemistry')
        max_score = a.data[0].get('max_score', 100)

        prompt = ('Grade this ' + subject + ' student answer out of ' + str(max_score) + '. ' +
            'Return ONLY JSON: {"score": number, "feedback": "2 sentences"}. ' +
            'Be fair and encouraging.\n\nANSWER:\n' + req.text)

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={'Authorization': 'Bearer ' + DEEPSEEK_KEY},
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': 'You are a Nigerian teacher grading homework. Return JSON only.'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'temperature': 0.3,
                },
            )
            data = r.json()
        raw = data['choices'][0]['message']['content'].strip()
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        import json as _j
        g = _j.loads(raw)

        sb.table('assignment_submissions').upsert({
            'assignment_id': req.assignment_id,
            'student_id': req.student_id,
            'text': req.text,
            'score': int(g.get('score', 0)),
            'feedback': g.get('feedback', ''),
            'status': 'graded',
        }, on_conflict='assignment_id,student_id').execute()

        return {'ok': True, 'score': int(g.get('score', 0)), 'feedback': g.get('feedback', '')}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}


class ManualGradeRequest(BaseModel):
    assignment_id: int
    student_id: str
    score: int
    feedback: str = ''


@app.post('/api/school/assignment/manual-grade')
def school_manual_grade(req: ManualGradeRequest):
    try:
        sb.table('assignment_submissions').upsert({
            'assignment_id': req.assignment_id,
            'student_id': req.student_id,
            'score': req.score,
            'feedback': req.feedback,
            'status': 'graded',
        }, on_conflict='assignment_id,student_id').execute()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# SCHOOL: CLASS ANALYTICS
# ============================================
@app.get('/api/school/analytics/{class_id}')
def school_class_analytics(class_id: int):
    try:
        members = sb.table('class_members').select('*').eq('class_id', class_id).execute()
        asgs = sb.table('assignments').select('id').eq('class_id', class_id).execute()
        asg_ids = [a['id'] for a in asgs.data]
        subs = []
        if asg_ids:
            subs = sb.table('assignment_submissions').select('*').in_('assignment_id', asg_ids).execute().data

        student_stats = {}
        for m in members.data:
            student_stats[m['user_id']] = {
                'user_id': m['user_id'],
                'name': m.get('full_name') or m['user_id'][:8],
                'submitted': 0,
                'total_score': 0,
                'graded': 0,
            }

        for s in subs:
            sid = s['student_id']
            if sid in student_stats:
                student_stats[sid]['submitted'] += 1
                if s.get('score') is not None:
                    student_stats[sid]['total_score'] += s['score']
                    student_stats[sid]['graded'] += 1

        rows = []
        for k, v in student_stats.items():
            avg = round(v['total_score'] / v['graded'], 1) if v['graded'] > 0 else 0
            rows.append({
                'user_id': v['user_id'],
                'name': v['name'],
                'submitted': v['submitted'],
                'graded': v['graded'],
                'avg_score': avg,
            })
        rows.sort(key=lambda x: -x['avg_score'])

        class_avg = round(sum(r['avg_score'] for r in rows) / len(rows), 1) if rows else 0
        return {
            'ok': True,
            'total_students': len(members.data),
            'total_assignments': len(asg_ids),
            'class_average': class_avg,
            'students': rows,
        }
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# SCHOOL: REPORT CARD
# ============================================
@app.get('/api/school/report/{class_id}/{student_id}')
def school_report_card(class_id: int, student_id: str):
    try:
        m = sb.table('class_members').select('*').eq('class_id', class_id).eq('user_id', student_id).execute()
        if not m.data:
            return {'ok': False, 'error': 'Student not in class'}
        name = m.data[0].get('full_name') or student_id[:8]

        asgs = sb.table('assignments').select('*').eq('class_id', class_id).execute()
        results = []
        for a in asgs.data:
            sub = sb.table('assignment_submissions').select('*').eq('assignment_id', a['id']).eq('student_id', student_id).execute()
            results.append({
                'assignment': a['title'],
                'subject': a.get('subject', ''),
                'max_score': a.get('max_score', 100),
                'score': sub.data[0].get('score') if sub.data else None,
                'feedback': sub.data[0].get('feedback') if sub.data else '',
            })

        grades = [r['score'] for r in results if r['score'] is not None]
        avg = round(sum(grades) / len(grades), 1) if grades else 0
        grade = 'A' if avg >= 75 else 'B' if avg >= 65 else 'C' if avg >= 55 else 'D' if avg >= 45 else 'F'

        return {
            'ok': True,
            'student': name,
            'class_id': class_id,
            'average': avg,
            'grade': grade,
            'assignments': results,
        }
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


# ============================================
# SCHOOL: EXAM SCHEDULE
# ============================================
class ExamScheduleRequest(BaseModel):
    school_license_id: int
    class_id: int
    created_by: str
    title: str
    subject: str = 'Chemistry'
    exam_date: str
    duration_minutes: int = 60
    total_questions: int = 40


@app.post('/api/school/exam/schedule')
def school_exam_schedule(req: ExamScheduleRequest):
    try:
        r = sb.table('school_exams').insert({
            'school_license_id': req.school_license_id,
            'class_id': req.class_id,
            'title': req.title,
            'subject': req.subject,
            'exam_date': req.exam_date,
            'duration_minutes': req.duration_minutes,
            'total_questions': req.total_questions,
            'created_by': req.created_by,
        }).execute()
        return {'ok': True, 'exam': r.data[0] if r.data else None}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


@app.get('/api/school/exams/{class_id}')
def school_list_exams(class_id: int):
    try:
        r = sb.table('school_exams').select('*').eq('class_id', class_id).order('exam_date').execute()
        return {'ok': True, 'exams': r.data}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}

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
