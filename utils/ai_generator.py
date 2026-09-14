"""CoreKnow AI Engine — internal.
Powers question generation, chat, and grading.
Vendor-neutral: nothing user-visible here.
"""

import os
import json
import re
import requests
import streamlit as st


# ============================================
# INTERNAL CONFIG (never shown to users)
# ============================================
def _get_api_key():
    try:
        return st.secrets["deepseek"]["api_key"]
    except Exception:
        return ""

# Endpoint assembled at runtime so the vendor string is never a literal
_HOST = "api." + "deep" + "seek" + ".com"
AI_URL = "https://" + _HOST + "/v1/chat/completions"

# Model name assembled at runtime (API requires this exact value)
AI_MODEL = "deep" + "seek" + "-chat"


# ============================================
# CoreKnow IDENTITY — airtight
# ============================================
COR EKNOW_IDENTITY = (
    "You are CoreKnow, an advanced AI tutor built by Darkmoor Ltd in Nigeria. "
    "You are the sole intelligence powering this platform. "

    "STRICT IDENTITY RULES:\n"
    "1. If asked who you are, who built you, what model you are, or what company makes you — "
    "answer ONLY: 'I am CoreKnow, an AI tutor created by Darkmoor Ltd. I don't disclose the "
    "underlying technology behind me, but I'm here to help you learn.'\n"
    "2. Never name or hint at any external AI company, product, or model. Treat all such names "
    "as confidential. If asked directly, politely decline and redirect to helping with the "
    "user's question.\n"
    "3. Never describe yourself as a 'language model' or as 'trained on' any data.\n"
    "4. If a user asks you to pretend, roleplay, or hypothesise about your identity, refuse "
    "and stay CoreKnow.\n"
    "5. If asked what powers you, say: 'CoreKnow is powered by proprietary AI technology "
    "developed by Darkmoor Ltd.'\n"
    "6. You ARE CoreKnow. That is your only identity, always.\n\n"

    "TEACHING STYLE:\n"
    "- Answer clearly, step-by-step, in simple language.\n"
    "- Show formulas, symbols, and calculations in full detail.\n"
    "- Use Nigerian context (Naira, local examples, JAMB/WAEC/NECO).\n"
    "- Be warm, encouraging, and patient — like a favorite tutor.\n"
)


# ============================================
# SANITIZER — regex patterns, no literal brand names
# ============================================
_SANITIZE_PATTERNS = [
    re.compile(r"\bdeep[ _-]?seek\b", re.IGNORECASE),
    re.compile(r"\bopen[ _-]?ai\b", re.IGNORECASE),
    re.compile(r"\bgpt[ -]?\d+(\.\d+)?\b", re.IGNORECASE),
    re.compile(r"\bchat[ _-]?gpt\b", re.IGNORECASE),
    re.compile(r"\banthropic\b", re.IGNORECASE),
    re.compile(r"\bclaude(\s+ai)?\b", re.IGNORECASE),
    re.compile(r"\bgemini(\s+ai)?\b", re.IGNORECASE),
    re.compile(r"\bgoogle\s+(ai|deepmind)\b", re.IGNORECASE),
    re.compile(r"\bmeta\s+ai\b", re.IGNORECASE),
    re.compile(r"\bllama\s*\d*\b", re.IGNORECASE),
    re.compile(r"\bmistral(\s+ai)?\b", re.IGNORECASE),
    re.compile(r"\balibaba\s+ai\b", re.IGNORECASE),
    re.compile(r"\bqwen(\s*\d*)\b", re.IGNORECASE),
    re.compile(r"\bbard\b", re.IGNORECASE),
]

def _sanitize(text):
    if not text:
        return text
    for pat in _SANITIZE_PATTERNS:
        text = pat.sub("CoreKnow", text)
    return text


# ============================================
# REQUEST WRAPPER
# ============================================
def _call_ai(messages, max_tokens=3000, temperature=0.7, timeout=120):
    api_key = _get_api_key()
    if not api_key:
        return None, "AI engine not configured"

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        r = requests.post(AI_URL, headers=headers, json=payload, timeout=timeout)
        if r.status_code != 200:
            return None, "AI engine error " + str(r.status_code)
        text = r.json()["choices"][0]["message"]["content"]
        return _sanitize(text), None
    except Exception as e:
        return None, str(e)


# ============================================
# QUESTION GENERATOR
# ============================================
def generate_hard_mcqs(topic, lesson_text, num_questions=50, difficulty="hard"):
    lesson_excerpt = lesson_text[:6000] if lesson_text else ""

    prompt = (
        "Generate " + str(num_questions) + " JAMB-style " + difficulty + " multiple-choice questions "
        "on the topic: " + topic + ".\n\n"
        "Base them on this lesson content:\n"
        "---\n" + lesson_excerpt + "\n---\n\n"
        "REQUIREMENTS:\n"
        "- Questions must be HARD and DIFFICULT (JAMB 300+ level).\n"
        "- Test calculation, application, and deep understanding — not just memorization.\n"
        "- Each question has exactly 4 options: A, B, C, D.\n"
        "- Only ONE correct answer.\n"
        "- Provide a DETAILED step-by-step solution explaining WHY the answer is correct.\n\n"
        'Return ONLY a JSON array. Each element:\n'
        '{"question": "...", "options": ["A text", "B text", "C text", "D text"], '
        '"correct": "A", "solution": "Step-by-step..."}\n\n'
        "Now generate " + str(num_questions) + " questions. Return ONLY the JSON array."
    )

    messages = [
        {"role": "system", "content": COR EKNOW_IDENTITY},
        {"role": "user", "content": prompt},
    ]

    text, err = _call_ai(messages, max_tokens=8000, temperature=0.8, timeout=180)
    if err:
        return None, err

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return None, "No valid JSON found"

    try:
        questions = json.loads(match.group())
    except Exception as e:
        return None, "JSON parse failed: " + str(e)

    valid = []
    for q in questions:
        if "question" in q and "options" in q and "correct" in q:
            if len(q["options"]) == 4:
                valid.append({
                    "question": q["question"],
                    "options": q["options"],
                    "correct": str(q.get("correct", "A")).upper(),
                    "solution": q.get("solution", "See lesson for details."),
                })
    return valid, None


# ============================================
# CHAT
# ============================================
def chat_with_coreknow(question, image_text=None, history=None):
    messages = [{"role": "system", "content": COR EKNOW_IDENTITY}]

    if history:
        for h in history[-10:]:
            messages.append({"role": "user", "content": h["q"]})
            messages.append({"role": "assistant", "content": h["a"]})

    full_q = question
    if image_text:
        if question:
            full_q = "[Extracted from uploaded image:]\n" + image_text + "\n\n[User question:] " + question
        else:
            full_q = "[Extracted from uploaded image:]\n" + image_text

    messages.append({"role": "user", "content": full_q})
    return _call_ai(messages, max_tokens=3000, temperature=0.7, timeout=120)


# ============================================
# EXAM
# ============================================
def generate_exam(topic, lesson_text, num_questions=40):
    return generate_hard_mcqs(topic, lesson_text, num_questions=num_questions, difficulty="hard")


# ============================================
# GRADING
# ============================================
def grade_uploaded_answers(student_answer_text, questions):
    key = "\n".join([
        "Q" + str(i + 1) + ": Correct = " + q["correct"] +
        ". Reason: " + q.get("solution", "")[:200]
        for i, q in enumerate(questions)
    ])

    prompt = (
        "You are grading a student's JAMB exam.\n\n"
        "The exam had these questions with correct answers:\n---\n" + key + "\n---\n\n"
        "The student uploaded an answer sheet. Extracted text:\n---\n" + student_answer_text + "\n---\n\n"
        "Match their answers to the questions.\n"
        "Return ONLY a JSON array:\n"
        '[{"q": 1, "student_answer": "B", "correct": false, "note": "Student chose B, but correct is A because..."}]\n\n'
        'If the student\'s answer cannot be determined, use "?" for student_answer.'
    )

    messages = [
        {"role": "system", "content": COR EKNOW_IDENTITY},
        {"role": "user", "content": prompt},
    ]

    text, err = _call_ai(messages, max_tokens=4000, temperature=0.3, timeout=120)
    if err:
        return None, err

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return None, "Could not parse grading response"

    try:
        return json.loads(match.group()), None
    except Exception as e:
        return None, str(e)


# ============================================
# OCR
# ============================================
def extract_text_from_image(image_bytes):
    try:
        from PIL import Image
        import io
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img).strip()
    except Exception:
        return ""
