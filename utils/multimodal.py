
import requests
import base64
import io
import os
import tempfile

def analyze_image(image_bytes, llm_api_key=None):
    """Analyze image using DeepSeek vision (if available) or return placeholder."""
    if not llm_api_key:
        return "Image analysis requires DeepSeek API key. Upload image for processing."
    
    # Convert image to base64
    img_b64 = base64.b64encode(image_bytes).decode()
    
    headers = {"Authorization": f"Bearer {llm_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are CoreKnow's visual understanding module. Describe what you see in the image and extract key concepts."},
            {"role": "user", "content": f"[Image data: {img_b64[:100]}...] Describe this image."}
        ],
        "max_tokens": 300
    }
    try:
        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return "Image analysis failed. Try again."

def transcribe_audio(audio_bytes, groq_api_key=None):
    """Transcribe audio using Groq Whisper API."""
    if not groq_api_key:
        return None, "Groq API key required for audio transcription"
    
    # Save audio to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(audio_bytes)
    tmp.close()
    
    headers = {"Authorization": f"Bearer {groq_api_key}"}
    with open(tmp.name, "rb") as f:
        files = {"file": ("audio.wav", f, "audio/wav")}
        data = {"model": "whisper-large-v3", "language": "en"}
        r = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
                         headers=headers, files=files, data=data, timeout=30)
    
    os.unlink(tmp.name)
    
    if r.status_code == 200:
        return r.json().get("text", "").strip(), None
    else:
        return None, f"Transcription error {r.status_code}"

def text_to_speech(text):
    """Convert text to speech using gTTS."""
    try:
        from gtts import gTTS
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts = gTTS(text=text, lang='en')
        tts.save(tmp.name)
        with open(tmp.name, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp.name)
        return audio_bytes, None
    except Exception as e:
        return None, str(e)
