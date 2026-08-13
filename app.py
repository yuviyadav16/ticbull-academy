import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ========================================================
# 🚀 SMART MULTI-LLM ROUTING SYSTEM
# ========================================================
# 1. Gemini Keys (For Education & Vision)
GEMINI_API_KEYS = [os.getenv("GEMINI_API_KEY", ""), "KEY2", "KEY3"]
VALID_GEMINI_KEYS = [k for k in GEMINI_API_KEYS if k.strip() and "KEY" not in k]

# 2. Meta/DeepSeek Keys (Using Groq or OpenRouter Free endpoints for Chat/Motivation)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") # Meta Llama / DeepSeek handler

# Environment Variables
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET", "") 
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "rakeshbhai@2308bull") 

otp_store = {}

def db_url(path):
    url = f"{FIREBASE_URL}/{path}"
    if FIREBASE_SECRET: url += f"?auth={FIREBASE_SECRET}"
    return url

def sanitize_email(email): return email.replace('.', '_').replace('@', '_at_')

def send_otp_email(to_email, otp, is_delete=False):
    if not SMTP_PASSWORD or not SMTP_EMAIL: return False
    subject = "⚠️ URGENT: Account Deletion OTP" if is_delete else "TicBull Academy - Secure OTP"
    body = f"Your OTP is: {otp}\n\nTicBull Support"
    msg = MIMEText(body)
    msg['Subject'], msg['From'], msg['To'] = subject, f"TicBull Academy <{SMTP_EMAIL}>", to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except: return False

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    email, password, auth_mode = data.get('email', '').strip().lower(), data.get('password', ''), data.get('auth_mode', 'login')
    if not email: return jsonify({"success": False, "message": "Email required!"}), 400
    
    if FIREBASE_URL:
        safe_email = sanitize_email(email)
        user_check = requests.get(db_url(f"users/{safe_email}.json")).json()
        if auth_mode == 'signup' and user_check: return jsonify({"success": False, "message": "Account exists!"}), 400
        elif auth_mode == 'login':
            if not user_check: return jsonify({"success": False, "message": "Account not found!"}), 400
            if user_check.get('password') != password: return jsonify({"success": False, "message": "Incorrect Password!"}), 400
            
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    if send_otp_email(email, otp): return jsonify({"success": True})
    return jsonify({"success": False, "message": "Error."}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email, user_otp, password, auth_mode = data.get('email', '').lower(), data.get('otp', ''), data.get('password', ''), data.get('auth_mode', 'login')
    
    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        token = str(random.randint(10000000, 99999999))
        user_data = {}
        if FIREBASE_URL:
            safe_email = sanitize_email(email)
            requests.put(db_url(f"sessions/{safe_email}.json"), json={"token": token})
            if auth_mode == 'signup': requests.put(db_url(f"users/{safe_email}.json"), json={"email": email, "password": password, "join_date": str(datetime.now().date())})
            elif auth_mode == 'forgot': requests.patch(db_url(f"users/{safe_email}.json"), json={"password": password})
            
            db_user = requests.get(db_url(f"users/{safe_email}.json")).json() or {}
            user_data = {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", ""), "enrolled_batches": db_user.get("enrolled_batches", [])}
        return jsonify({"success": True, "token": token, "user": user_data})
    return jsonify({"success": False, "message": "Invalid OTP!"}), 400

@app.route('/api/sync-batch', methods=['POST'])
def sync_batch():
    data = request.get_json() or {}
    email, batch_data = data.get('email', '').strip().lower(), data.get('batch')
    if not email or not FIREBASE_URL: return jsonify({"success": False}), 400
    safe_email = sanitize_email(email)
    user_url = db_url(f"users/{safe_email}.json")
    try:
        user_db = requests.get(user_url).json() or {}
        enrolled = user_db.get('enrolled_batches', [])
        exists = False
        for b in enrolled:
            if b.get('title') == batch_data.get('title'):
                exists = True; b['subjects'] = batch_data.get('subjects', []); break
        if not exists: enrolled.append(batch_data)
        requests.patch(user_url, json={"enrolled_batches": enrolled})
        return jsonify({"success": True})
    except: return jsonify({"success": False}), 500

@app.route('/api/check-session', methods=['POST'])
def check_session():
    data = request.get_json() or {}
    email, token = data.get('email', '').lower(), data.get('token', '')
    if not FIREBASE_URL: return jsonify({"success": True, "active": True})
    res = requests.get(db_url(f"sessions/{sanitize_email(email)}.json")).json() or {}
    if res.get("token") == token:
        db_user = requests.get(db_url(f"users/{sanitize_email(email)}.json")).json() or {}
        return jsonify({"success": True, "active": True, "user": {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", ""), "enrolled_batches": db_user.get("enrolled_batches", [])}})
    return jsonify({"success": True, "active": False})

@app.route('/api/sync-session', methods=['POST'])
def sync_session():
    data = request.get_json() or {}
    if data.get('email') and FIREBASE_URL: requests.put(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json"), json={"title": data.get('title'), "html": data.get('html')})
    return jsonify({"success": True})

@app.route('/api/delete-session', methods=['POST'])
def delete_session():
    data = request.get_json() or {}
    if data.get('email') and FIREBASE_URL: requests.delete(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json"))
    return jsonify({"success": True})

# 🧠 THE SMART ROUTER (META / DEEPSEEK / GEMINI)
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    images = data.get('images', []) 
    board, cls, stream, student_name, email = data.get('board', ''), data.get('class', ''), data.get('stream', ''), data.get('student_name', 'Student'), data.get('email', '').lower()
    
    if not prompt and not images: return jsonify({"success": False}), 400

    # 1. Keyword Check for "Timepass/Motivation" routing
    timepass_keywords = ['hi', 'hello', 'hey', 'kaise ho', 'how are you', 'motivate', 'motivation', 'time table', 'routine', 'boring', 'ticbull', 'support', 'contact', 'help', 'app']
    is_timepass = any(word in prompt.lower() for word in timepass_keywords)
    
    system_instruction = f"""You are an elite AI Tutor on TicBull Academy app.
Student: {student_name}
Subject: {board}

RULES:
1. NO ROBOTIC TONE. Act like a helpful human teacher.
2. If asked about TicBull support, tell them to email ticbull.support@gmail.com or contact @ticbullteam on Telegram.
3. Don't mention Gemini, Meta, or DeepSeek. You are TicBull AI."""

    final_reply = None
    
    # 2. If it's timepass & no image attached, try using Free API (Groq/Meta/DeepSeek)
    if is_timepass and not images and GROQ_API_KEY:
        try:
            # Using Groq Cloud for fast free Llama/DeepSeek routing
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "llama3-8b-8192", # Default free model, can be changed to deepseek if supported
                "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}]
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                final_reply = res.json()['choices'][0]['message']['content']
        except:
            pass # Fallback to Gemini if Groq fails
            
    # 3. If it's a study question, has images, or Free API failed -> Use Gemini!
    if not final_reply and VALID_GEMINI_KEYS:
        parts = [{"text": f"{system_instruction}\n\nUser: {prompt}"}]
        for file_data in images:
            if "," in file_data:
                mime_type = file_data.split(';')[0].split(':')[1]
                parts.append({"inline_data": {"mime_type": mime_type, "data": file_data.split(',')[1]}})
                
        payload = {"contents": [{"parts": parts}]}
        for api_key in VALID_GEMINI_KEYS:
            try:
                res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}", json=payload, headers={"Content-Type": "application/json"}, timeout=25)
                res_data = res.json()
                if "candidates" in res_data:
                    final_reply = res_data['candidates'][0]['content']['parts'][0]['text']
                    break
            except: continue

    if final_reply:
        # Increase Usage count in DB here if you want
        return jsonify({"success": True, "reply": final_reply.replace("Gemini", "TicBull").replace("Google", "TicBull")})
    else:
        return jsonify({"success": False, "message": "Server error. Try again."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
