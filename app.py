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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "TicBull@2026") # Admin Panel Password

otp_store = {}

def sanitize_email(email):
    return email.replace('.', '_').replace('@', '_at_')

def send_otp_email(to_email, otp, is_delete=False):
    if not SMTP_PASSWORD or not SMTP_EMAIL:
        return False
        
    if is_delete:
        subject = "⚠️ URGENT: Account Deletion OTP - TicBull Academy"
        body = f"WARNING!\n\nYou have requested to PERMANENTLY DELETE your account.\n\nYour Deletion OTP is: {otp}\n\nTicBull Support"
    else:
        subject = "TicBull Academy - Secure Verification OTP"
        body = f"Welcome to TicBull Academy!\n\nYour 6-Digit Secure Verification OTP is: {otp}\n\nPlease do not share this.\n\nTicBull Support Team"
        
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

# --- AUTHENTICATION ENDPOINTS ---

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
                return jsonify({"success": False, "message": "Incorrect Password!"}), 400
        elif auth_mode == 'forgot':
            if not user_check:
                return jsonify({"success": False, "message": "Account not found!"}), 400
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": f"OTP sent to {email}"})
    return jsonify({"success": False, "message": "System configuration error."}), 500

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
            requests.put(f"{FIREBASE_URL}/sessions/{safe_email}.json", json={"token": token, "device_id": device_id})
            
            if auth_mode == 'signup':
                join_date = str(datetime.now().date())
                requests.put(f"{FIREBASE_URL}/users/{safe_email}.json", json={"email": email, "password": password, "join_date": join_date})
            elif auth_mode == 'forgot':
                requests.patch(f"{FIREBASE_URL}/users/{safe_email}.json", json={"password": password})
            
            db_user = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json() or {}
            user_data = {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", "")}
            
        return jsonify({"success": True, "message": "Verification successful!", "token": token, "user": user_data})
    return jsonify({"success": False, "message": "Invalid 6-Digit OTP!"}), 400

# --- ACCOUNT DELETION ENDPOINTS ---

@app.route('/api/send-delete-otp', methods=['POST'])
def send_delete_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    if send_otp_email(email, otp, is_delete=True):
        return jsonify({"success": True, "message": "Deletion Warning OTP sent"})
    return jsonify({"success": False, "message": "Error sending email."}), 500

@app.route('/api/delete-account', methods=['POST'])
def delete_account():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    user_otp = data.get('otp', '').strip()
    
    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        if FIREBASE_URL:
            safe_email = sanitize_email(email)
            # Delete everything related to user
            for path in ['users', 'sessions', 'chats', 'chat_sessions', 'chat_ui', 'usage']:
                requests.delete(f"{FIREBASE_URL}/{path}/{safe_email}.json")
        return jsonify({"success": True, "message": "Account Deleted Permanently!"})
    return jsonify({"success": False, "message": "Invalid Deletion OTP!"}), 400

# --- PROFILE & SESSION ENDPOINTS ---

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        update_data = {"name": data.get("name"), "dob": data.get("dob"), "photo": data.get("photo")}
        requests.patch(f"{FIREBASE_URL}/users/{safe_email}.json", json=update_data)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/check-session', methods=['POST'])
def check_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    token = data.get('token', '')
    
    if not FIREBASE_URL:
        return jsonify({"success": True, "active": True})
        
    safe_email = sanitize_email(email)
    res = requests.get(f"{FIREBASE_URL}/sessions/{safe_email}.json").json() or {}
    if res.get("token") == token:
        db_user = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json() or {}
        user_data = {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", "")}
        return jsonify({"success": True, "active": True, "user": user_data})
        
    return jsonify({"success": True, "active": False, "message": "Session Expired!"})

# --- MULTI-SESSION CHAT ENDPOINTS ---

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
        sessions = requests.get(f"{FIREBASE_URL}/chat_sessions/{safe_email}.json").json() or {}
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
        res = requests.get(f"{FIREBASE_URL}/chat_sessions/{safe_email}/{session_id}.json").json() or {}
        return jsonify({"success": True, "html": res.get("html", "")})
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

# --- RATE LIMITING & GEMINI AI ENGINE ---

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science')
    lang = data.get('lang', 'Hinglish')
    student_name = data.get('student_name', 'Student')
    purchased_plan = data.get('purchased_plan', 'Free Demo Plan')
    email = data.get('email', '').strip().lower()
    
    if not prompt:
        return jsonify({"success": False, "message": "Prompt cannot be empty!"}), 400
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "message": "API Key is missing!"}), 500
    
    # 1. FAIR USAGE POLICY (FUP) RATE LIMITING
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        today_str = str(datetime.now().date())
        usage_url = f"{FIREBASE_URL}/usage/{safe_email}/{today_str}.json"
        
        current_usage = requests.get(usage_url).json() or 0
        is_free = 'Free' in purchased_plan
        daily_limit = 5 if is_free else 50
        
        if current_usage >= daily_limit:
            if is_free:
                return jsonify({"success": True, "reply": f"⚠️ **Daily Limit Reached!**\n\n{student_name}, aapne aaj ke 5 free prompts use kar liye hain. Unlimited access aur poori padhai ke liye kripya **Premium Pass** activate karein! 🚀"})
            else:
                return jsonify({"success": True, "reply": f"🛑 **Screen Time Limit Reached!**\n\n{student_name}, aapne aaj ki maximum limit (50/50) poori kar li hai. Healthy mind ke liye ab aaram karein aur kal wapas aayen!"})
    
    # 2. GEMINI AI CALL
    system_instruction = f"""You are TicBull Teacher. Developed by MrYuviYadav.
Student: {student_name}
Plan: {purchased_plan}
Course: {board} {cls} {stream} in {lang}
Teach clearly in bullet points. Do not mention Google or Gemini."""

    try:
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": f"{system_instruction}\n\nQuestion: {prompt}"}]}]}
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
        res = requests.post(url, json=payload, headers=headers, timeout=25)
        res_data = res.json()
        
        if "candidates" in res_data:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
            reply = reply.replace("Gemini", "TicBull").replace("Google", "TicBull")
            
            # Increment Usage Counter in Database
            if email and FIREBASE_URL:
                requests.put(usage_url, json=current_usage + 1)
                
            return jsonify({"success": True, "reply": reply})
            
        elif "error" in res_data:
            return jsonify({"success": False, "message": f"AI Error: {res_data['error'].get('message')}"}), 500
        else:
            return jsonify({"success": False, "message": "API Response Error"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- ADMIN PANEL ENDPOINTS ---

@app.route('/api/admin/data', methods=['POST'])
def admin_data():
    data = request.get_json() or {}
    
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Access Denied. Wrong Password!"}), 403
        
    if FIREBASE_URL:
        users = requests.get(f"{FIREBASE_URL}/users.json").json() or {}
        usage = requests.get(f"{FIREBASE_URL}/usage.json").json() or {}
        
        user_list = []
        for email_key, udata in users.items():
            email_real = email_key.replace('_at_', '@').replace('_', '.')
            user_list.append({
                "email": email_real, 
                "name": udata.get("name", "Unknown"), 
                "joined": udata.get("join_date", "Old User")
            })
            
        return jsonify({"success": True, "total_users": len(user_list), "users": user_list, "usage_raw": usage})
        
    return jsonify({"success": False, "message": "Database not connected."})

@app.route('/')
def home():
    return "TicBull Master AI Engine is securely running with API Rate Limiting!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
    
@app.route('/admin.html')
def admin_page():
    return app.send_static_file('admin.html')
