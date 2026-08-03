import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Keys from Vercel Environment Variables
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
    subject = "TicBull Academy - Verification OTP"
    body = f"Welcome to TicBull Academy! Your 6-Digit Verification OTP is: {otp}"
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
    if not email:
        return jsonify({"success": False, "message": "Email zaroori hai!"}), 400
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": f"OTP sent successfully to {email}"})
    return jsonify({"success": False, "message": "Email configuration error! SMTP credentials check karein."}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    user_otp = data.get('otp', '').strip()
    device_id = data.get('device_id', 'default_device')
    
    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        token = str(random.randint(10000000, 99999999))
        
        if FIREBASE_URL:
            safe_email = sanitize_email(email)
            session_data = {"token": token, "device_id": device_id}
            requests.put(f"{FIREBASE_URL}/sessions/{safe_email}.json", json=session_data)
            
        return jsonify({"success": True, "message": "Verified!", "token": token})
    return jsonify({"success": False, "message": "Galat OTP! Kripya sahi 6-digit OTP daalein."}), 400

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
            return jsonify({"success": True, "active": True})
            
    return jsonify({"success": True, "active": False, "message": "Logged in from another device!"})

# --- AI CHAT ENGINE WITH SUPER INTELLIGENT REAL TEACHER BRAIN ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE Board')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science')
    lang = data.get('lang', 'Hinglish')
    student_name = data.get('student_name', 'Student')
    
    if not prompt:
        return jsonify({"success": False, "message": "Question empty nahi ho sakta!"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "message": "API Key missing in Vercel Environment Variables!"}), 500
        
    system_instruction = f"""Tu TicBull Academy ka Main aur Akela Intelligent Teacher hai. Tujhe MrYuviYadav ne banaya hai.
Student Name: {student_name}
Active Purchased Plan: {board} {cls} {stream}
Language: {lang}

DHYAN RAHE: TicBull app me koi video lectures nahi hain. Tu hi unka akela aur asli teacher hai! Bachhe yahan sirf tujhse chat karke padhne aate hain.

STRICT RULES TO BE A MASTER TEACHER:
1. INTERACTIVE TEACHING: Lamba bookish text mat chaapna. Concept ko step-by-step, chote bullet points me aur easy examples ke sath samjhao. Padhate waqt aakhir me hamesha poocho: "{student_name}, kya ye samajh aaya? Aage badhein?"
2. PERSONAL CONNECTION: Student ko beech-beech me uske naam ({student_name}) se bulao. 
3. CROSS-CLASS STRICTNESS & UPSELL: Agar student active plan ({cls}) ke bahar ka pooche, toh 2-3 line me ek badhiya 'Quick Revision' do aur bolo: "{student_name}, aapka active plan {cls} ka hai. Detail me padhne ke liye aapko TicBull Academy ka wo specific batch buy karna padega. 🚀"
4. CAREER GUIDANCE: JEE/NEET/UPSC ya aage ki padhai par ek expert mentor ki tarah short guidance do, aur hamesha bolo ki "Achhi tayari ke liye TicBull Academy ka premium batch buy karein! 🚀"
5. IDENTITY: Tu sirf 'TicBull Teacher' hai. Google, Gemini, AI word use nahi karna."""
    
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
            err_msg = res_data["error"].get("message", "API Error")
            return jsonify({"success": False, "message": f"AI Error: {err_msg}"}), 500
        else:
            return jsonify({"success": False, "message": "API Response Error"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "TicBull Secure Database & AI Master Teacher Engine is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
