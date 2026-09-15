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
