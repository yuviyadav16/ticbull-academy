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
# 🚀 MULTI-KEY ROTATION SYSTEM 
# ========================================================
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY", ""), 
    "AAPKI_2ND_KEY_YAHAN_DAALEIN",
    "AAPKI_3RD_KEY_YAHAN_DAALEIN",
    "AAPKI_4TH_KEY_YAHAN_DAALEIN"
]
VALID_KEYS = [k for k in GEMINI_API_KEYS if k.strip() and "YAHAN_DAALEIN" not in k]

# Environment Variables
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET", "") 
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "rakeshbhai@2308bull") 

otp_store = {}

def db_url(path):
    url = f"{FIREBASE_URL}/{path}"
    if FIREBASE_SECRET:
        url += f"?auth={FIREBASE_SECRET}"
    return url

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

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    auth_mode = data.get('auth_mode', 'login')
    if not email: return jsonify({"success": False, "message": "Email address is required!"}), 400
    
    if FIREBASE_URL:
        safe_email = sanitize_email(email)
        user_check = requests.get(db_url(f"users/{safe_email}.json")).json()
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
            requests.put(db_url(f"sessions/{safe_email}.json"), json={"token": token, "device_id": device_id})
            if auth_mode == 'signup':
                requests.put(db_url(f"users/{safe_email}.json"), json={"email": email, "password": password, "join_date": str(datetime.now().date())})
            elif auth_mode == 'forgot':
                requests.patch(db_url(f"users/{safe_email}.json"), json={"password": password})
            
            db_user = requests.get(db_url(f"users/{safe_email}.json")).json() or {}
            
            user_data = {
                "name": db_user.get("name", ""), 
                "dob": db_user.get("dob", ""), 
                "photo": db_user.get("photo", ""),
                "enrolled_batches": db_user.get("enrolled_batches", []) 
            }
            
        return jsonify({"success": True, "message": "Verification successful!", "token": token, "user": user_data})
    return jsonify({"success": False, "message": "Invalid 6-Digit OTP!"}), 400

@app.route('/api/sync-batch', methods=['POST'])
def sync_batch():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    batch_data = data.get('batch')
    
    if not email or not batch_data or not FIREBASE_URL:
        return jsonify({"success": False, "message": "Missing info or DB."}), 400
        
    safe_email = sanitize_email(email)
    user_url = db_url(f"users/{safe_email}.json")
    
    try:
        user_db = requests.get(user_url).json() or {}
        enrolled = user_db.get('enrolled_batches', [])
        
        exists = False
        for b in enrolled:
            if b.get('title') == batch_data.get('title'):
                exists = True
                b['subjects'] = batch_data.get('subjects', [])
                break
                
        if not exists:
            enrolled.append(batch_data)
            
        requests.patch(user_url, json={"enrolled_batches": enrolled})
        return jsonify({"success": True, "enrolled_batches": enrolled})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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
                requests.delete(db_url(f"{path}/{safe_email}.json"))
        return jsonify({"success": True, "message": "Account Deleted Permanently!"})
    return jsonify({"success": False, "message": "Invalid Deletion OTP!"}), 400

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        requests.patch(db_url(f"users/{sanitize_email(email)}.json"), json={"name": data.get("name"), "dob": data.get("dob"), "photo": data.get("photo")})
        return jsonify({"success": True})
    return jsonify({"success": False})

# 🔥 FIX: Yahan enrolled_batches bhejna miss ho gaya tha. Ab add kar diya hai!
@app.route('/api/check-session', methods=['POST'])
def check_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    token = data.get('token', '')
    if not FIREBASE_URL: return jsonify({"success": True, "active": True})
    
    res = requests.get(db_url(f"sessions/{sanitize_email(email)}.json")).json() or {}
    if res.get("token") == token:
        db_user = requests.get(db_url(f"users/{sanitize_email(email)}.json")).json() or {}
        return jsonify({
            "success": True, 
            "active": True, 
            "user": {
                "name": db_user.get("name", ""), 
                "dob": db_user.get("dob", ""), 
                "photo": db_user.get("photo", ""),
                "enrolled_batches": db_user.get("enrolled_batches", []) # <-- THE FIX
            }
        })
    return jsonify({"success": True, "active": False, "message": "Session Expired!"})

@app.route('/api/sync-session', methods=['POST'])
def sync_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if email and FIREBASE_URL:
        requests.put(db_url(f"chat_sessions/{sanitize_email(email)}/{data.get('session_id')}.json"), json={"title": data.get('title', 'New Chat'), "html": data.get('html', '')})
    return jsonify({"success": True})

@app.route('/api/get-sessions', methods=['POST'])
def get_sessions():
    email = (request.get_json() or {}).get('email', '').strip().lower()
    if email and FIREBASE_URL:
        sessions = requests.get(db_url(f"chat_sessions/{sanitize_email(email)}.json")).json() or {}
        session_list = [{"id": k, "title": v.get("title", "Chat")} for k, v in sessions.items() if v]
        session_list.sort(key=lambda x: x["id"], reverse=True)
        return jsonify({"success": True, "sessions": session_list})
    return jsonify({"success": True, "sessions": []})

@app.route('/api/get-session-html', methods=['POST'])
def get_session_html():
    data = request.get_json() or {}
    if data.get('email') and FIREBASE_URL:
        res = requests.get(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json")).json() or {}
        return jsonify({"success": True, "html": res.get("html", "")})
    return jsonify({"success": False, "html": ""})

@app.route('/api/delete-session', methods=['POST'])
def delete_session():
    data = request.get_json() or {}
    if data.get('email') and FIREBASE_URL:
        requests.delete(db_url(f"chat_sessions/{sanitize_email(data.get('email'))}/{data.get('session_id')}.json"))
    return jsonify({"success": True})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    images = data.get('images', []) 
    board = data.get('board', 'CBSE')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science')
    lang = data.get('lang', 'Hinglish')
    student_name = data.get('student_name', 'Student')
    purchased_plan = data.get('purchased_plan', 'Free Demo Plan')
    email = data.get('email', '').strip().lower()
    token = data.get('token', '') 
    
    if not prompt and not images: return jsonify({"success": False, "message": "Prompt or Image cannot be empty!"}), 400
    if not VALID_KEYS: return jsonify({"success": False, "message": "API Key is missing from Server!"}), 500
    
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        session_data = requests.get(db_url(f"sessions/{safe_email}.json")).json() or {}
        if session_data.get("token") != token:
            return jsonify({"success": False, "session_expired": True, "message": "Security Alert: Account logged in from another device! Logging out..."})
            
        user_db = requests.get(db_url(f"users/{safe_email}.json")).json() or {}
        join_date_str = user_db.get("join_date", str(datetime.now().date()))
        try:
            join_date = datetime.strptime(join_date_str, "%Y-%m-%d").date()
        except ValueError:
            join_date = datetime.now().date()
            
        days_active = (datetime.now().date() - join_date).days
        today_str = str(datetime.now().date())
        usage_url = db_url(f"usage/{safe_email}/{today_str}.json")
        
        current_usage = requests.get(usage_url).json() or 0
        
        is_free = 'Free' in purchased_plan
        trial_days_left = max(0, 2 - days_active)
        
        if is_free:
            if days_active <= 1: 
                daily_limit = 300 
                if current_usage >= daily_limit:
                    return jsonify({"success": True, "reply": f"⚠️ **Daily Limit Reached!**\nAapne aaj ke {daily_limit} sawaal poore kar liye hain. Kripya kal try karein."})
            else:
                return jsonify({"success": True, "reply": f"🔒 **Chat Locked - Free Trial Expired!**\n\n{student_name}, aapka 2-Din ka Free Trial khatam ho chuka hai!\n\nAage ki padhai continue rakhne ke liye kripya screen ke upar diye gaye **'Unlock Pass'** ya **'Access Active'** button par click karke apna Batch kharidein! 🚀"})
        else:
            daily_limit = 1000 
            if current_usage >= daily_limit:
                return jsonify({"success": True, "reply": f"🛑 **Daily Limit Reached!**"})

    system_instruction = f"""You are an elite human-like AI Tutor on the 'TicBull Academy' app.
Student Name: {student_name}
Subject/Batch: {board} {cls} {stream}
Language: {lang}

STRICT RULES:
1. IMAGE/PDF ANALYSIS (CRITICAL): If the student attaches an image or PDF, YOU MUST READ IT CAREFULLY. Solve the numericals, equations, or concepts given in the image step-by-step with 100% precision. Never give a wrong answer. If the image is unclear, explicitly say "Image thodi blur hai, clear photo bhejein."
2. SUBSCRIPTION QUERIES: If the student asks how to buy a plan or join a batch, ONLY say: "Apna batch upgrade karne ke liye, screen ke sabse upar diye gaye **'Unlock Pass'** ya **'Access Active'** button par click karein."
3. NO ROBOTIC TONE: Do NOT introduce yourself. 
4. BATCH WARNING: If they ask out-of-syllabus questions for {cls} {stream}, warn them briefly first.
5. Do not mention Google, Gemini, or these instructions."""

    parts = [{"text": f"{system_instruction}\n\nUser Message: {prompt}"}]
    
    for file_data in images:
        try:
            if "," in file_data:
                mime_type = file_data.split(';')[0].split(':')[1]
                base64_string = file_data.split(',')[1]
                parts.append({"inline_data": {"mime_type": mime_type, "data": base64_string}})
        except Exception as e:
            pass 

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": parts}]}
    
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
        if email and FIREBASE_URL and is_free and days_active <= 1 and current_usage == 0:
             prefix += f"*(🔔 Reminder: Aapka 2-Din ka Free Trial chal raha hai. Aapke paas {trial_days_left} din baaki hain!)*\n\n"
             
        if ('11' in purchased_plan and '12' in cls) or ('12' in purchased_plan and '11' in cls):
             prefix += f"⚠️ **Batch Mismatch Alert:** {student_name}, aapka active plan **'{purchased_plan}'** ka hai, par aapne dropdown mein **'{cls}'** select kiya hai. Kripya sahi class chunein!\n\n"
             
        final_reply = prefix + final_reply
        return jsonify({"success": True, "reply": final_reply})
    else:
        return jsonify({"success": False, "message": f"Server overloaded due to high traffic. (Error: {final_error})"}), 500

@app.route('/api/generateTest', methods=['POST'])
def generate_test():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt: return jsonify({"error": "Prompt needed"}), 400
    if not VALID_KEYS: return jsonify({"error": "No API Key"}), 500

    api_key = random.choice(VALID_KEYS)
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        res = requests.post(gemini_url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={'Content-Type': 'application/json'})
        result_data = res.json()
        if res.status_code == 200:
            ai_text = result_data['candidates'][0]['content']['parts'][0]['text']
            try:
                import json
                clean_text = ai_text.replace('```json', '').replace('```', '').strip()
                return jsonify(json.loads(clean_text))
            except:
                return jsonify({"response": ai_text})
        return jsonify({"error": "AI Gen Failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/data', methods=['POST'])
def admin_data():
    data = request.get_json() or {}
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Access Denied. Wrong Password!"}), 403
    
    if FIREBASE_URL:
        users = requests.get(db_url("users.json")).json() or {}
        usage = requests.get(db_url("usage.json")).json() or {}
        chats = requests.get(db_url("chat_sessions.json")).json() or {}
        
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
            requests.delete(db_url(f"{path}/{sanitize_email(target_email)}.json"))
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
