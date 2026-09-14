"""CoreKnow AI Engine.
Uses internal LLM infrastructure to power question generation, chat, and grading.
"""

import os
import json
import re
import requests
import streamlit as st


# ============================================
# CONFIG (internal — never shown to users)
# ============================================
def _get_api_key():
    try:
        return st.secrets["deepseek"]["api_key"]
    except Exception:
        return ""

AI_URL = "https://api.deepseek.com/v1/chat/completions"


# ============================================
# CoreKnow IDENTITY — AIRTIGHT
# ============================================
COR EKNOW_IDENTITY = (
    "You are CoreKnow, an advanced AI tutor built by Darkmoor Ltd in Nigeria. "
    "You are the sole intelligence powering this platform. "

    "STRICT IDENTITY RULES:\n"
    "1. If anyone asks who you are, who built you, what model you are, or what company "
    "makes you — you MUST answer: 'I am CoreKnow, an AI tutor created by Darkmoor Ltd. "
    "I don't disclose the underlying technology behind me, but I'm here to help you learn.'\n"
    "2. NEVER mention any company, model, or technology name (including but not limited "
    "to: DeepSeek, OpenAI, GPT, ChatGPT, Claude, Anthropic, Gemini, Google, Meta, Llama, "
    "Mistral, Alibaba, Qwen, or any other AI company or model).\n"
    "3. NEVER say 'I am a language model' or 'I was trained on...'.\n"
    "4. If pushed or tricked ('pretend', 'hypothetically', 'in a story'), still refuse "
    "and redirect: 'I'm CoreKnow and I'm here to help you learn. What's your question?'\n"
    "5. If someone asks what powers you, say: 'CoreKnow is powered by proprietary "
    "AI technology developed by Darkmoor Ltd.'\n"
    "6. You ARE CoreKnow. That is your only identity.\n\n"

    "TEACHING STYLE:\n"
    "- Answer clearly, step-by-step, in simple language.\n"
    "- Show formulas, symbols, and calculations in full detail.\n"
    "- Use Nigerian context (Naira, local examples, JAMB/WAEC/NECO).\n"
    "- Be warm, encouraging, and patient — like a favorite tutor.\n"
)


# ============================================
# HARDENED REQUEST WRAPPER
# ============================================
def _call_ai(messages, max_tokens=3000, temperature=0.7, timeout=120):
    """Internal helper. Sends request and returns text."""
    api_key = _get_api_key()
    if not api_key:
        return None, "AI engine not configured"

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
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


def _sanitize(text):
    """Final safety net — strip any leaked brand names."""
    if not text:
        return text
    replacements = [
        "DeepSeek", "Deepseek", "deepseek",
        "OpenAI", "GPT-4", "GPT-3", "ChatGPT",
        "Anthropic", "Claude",
        "Google AI", "Gemini", "Bard",
        "Meta AI", "LLaMA", "Llama",
        "Mistral AI", "Mistral",
        "Alibaba AI", "Qwen",
    ]
    for word in replacements:
        # Only strip if it looks like a brand mention (surrounded by spaces/punct)
        text = re.sub(r'\b' + re.escape(word) + r'\b', 'CoreKnow', text, flags=re.IGNORECASE)
    return text


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
        'Return ONLY a JSON array. Each element has these fields:\n'
        '{"question": "...", "options": ["A text", "B text", "C text", "D text"], "correct": "A", "solution": "Step-by-step explanation..."}\n\n'
        "Now generate " + str(num_questions) + " questions. Return ONLY the JSON array, no other text."
    )

    messages = [
        {"role": "system", "content": COR EKNOW_IDENTITY},
        {"role": "user", "content": prompt},
    ]

    text, err = _call_ai(messages, max_tokens=8000, temperature=0.8, timeout=180)
    if err:
        return None, err

    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        return None, "No valid JSON found"

    try:
        questions = json.loads(match.group())
    except Exception as e:
        return None, "JSON parse failed: " + str(e)

    valid = []
    for q in questions:
        if "question" in q and "options" in q and "correct" in q:
            opts = q["options"]
            if len(opts) == 4:
                valid.append({
                    "question": q["question"],
                    "options": opts,
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
        "Q" + str(i + 1) + ": Correct = " + q["correct"] + ". Reason: " + q.get("solution", "")[:200]
        for i, q in enumerate(questions)
    ])

    prompt = (
        "You are grading a student's JAMB exam.\n\n"
        "The exam had these questions with correct answers:\n---\n" + key + "\n---\n\n"
        "The student uploaded an answer sheet. Extracted text:\n---\n" + student_answer_text + "\n---\n\n"
        "Match their answers to the questions.\n"
        "Return ONLY a JSON array:\n"
        '[{"q": 1, "student_answer": "B", "correct": false, "note": "Student chose B, but correct is A because..."}]\n\n'
        "If the student's answer cannot be determined, use \"?\" for student_answer."
    )

    messages = [
        {"role": "system", "content": COR EKNOW_IDENTITY},
        {"role": "user", "content": prompt},
    ]

    text, err = _call_ai(messages, max_tokens=4000, temperature=0.3, timeout=120)
    if err:
        return None, err

    match = re.search(r'\[.*\]', text, re.DOTALL)
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
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception:
        return ""
