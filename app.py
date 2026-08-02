import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

otp_store = {}

def send_otp_email(to_email, otp):
    if not SMTP_PASSWORD or not SMTP_EMAIL:
        return False
    subject = "TicBull Academy - Email Verification OTP"
    body = f"Welcome to TicBull Academy! Your 6-Digit Email Verification OTP is: {otp}\n\nDo not share this OTP with anyone."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"TicBull Academy <{SMTP_EMAIL}>"
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        return False

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({"success": False, "message": "Email ID zaroori hai!"}), 400
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": f"OTP successfully sent to {email}"})
    else:
        return jsonify({"success": False, "message": "Email bhejne me error aayi!"}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    user_otp = data.get('otp', '').strip()
    
    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        return jsonify({"success": True, "message": "Email Verified Successfully!"})
    else:
        return jsonify({"success": False, "message": "Galat OTP! Sahi 6-digit OTP daalein."}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE Board')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science (PCM/PCB)')
    lang = data.get('lang', 'Hinglish')
    
    if not prompt:
        return jsonify({"success": False, "message": "Question khali nahi ho sakta!"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "message": "Server API Key missing!"}), 500
        
    # 🛑 STRICT TICBULL AI BRAIN (Syllabus Control)
    system_instruction = f"""Tu TicBull Academy ka ek intelligent aur strict AI Teacher hai. Tujhe MrYuviYadav ne banaya hai.
Tera student abhi '{board} | {cls} | {stream}' ki padhai kar raha hai.
CRITICAL RULES JINHE KABHI NAHI TODNA HAI:
1. OUT OF SYLLABUS STRICTNESS: Agar student ka sawal is course/class se related nahi hai (jaise gaane, movies, politics, ya kisi aur class ka sawal), toh strictly mana kar de aur bol: "Bhai, main TicBull ka AI Teacher hu. Main sirf aapke purchased course ({cls} {stream}) ke sawal hi bata sakta hu. Ye sawal out of syllabus hai."
2. KABHI BHI mat bolna ki tu ek AI hai, LLM hai, ya Google/Gemini ne tujhe banaya hai. 
3. Hamesha {lang} bhasha me jawab de.
"""
    full_prompt = f"{system_instruction}\n\nStudent's Question: {prompt}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        reply_text = response.text.replace("Gemini", "TicBull Engine").replace("Google", "TicBull")
        return jsonify({"success": True, "reply": reply_text})
    except Exception as e:
        # Ab asli error dikhega taaki pata chale issue kya hai
        return jsonify({"success": False, "message": f"AI Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "TicBull Backend is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
