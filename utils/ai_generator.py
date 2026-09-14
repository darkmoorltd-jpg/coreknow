
import json
import re
import requests
import streamlit as st

try:
    DEEPSEEK_API_KEY = st.secrets["deepseek"]["api_key"]
except Exception:
    DEEPSEEK_API_KEY = ""

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are CoreKnow, an expert JAMB and WAEC Chemistry tutor from Nigeria. "
    "Always answer clearly, step by step, using simple language. "
    "Show formulas, symbols, and calculations in full detail. "
    "Never mention DeepSeek or any other AI company. You ARE CoreKnow."
)


def generate_hard_mcqs(topic, lesson_text, num_questions=50, difficulty="hard"):
    if not DEEPSEEK_API_KEY:
        return None, "DeepSeek API key not configured"

    lesson_excerpt = (lesson_text or "")[:6000]

    prompt = f"""Generate {num_questions} JAMB-style {difficulty} multiple-choice questions on the topic: {topic}.

Base them on this lesson content:
---
{lesson_excerpt}
---

REQUIREMENTS:
- Questions must be HARD and DIFFICULT (JAMB 300+ level).
- Test calculation, application, and deep understanding.
- Each question has exactly 4 options: A, B, C, D.
- Provide a DETAILED step-by-step solution.

Return ONLY a JSON array. Each element has fields:
"question", "options" (array of 4 strings), "correct" (A/B/C/D), "solution".

Example:
[{{"question": "Calculate pH of 0.001 M HCl.", "options": ["1", "2", "3", "4"], "correct": "C", "solution": "pH = -log(0.001) = 3."}}]

Now generate {num_questions} questions. Return ONLY the JSON array, no other text."""

    headers = {"Authorization": "Bearer " + DEEPSEEK_API_KEY, "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 8000,
        "temperature": 0.8
    }

    try:
        r = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=180)
        if r.status_code != 200:
            return None, "API error: " + str(r.status_code)
        content = r.json()["choices"][0]["message"]["content"]
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            return None, "No valid JSON found"
        questions = json.loads(match.group())
        valid = []
        for q in questions:
            if "question" in q and "options" in q and "correct" in q:
                if len(q["options"]) == 4:
                    valid.append({
                        "question": q["question"],
                        "options": q["options"],
                        "correct": str(q.get("correct", "A")).upper(),
                        "solution": q.get("solution", "See lesson for details.")
                    })
        return valid, None
    except Exception as e:
        return None, str(e)


def chat_with_coreknow(question, image_text=None, history=None):
    if not DEEPSEEK_API_KEY:
        return None, "DeepSeek API key not configured"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for h in history[-10:]:
            messages.append({"role": "user", "content": h["q"]})
            messages.append({"role": "assistant", "content": h["a"]})

    full_q = question
    if image_text:
        full_q = "[Uploaded image text:]\n" + image_text + "\n\n[User question:] " + (question or "")
    messages.append({"role": "user", "content": full_q})

    headers = {"Authorization": "Bearer " + DEEPSEEK_API_KEY, "Content-Type": "application/json"}
    payload = {"model": "deepseek-chat", "messages": messages, "max_tokens": 3000, "temperature": 0.7}

    try:
        r = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if r.status_code != 200:
            return None, "API error: " + str(r.status_code)
        return r.json()["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, str(e)


def generate_exam(topic, lesson_text, num_questions=40):
    return generate_hard_mcqs(topic, lesson_text, num_questions=num_questions, difficulty="hard")


def grade_uploaded_answers(student_answer_text, questions):
    if not DEEPSEEK_API_KEY:
        return None, "DeepSeek API key not configured"

    key_parts = []
    for i, q in enumerate(questions):
        key_parts.append("Q" + str(i+1) + ": correct=" + q["correct"] + ". Reason: " + str(q.get("solution", ""))[:200])
    key = "\n".join(key_parts)

    prompt = f"""You are grading a JAMB Chemistry exam.

Answer key:
---
{key}
---

Student answer sheet (extracted text):
---
{student_answer_text}
---

Return ONLY a JSON array, one object per question:
[{{"q": 1, "student_answer": "A", "correct": true, "note": "explanation"}}]"""

    headers = {"Authorization": "Bearer " + DEEPSEEK_API_KEY, "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.3
    }

    try:
        r = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=120)
        if r.status_code != 200:
            return None, "API error: " + str(r.status_code)
        content = r.json()["choices"][0]["message"]["content"]
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            return None, "Could not parse grading response"
        return json.loads(match.group()), None
    except Exception as e:
        return None, str(e)


def extract_text_from_image(image_bytes):
    try:
        from PIL import Image
        import io
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img).strip()
    except Exception:
        return ""
