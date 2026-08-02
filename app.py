import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# CONFIGURATION (Set via Environment Variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "YOUR_EMAIL_APP_PASSWORD_HERE")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Temporary OTP Store (In production, use Redis or DB)
otp_store = {}

def send_otp_email(to_email, otp):
    subject = "TicBull Academy - Email Verification OTP"
    body = f"Welcome to TicBull Academy!\n\nYour 6-Digit Email Verification OTP is: {otp}\n\nDo not share this OTP with anyone."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print("SMTP Error:", e)
        return False

# 1. SEND OTP ENDPOINT
@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": f"OTP sent to {email}"})
    else:
        # Fallback for testing if SMTP not configured yet
        return jsonify({"success": True, "message": f"OTP generated (Testing: {otp})", "debug_otp": otp})

# 2. VERIFY OTP ENDPOINT
@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    user_otp = data.get('otp')

    if email in otp_store and otp_store[email] == user_otp:
        del otp_store[email]
        return jsonify({"success": True, "message": "Email Verified Successfully!"})
    else:
        return jsonify({"success": False, "message": "Invalid or Expired OTP!"}), 400

# 3. AI CHAT QUERY ENDPOINT
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt', '')
    board = data.get('board', '')
    cls = data.get('class', '')
    stream = data.get('stream', '')
    lang = data.get('lang', 'Hinglish')

    if not prompt:
        return jsonify({"success": False, "message": "Prompt is required"}), 400

    system_instruction = f"You are an expert AI Tutor for {board}, {cls}, {stream}. Answer clearly in {lang}."
    full_prompt = f"{system_instruction}\n\nStudent Question: {prompt}"

    try:
        response = model.generate_content(full_prompt)
        return jsonify({"success": True, "reply": response.text})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

