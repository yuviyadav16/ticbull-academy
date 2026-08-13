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
# 🚀 1. BEAST MODE: MULTI-KEY ROTATION SYSTEM (25+ KEYS)
# ========================================================
GEMINI_API_KEYS = []
for key, value in os.environ.items():
    if key.startswith("GEMINI_API_KEY") and value.strip():
        GEMINI_API_KEYS.append(value.strip())

if not GEMINI_API_KEYS:
    GEMINI_API_KEYS = [os.getenv("GEMINI_API_KEY", "")]

VALID_KEYS = list(set([k for k in GEMINI_API_KEYS if k.strip() and "YAHAN_DAALEIN" not in k]))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

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
                "enrolled_batches": db_user.get("enrolled_batches", []) 
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

# --- SUPER SMART AI CHAT ENGINE ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    attachments = data.get('images', []) 
    
    board = data.get('board', 'General Batch')
    subject = data.get('subject', 'General Subject')
    student_name = data.get('student_name', 'Student')
    purchased_plan = data.get('purchased_plan', 'Free Demo Plan')
    email = data.get('email', '').strip().lower()
    token = data.get('token', '') 
    teacher_name = data.get('teacher_name', 'Teacher')
    teacher_gender = data.get('teacher_gender', 'Male')
    
    if not prompt and not attachments: return jsonify({"success": False, "message": "Prompt or Image cannot be empty!"}), 400
    
    # 🔒 USAGE LIMITS
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        session_data = requests.get(db_url(f"sessions/{safe_email}.json")).json() or {}
        if session_data.get("token") != token:
            return jsonify({"success": False, "session_expired": True, "message": "Security Alert: Logged in from another device!"})
            
        user_db = requests.get(db_url(f"users/{safe_email}.json")).json() or {}
        join_date_str = user_db.get("join_date", str(datetime.now().date()))
        try: join_date = datetime.strptime(join_date_str, "%Y-%m-%d").date()
        except: join_date = datetime.now().date()
            
        days_active = (datetime.now().date() - join_date).days
        today_str = str(datetime.now().date())
        usage_url = db_url(f"usage/{safe_email}/{today_str}.json")
        current_usage = requests.get(usage_url).json() or 0
        
        is_free = 'Free' in purchased_plan
        
        if is_free:
            if days_active <= 1: 
                daily_limit = 300 
                if current_usage >= daily_limit: return jsonify({"success": True, "reply": f"⚠️ **Daily Limit Reached!**\nKal try karein."})
            else:
                return jsonify({"success": True, "reply": f"🔒 **Chat Locked - Free Trial Expired!**\n\nAage padhai ke liye Batch kharidein!"})
        else:
            daily_limit = 1000 
            if current_usage >= daily_limit: return jsonify({"success": True, "reply": f"🛑 **Daily Limit Reached!**"})

    # ⚡ 2. SMART IMAGE GENERATOR FIX
    if "image" in prompt.lower() and len(prompt) < 100:
        topic = prompt.lower().replace("describe an educational image prompt for:", "").replace("image", "").replace("generate", "").replace("prompt", "").replace("for:", "").strip()
        img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(topic)}?nologo=true&width=1024&height=1024"
        return jsonify({"success": True, "reply": f"Ye rahi is topic ki image:\n\n![Image]({img_url})"})

    # ⚡ 3. CACHE SYSTEM
    prompt_key = urllib.parse.quote(prompt.lower().strip())
    cache_url = db_url(f"cache/{prompt_key}.json")
    
    if not attachments and FIREBASE_URL:
        try:
            cached_reply = requests.get(cache_url).json()
            if cached_reply:
                if email: requests.put(usage_url, json=current_usage + 1)
                return jsonify({"success": True, "reply": cached_reply, "source": "cache"})
        except: pass

    # ⚡ 4. HYPER-REALISTIC PERSONA
    gender_hint = "female" if teacher_gender.lower() == 'female' else "male"
    
    if gender_hint == "female":
        persona = "You are a highly intellectual and strict Indian female teacher (Madam/Ma'am). Use standard Hinglish with respect (use 'Tum', never use 'Tu' or 'Tera'). If the student wastes time, scold them effectively like an Indian teacher to make them study."
    else:
        persona = "You are an elite, smart, and strict Indian male teacher (Sir). Use proper Hinglish (use 'Tum', never use 'Tu', 'Tera', or cheap slang like 'Yaar'). If the student does timepass, roast them intellectually and guide them back to studies."

    system_instruction = f"""Act exactly as {teacher_name}, an elite and intelligent {subject} expert teacher at TicBull Academy.
Student Name: {student_name}
Student's Academic Level/Batch: {board} (CRITICAL: Use this ONLY to set the difficulty of your teaching. NEVER mention the batch name aloud).

CRITICAL RULES FOR REALISM:
1. IMAGE READING: If the student uploads an image, analyze it extremely carefully and answer their questions based ONLY on the content of that image.
2. NATURAL HINGLISH: Speak like a highly educated Indian teacher. NEVER use cheap slang like 'teri', 'tera', 'yaar' awkwardly. Use 'tum' or 'aap'.
3. NO ROBOTIC GREETINGS: If the student says "Hi" or "Hello", DO NOT reply with "Namaste, main Prof...". Just reply naturally like "Haan {student_name}, batao aaj kis topic mein doubt hai?"
4. PERSONALITY: {persona}
5. HOOK & GUIDE: Your job is to make them study 100%.
6. OUT OF SYLLABUS: You ONLY teach {subject}.
7. APP & SUPPORT: If they ask about login/app issues, clearly say: "Beta, app ya account ki dikkat ke liye ticbull.support@gmail.com par mail kardo, team help kar degi."
8. NO AI MENTIONS: NEVER say you are an AI, an assistant, or Gemini.
"""

    final_reply = None
    
    # ⚡ 5. SMART ROUTER
    is_simple_chat = len(prompt) < 150 and not attachments
    
    if is_simple_chat and GROQ_API_KEY:
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions",
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=7)
            if res.status_code == 200: final_reply = res.json()['choices'][0]['message']['content']
        except: pass

    if not final_reply and VALID_KEYS:
        parts = [{"text": f"{system_instruction}\n\nStudent message: {prompt}"}]
        
        # 🔥 THE CRITICAL IMAGE BUG FIX 🔥
        # Using camelCase "inlineData" and "mimeType" per Google REST API specs!
        for file_data in attachments:
            if "," in file_data:
                mime_type = file_data.split(';')[0].split(':')[1]
                b64_data = file_data.split(',')[1]
                parts.append({"inlineData": {"mimeType": mime_type, "data": b64_data}})
        
        random.shuffle(VALID_KEYS)
        for api_key in VALID_KEYS:
            try:
                res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}", 
                    json={"contents": [{"parts": parts}]}, headers={"Content-Type": "application/json"}, timeout=25)
                res_data = res.json()
                if "candidates" in res_data:
                    final_reply = res_data['candidates'][0]['content']['parts'][0]['text']
                    break
            except: continue

    if final_reply:
        formatted_reply = final_reply.replace("Gemini", "TicBull").replace("Google", "TicBull")
        
        if not attachments and FIREBASE_URL:
            try: requests.put(cache_url, json=formatted_reply)
            except: pass
            
        if email and FIREBASE_URL: requests.put(usage_url, json=current_usage + 1)
        return jsonify({"success": True, "reply": formatted_reply})
        
    return jsonify({"success": False, "message": "Server error. Try again."}), 500

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
        if res.status_code == 200:
            ai_text = res.json()['candidates'][0]['content']['parts'][0]['text']
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
