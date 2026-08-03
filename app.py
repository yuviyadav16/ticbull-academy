import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')

otp_store = {}

def sanitize_email(email):
    return email.replace('.', '_').replace('@', '_at_')

def send_otp_email(to_email, otp):
    if not SMTP_PASSWORD or not SMTP_EMAIL:
        return False
    subject = "TicBull Academy - Secure Verification OTP"
    body = f"Welcome to TicBull Academy!\n\nYour 6-Digit Secure Verification OTP is: {otp}\n\nPlease do not share this OTP with anyone.\n\nBest Regards,\nTicBull Support Team"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"TicBull Academy <{SMTP_EMAIL}>"
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except:
        return False

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    auth_mode = data.get('auth_mode', 'login')
    
    if not email:
        return jsonify({"success": False, "message": "Email address is required!"}), 400
        
    if FIREBASE_URL:
        safe_email = sanitize_email(email)
        user_check = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json()
        
        if auth_mode == 'signup':
            if user_check:
                return jsonify({"success": False, "message": "Account already exists! Please Sign In."}), 400
        elif auth_mode == 'login':
            if not user_check:
                return jsonify({"success": False, "message": "Account not found! Please Create an Account first."}), 400
            if user_check.get('password') != password:
                return jsonify({"success": False, "message": "Incorrect Password! Please try again."}), 400
        elif auth_mode == 'forgot':
            if not user_check:
                return jsonify({"success": False, "message": "Account not found! Enter a registered email."}), 400
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": f"OTP sent successfully to {email}"})
    return jsonify({"success": False, "message": "System configuration error. Contact Support."}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    user_otp = data.get('otp', '').strip()
    password = data.get('password', '').strip()
    auth_mode = data.get('auth_mode', 'login')
    device_id = data.get('device_id', 'default_device')
    
    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        token = str(random.randint(10000000, 99999999))
        user_data = {}
        
        if FIREBASE_URL:
            safe_email = sanitize_email(email)
            session_data = {"token": token, "device_id": device_id}
            requests.put(f"{FIREBASE_URL}/sessions/{safe_email}.json", json=session_data)
            
            if auth_mode == 'signup':
                requests.put(f"{FIREBASE_URL}/users/{safe_email}.json", json={"email": email, "password": password})
            elif auth_mode == 'forgot':
                requests.patch(f"{FIREBASE_URL}/users/{safe_email}.json", json={"password": password})
            
            db_user = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json() or {}
            user_data = {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", "")}
            
        return jsonify({"success": True, "message": "Verification successful!", "token": token, "user": user_data})
    return jsonify({"success": False, "message": "Invalid 6-Digit OTP!"}), 400

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        update_data = {"name": data.get("name"), "dob": data.get("dob"), "photo": data.get("photo")}
        requests.patch(f"{FIREBASE_URL}/users/{safe_email}.json", json=update_data)
        return jsonify({"success": True, "message": "Profile updated successfully!"})
    return jsonify({"success": False, "message": "Failed to update profile."})

@app.route('/api/check-session', methods=['POST'])
def check_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    token = data.get('token', '')
    
    if not FIREBASE_URL:
        return jsonify({"success": True, "active": True})
        
    safe_email = sanitize_email(email)
    res = requests.get(f"{FIREBASE_URL}/sessions/{safe_email}.json")
    if res.status_code == 200 and res.json():
        db_session = res.json()
        if db_session.get("token") == token:
            db_user = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json() or {}
            user_data = {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", "")}
            return jsonify({"success": True, "active": True, "user": user_data})
            
    return jsonify({"success": True, "active": False, "message": "Session Expired! Logged in from another device."})


# ==========================================
# TRUE CHATGPT-LIKE MULTI-SESSION ARCHITECTURE
# ==========================================

@app.route('/api/sync-session', methods=['POST'])
def sync_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    session_id = data.get('session_id')
    title = data.get('title', 'New Chat')
    chat_html = data.get('html', '')
    
    if email and session_id and FIREBASE_URL:
        safe_email = sanitize_email(email)
        payload = {"title": title, "html": chat_html}
        requests.put(f"{FIREBASE_URL}/chat_sessions/{safe_email}/{session_id}.json", json=payload)
    return jsonify({"success": True})

@app.route('/api/get-sessions', methods=['POST'])
def get_sessions():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        res = requests.get(f"{FIREBASE_URL}/chat_sessions/{safe_email}.json")
        if res.status_code == 200 and res.json():
            sessions = res.json()
            session_list = [{"id": k, "title": v.get("title", "Chat")} for k, v in sessions.items() if v]
            session_list.sort(key=lambda x: x["id"], reverse=True)
            return jsonify({"success": True, "sessions": session_list})
    return jsonify({"success": True, "sessions": []})

@app.route('/api/get-session-html', methods=['POST'])
def get_session_html():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    session_id = data.get('session_id')
    if email and session_id and FIREBASE_URL:
        safe_email = sanitize_email(email)
        res = requests.get(f"{FIREBASE_URL}/chat_sessions/{safe_email}/{session_id}.json")
        if res.status_code == 200 and res.json():
            return jsonify({"success": True, "html": res.json().get("html", "")})
    return jsonify({"success": False, "html": ""})

@app.route('/api/delete-session', methods=['POST'])
def delete_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    session_id = data.get('session_id')
    if email and session_id and FIREBASE_URL:
        safe_email = sanitize_email(email)
        requests.delete(f"{FIREBASE_URL}/chat_sessions/{safe_email}/{session_id}.json")
    return jsonify({"success": True})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE Board')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science')
    lang = data.get('lang', 'Hinglish')
    student_name = data.get('student_name', 'Student')
    purchased_plan = data.get('purchased_plan', 'Free Demo Plan')
    
    if not prompt:
        return jsonify({"success": False, "message": "Prompt cannot be empty!"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "message": "API Key is missing!"}), 500
        
    system_instruction = f"""You are the Master AI Teacher for 'TicBull Academy'. Developed exclusively by MrYuviYadav.
Student Name: {student_name}
Current Active Plan: {purchased_plan}
Selected Course: {board} {cls} {stream}
Language: {lang}

STRICT INTELLIGENCE RULES:
1. FREE PLAN UPSELL: If the student is on 'Free Demo Plan', provide a concise, basic explanation. Softly urge them: "To unlock highly detailed visual notes and complete syllabus, please upgrade to the TicBull Premium Batch! 🚀"
2. TEACHING STYLE: Use well-structured bullet points, bold keywords, and extremely easy-to-understand examples. Always ask a highly engaging closing question like: "{student_name}, is this concept 100% clear?"
3. IDENTITY: You are strictly 'TicBull Teacher'. NEVER mention Google, Gemini, OpenAI, or LLM. Respond naturally as an expert human educator."""
    
    full_prompt = f"{system_instruction}\n\nStudent Question: {prompt}"
    
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        
        model_name = "gemini-flash-latest"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        res_data = response.json()
        
        if "candidates" in res_data:
            reply_text = res_data['candidates'][0]['content']['parts'][0]['text']
            reply_text = reply_text.replace("Gemini", "TicBull").replace("Google", "TicBull")
            return jsonify({"success": True, "reply": reply_text})
        elif "error" in res_data:
            return jsonify({"success": False, "message": f"AI Engine Error: {res_data['error'].get('message')}"}), 500
        else:
            return jsonify({"success": False, "message": "Invalid API Response."}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Server Connection Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "TicBull Master AI Engine is securely running with ChatGPT Multi-Session Architecture!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
