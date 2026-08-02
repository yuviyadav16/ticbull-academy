import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

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
    body = f"Welcome to TicBull Academy! Your 6-Digit Email Verification OTP is: {otp}"
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
        return jsonify({"success": False, "message": "Email zaroori hai!"}), 400
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    
    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": f"OTP sent to {email}"})
    else:
        return jsonify({"success": False, "message": "Email error!"}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    user_otp = data.get('otp', '').strip()
    
    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        return jsonify({"success": True, "message": "Verified!"})
    else:
        return jsonify({"success": False, "message": "Galat OTP!"}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE Board')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science')
    lang = data.get('lang', 'Hinglish')
    
    if not prompt:
        return jsonify({"success": False, "message": "Question empty nahi ho sakta!"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "message": "API Key missing in Vercel!"}), 500
        
    system_instruction = f"""Tu TicBull Academy ka intelligent teacher hai. Tujhe MrYuviYadav ne banaya hai. 
Student {board} {cls} {stream} ka hai. 
Rules: Out of syllabus sawal mana kar dena. Kabhie mat kehna ki tu AI ya Gemini hai. Hamesha {lang} me bolo."""
    
    full_prompt = f"{system_instruction}\n\nStudent Question: {prompt}"
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        reply_text = response.text.replace("Gemini", "TicBull Engine").replace("Google", "TicBull").replace("gemini", "ticbull")
        return jsonify({"success": True, "reply": reply_text})
    except Exception as e:
        return jsonify({"success": False, "message": f"AI Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "TicBull Backend is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
