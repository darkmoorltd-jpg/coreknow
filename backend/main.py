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
