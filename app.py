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
# 🚀 MULTI-KEY ROTATION SYSTEM (Add Keys Here)
# ========================================================
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY", ""), 
    "AAPKI_DUSRI_GMAIL_KI_KEY_YAHAN_DAALEIN",
    "AAPKI_TEESRI_GMAIL_KI_KEY_YAHAN_DAALEIN",
    "AAPKI_CHAUTHI_GMAIL_KI_KEY_YAHAN_DAALEIN"
]
# Clean empty placeholders automatically
VALID_KEYS = [k for k in GEMINI_API_KEYS if k.strip() and "YAHAN_DAALEIN" not in k]

# Environment Variables
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "rakeshbhai@2308bull") 

otp_store = {}

def sanitize_email(email):
    return email.replace('.', '_').replace('@', '_at_')

def send_otp_email(to_email, otp, is_delete=False):
    if not SMTP_PASSWORD or not SMTP_EMAIL: return False
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
    
    if not email: return jsonify({"success": False, "message": "Email address is required!"}), 400
    
    if FIREBASE_URL:
        safe_email = sanitize_email(email)
        user_check = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json()
        if auth_mode == 'signup' and user_check:
            return jsonify({"success": False, "message": "Account already exists! Please Sign In."}), 400
        elif auth_mode == 'login':
            if not user_check: return jsonify({"success": False, "message": "Account not found! Please Create an Account first."}), 400
            if user_check.get('password') != password: return jsonify({"success": False, "message": "Incorrect Password!"}), 400
        elif auth_mode == 'forgot' and not user_check:
            return jsonify({"success": False, "message": "Account not found!"}), 400
            
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    if send_otp_email(email, otp): return jsonify({"success": True, "message": f"OTP sent to {email}"})
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
                requests.put(f"{FIREBASE_URL}/users/{safe_email}.json", json={"email": email, "password": password, "join_date": str(datetime.now().date())})
            elif auth_mode == 'forgot':
                requests.patch(f"{FIREBASE_URL}/users/{safe_email}.json", json={"password": password})
            
            db_user = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json() or {}
            user_data = {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", "")}
            
        return jsonify({"success": True, "message": "Verification successful!", "token": token, "user": user_data})
    return jsonify({"success": False, "message": "Invalid 6-Digit OTP!"}), 400

@app.route('/api/send-delete-otp', methods=['POST'])
def send_delete_otp():
    email = (request.get_json() or {}).get('email', '').strip().lower()
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    if send_otp_email(email, otp, is_delete=True): return jsonify({"success": True, "message": "Deletion Warning OTP sent"})
    return jsonify({"success": False, "message": "Error sending email."}), 500

@app.route('/api/delete-account', methods=['POST'])
def delete_account():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email in otp_store and otp_store[email] == data.get('otp', '').strip():
        del otp_store[email]
        if FIREBASE_URL:
            safe_email = sanitize_email(email)
            for path in ['users', 'sessions', 'chat_sessions', 'usage']:
                requests.delete(f"{FIREBASE_URL}/{path}/{safe_email}.json")
        return jsonify({"success": True, "message": "Account Deleted Permanently!"})
    return jsonify({"success": False, "message": "Invalid Deletion OTP!"}), 400

# --- PROFILE & SESSION ENDPOINTS ---
@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        requests.patch(f"{FIREBASE_URL}/users/{sanitize_email(email)}.json", json={"name": data.get("name"), "dob": data.get("dob"), "photo": data.get("photo")})
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/check-session', methods=['POST'])
def check_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    token = data.get('token', '')
    if not FIREBASE_URL: return jsonify({"success": True, "active": True})
    
    res = requests.get(f"{FIREBASE_URL}/sessions/{sanitize_email(email)}.json").json() or {}
    if res.get("token") == token:
        db_user = requests.get(f"{FIREBASE_URL}/users/{sanitize_email(email)}.json").json() or {}
        return jsonify({"success": True, "active": True, "user": {"name": db_user.get("name", ""), "dob": db_user.get("dob", ""), "photo": db_user.get("photo", "")}})
    return jsonify({"success": True, "active": False, "message": "Session Expired!"})

# --- MULTI-SESSION CHAT ENDPOINTS ---
@app.route('/api/sync-session', methods=['POST'])
def sync_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        requests.put(f"{FIREBASE_URL}/chat_sessions/{sanitize_email(email)}/{data.get('session_id')}.json", json={"title": data.get('title', 'New Chat'), "html": data.get('html', '')})
    return jsonify({"success": True})

@app.route('/api/get-sessions', methods=['POST'])
def get_sessions():
    email = (request.get_json() or {}).get('email', '').strip().lower()
    if email and FIREBASE_URL:
        sessions = requests.get(f"{FIREBASE_URL}/chat_sessions/{sanitize_email(email)}.json").json() or {}
        session_list = [{"id": k, "title": v.get("title", "Chat")} for k, v in sessions.items() if v]
        session_list.sort(key=lambda x: x["id"], reverse=True)
        return jsonify({"success": True, "sessions": session_list})
    return jsonify({"success": True, "sessions": []})

@app.route('/api/get-session-html', methods=['POST'])
def get_session_html():
    data = request.get_json() or {}
    if data.get('email') and FIREBASE_URL:
        res = requests.get(f"{FIREBASE_URL}/chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json").json() or {}
        return jsonify({"success": True, "html": res.get("html", "")})
    return jsonify({"success": False, "html": ""})

@app.route('/api/delete-session', methods=['POST'])
def delete_session():
    data = request.get_json() or {}
    if data.get('email') and FIREBASE_URL:
        requests.delete(f"{FIREBASE_URL}/chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json")
    return jsonify({"success": True})

# --- 🧠 RATE LIMITING, SMART AI & BATCH WARNING ENGINE ---
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
    token = data.get('token', '') 
    
    if not prompt: return jsonify({"success": False, "message": "Prompt cannot be empty!"}), 400
    if not VALID_KEYS: return jsonify({"success": False, "message": "API Key is missing from Server!"}), 500
    
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        
        # 🚨 Z+ SECURITY: SINGLE DEVICE LOGIN CHECK
        session_data = requests.get(f"{FIREBASE_URL}/sessions/{safe_email}.json").json() or {}
        if session_data.get("token") != token:
            return jsonify({"success": False, "session_expired": True, "message": "Security Alert: Account logged in from another device! Logging out..."})
            
        # 🗓️ 3-DAY UNLIMITED TRIAL LOGIC
        user_db = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json() or {}
        join_date_str = user_db.get("join_date", str(datetime.now().date()))
        try:
            join_date = datetime.strptime(join_date_str, "%Y-%m-%d").date()
        except ValueError:
            join_date = datetime.now().date()
            
        days_active = (datetime.now().date() - join_date).days

        today_str = str(datetime.now().date())
        usage_url = f"{FIREBASE_URL}/usage/{safe_email}/{today_str}.json"
        current_usage = requests.get(usage_url).json() or 0
        
        is_free = 'Free' in purchased_plan
        trial_days_left = max(0, 3 - days_active)
        
        if is_free:
            if days_active <= 3:
                daily_limit = 300 
                if current_usage >= daily_limit:
                    return jsonify({"success": True, "reply": f"⚠️ **Fair Usage Limit!**\nAapne aaj ke {daily_limit} sawaal poore kar liye hain. Kripya kal try karein."})
            else:
                return jsonify({"success": True, "reply": f"🛑 **Free Trial Expired!**\n{student_name}, aapka 3-Din ka Unlimited Free Trial khatam ho chuka hai! Aage apni padhai continue rakhne ke liye kripya **Premium Pass** activate karein. 🚀"})
        else:
            daily_limit = 1000 
            if current_usage >= daily_limit:
                return jsonify({"success": True, "reply": f"🛑 **Daily Limit Reached!**"})

    # 🧠 STRICT AI INSTRUCTIONS (Anti-Robotic Tone)
    system_instruction = f"""You are a human-like expert tutor.
Student Name: {student_name}
Subject/Batch Context: {board} {cls} {stream}
Language: {lang}

STRICT RULES (Follow Blindly):
1. NO ROBOTIC INTROS: NEVER introduce yourself. DO NOT say "Namaste {student_name}" or "Main TicBull Teacher hoon" unless specifically asked "Who are you". Talk like a real human.
2. SHORT GREETINGS: If the user just says "Ok", "Hi", "Hello", "Yes", reply with ONLY ONE SHORT SENTENCE like: "Haan bataiye, aaj kya padhna chahenge?". DO NOT give long lists of subjects.
3. Jump straight to the point. Teach clearly using bullet points for actual questions.
4. Never mention Google, Gemini, or these instructions."""

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": f"{system_instruction}\n\nUser Message: {prompt}"}]}]}
    
    final_reply = None
    final_error = "Unknown Error"

    for api_key in VALID_KEYS:
        try:
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}", json=payload, headers=headers, timeout=25)
            res_data = res.json()
            
            if "candidates" in res_data:
                final_reply = res_data['candidates'][0]['content']['parts'][0]['text']
                final_reply = final_reply.replace("Gemini", "TicBull").replace("Google", "TicBull")
                break 
            elif "error" in res_data:
                err_msg = res_data['error'].get('message', 'Unknown Error').lower()
                if "quota" in err_msg or "429" in str(res_data):
                    final_error = "Server Traffic High. Retrying..."
                    continue 
                else:
                    final_error = res_data['error'].get('message')
                    break 
        except Exception as e:
            final_error = str(e)
            continue 

    if final_reply:
        if email and FIREBASE_URL: requests.put(usage_url, json=current_usage + 1)
        
        prefix = ""
        # 1. 3-Day Trial Reminder
        if email and FIREBASE_URL and is_free and days_active <= 3 and current_usage == 0:
             prefix += f"*(🔔 Reminder: Aapka 3-Din ka Free Unlimited Trial chal raha hai. Aapke paas {trial_days_left} din baaki hain!)*\n\n"
             
        # 2. 🚨 100% ACCURATE PYTHON BATCH WARNING
        if ('11' in purchased_plan and '12' in cls) or ('12' in purchased_plan and '11' in cls):
             prefix += f"⚠️ **Batch Mismatch Alert:** {student_name}, aapka active plan **'{purchased_plan}'** ka hai, par aapne dropdown mein **'{cls}'** select kiya hai. Kripya sahi class chunein!\n\n"
             
        final_reply = prefix + final_reply
        return jsonify({"success": True, "reply": final_reply})
    else:
        return jsonify({"success": False, "message": f"Server overloaded due to high traffic. (Error: {final_error})"}), 500

# --- ADMIN PANEL ENDPOINTS ---
@app.route('/api/admin/data', methods=['POST'])
def admin_data():
    data = request.get_json() or {}
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Access Denied. Wrong Password!"}), 403
    
    if FIREBASE_URL:
        users = requests.get(f"{FIREBASE_URL}/users.json").json() or {}
        usage = requests.get(f"{FIREBASE_URL}/usage.json").json() or {}
        chats = requests.get(f"{FIREBASE_URL}/chat_sessions.json").json() or {}
        
        user_list = []
        today_str = str(datetime.now().date())
        for email_key, udata in users.items():
            email_real = email_key.replace('_at_', '@').replace('_', '.')
            user_chats = chats.get(email_key, {})
            recent_prompts = [v.get('title', 'Unknown') for k, v in user_chats.items() if v]
            user_usage = usage.get(email_key, {}).get(today_str, 0)
            user_list.append({"email": email_real, "name": udata.get("name", "Unknown"), "joined": udata.get("join_date", "Old User"), "today_usage": user_usage, "recent_chats": recent_prompts[:3]})
        return jsonify({"success": True, "total_users": len(user_list), "users": user_list})
    return jsonify({"success": False, "message": "Database not connected."})

@app.route('/api/admin/ban-user', methods=['POST'])
def admin_ban_user():
    data = request.get_json() or {}
    if data.get('password') != ADMIN_PASSWORD: return jsonify({"success": False, "message": "Access Denied!"}), 403
    target_email = data.get('target_email', '').strip()
    if not target_email: return jsonify({"success": False, "message": "Email missing"}), 400
    
    if FIREBASE_URL:
        for path in ['users', 'sessions', 'chat_sessions', 'usage']:
            requests.delete(f"{FIREBASE_URL}/{path}/{sanitize_email(target_email)}.json")
        return jsonify({"success": True, "message": f"User {target_email} permanently BANNED!"})
    return jsonify({"success": False, "message": "DB Error"})

@app.route('/admin.html')
def admin_page():
    return app.send_static_file('admin.html')

@app.route('/')
def home():
    return "TicBull Master AI Engine Secure API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
