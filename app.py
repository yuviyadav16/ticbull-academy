import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import urllib.parse

app = Flask(__name__)
CORS(app)

# ========================================================
# 🚀 FULL MASTER BACKEND (All Systems Included)
# ========================================================
VALID_GEMINI_KEYS = [k for k in [os.getenv("GEMINI_API_KEY", "")] if k.strip()]
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def db_url(path):
    url = f"{FIREBASE_URL}/{path}"
    if FIREBASE_SECRET: url += f"?auth={FIREBASE_SECRET}"
    return url

def sanitize_email(email): return email.replace('.', '_').replace('@', '_at_')

# --- AUTH SYSTEM (Required) ---
@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'], msg['From'], msg['To'] = "TicBull Verification", f"TicBull <{SMTP_EMAIL}>", email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.sendmail(SMTP_EMAIL, email, msg.as_string())
        return jsonify({"success": True})
    except: return jsonify({"success": False}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email, user_otp = data.get('email', '').lower(), data.get('otp', '')
    if email in otp_store and otp_store[email] == user_otp:
        token = str(random.randint(10000000, 99999999))
        return jsonify({"success": True, "token": token})
    return jsonify({"success": False}), 400

# --- SYNC SYSTEM (Required for Cloud History) ---
@app.route('/api/sync-batch', methods=['POST'])
def sync_batch():
    data = request.get_json() or {}
    email, batch = data.get('email', '').lower(), data.get('batch')
    safe_email = sanitize_email(email)
    user_url = db_url(f"users/{safe_email}.json")
    user_db = requests.get(user_url).json() or {}
    enrolled = user_db.get('enrolled_batches', [])
    enrolled.append(batch)
    requests.patch(user_url, json={"enrolled_batches": enrolled})
    return jsonify({"success": True})

@app.route('/api/sync-session', methods=['POST'])
def sync_session():
    data = request.get_json() or {}
    if data.get('email'):
        requests.put(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json"), 
                     json={"title": data.get('title'), "html": data.get('html')})
    return jsonify({"success": True})

@app.route('/api/get-session-html', methods=['POST'])
def get_session_html():
    data = request.get_json() or {}
    res = requests.get(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json")).json() or {}
    return jsonify({"success": True, "html": res.get("html", "")})

@app.route('/api/delete-session', methods=['POST'])
def delete_session():
    data = request.get_json() or {}
    requests.delete(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json"))
    return jsonify({"success": True})

# --- AI CHAT ROUTER (Includes Image Generation + Groq) ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt, attachments = data.get('prompt', '').strip(), data.get('images', [])
    teacher_name, teacher_gender = data.get('teacher_name', 'AI Teacher'), data.get('teacher_gender', 'Male')
    
    # 1. Image Generate Shortcut
    if "image" in prompt.lower() and len(prompt) < 30:
        topic = prompt.replace("image", "").strip()
        img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(topic)}?nologo=true"
        return jsonify({"success": True, "reply": f"Ye rahi aapki image:\n\n![Image]({img_url})"})

    # 2. Logic to choose AI
    is_simple = len(prompt) < 100 and not attachments
    final_reply = None

    # Try Groq for simple text
    if is_simple and GROQ_API_KEY:
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=5)
            if res.status_code == 200: final_reply = res.json()['choices'][0]['message']['content']
        except: pass

    # Fallback to Gemini
    if not final_reply and VALID_GEMINI_KEYS:
        parts = [{"text": f"You are {teacher_name}. {prompt}"}]
        for f in attachments:
            parts.append({"inline_data": {"mime_type": f.split(';')[0].split(':')[1], "data": f.split(',')[1]}})
        res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={VALID_GEMINI_KEYS[0]}", 
                           json={"contents": [{"parts": parts}]}, headers={"Content-Type": "application/json"})
        final_reply = res.json()['candidates'][0]['content']['parts'][0]['text']

    return jsonify({"success": True, "reply": final_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
