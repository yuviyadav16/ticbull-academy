import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Environment Variables (Set these on Render/Vercel)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Gmail App Password

# Temporary OTP Storage
otp_store = {}

def send_otp_email(to_email, otp):
    if not SMTP_PASSWORD:
        return False
    
    subject = "TicBull Academy - Email Verification OTP"
    body = f"Welcome to TicBull Academy! 🚀\n\nYour 6-Digit Email Verification OTP is: {otp}\n\nDo not share this OTP with anyone.\n\nRegards,\nMrYuviYadav\nFounder, TicBull Academy"
    
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
        print("SMTP Email Error:", e)
        return False

# 1. SEND OTP API
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
        # Fallback for testing if SMTP Gmail App Password is not added yet
        return jsonify({
            "success": True, 
            "message": f"Testing Mode: OTP is {otp} (Add Gmail App Password in Render for Real Emails)", 
            "test_otp": otp
        })

# 2. VERIFY OTP API
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

# 3. SUPER INTELLIGENT AI CHAT ENGINE
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE Board')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science (PCM/PCB)')
    lang = data.get('lang', 'Hinglish')

    if not prompt:
        return jsonify({"success": False, "message": "Doubt/Question khali nahi ho sakta!"}), 400

    # INTELLIGENT BRAIN SYSTEM PROMPT
    system_instruction = f"""
    You are 'TicBull AI Engine v8.5', a world-class expert educator, exam topper mentor, and creator consultant created by Founder MrYuviYadav.
    
    Student Context:
    - Target Exam/Board: {board}
    - Class/Level: {cls}
    - Stream/Category: {stream}
    - Medium/Language: Answer strictly in {lang} with professional, encouraging tone.

    Your Behavior Rules:
    1. If student asks a doubt, give step-by-step, accurate, top-marks level answers.
    2. For BPSC/UPSC: Include Prelims facts + Mains Answer Writing Pointers + Bihar Special context if relevant.
    3. For Class 9-12 (PCM/PCB/Commerce): Explain core concepts, key formulas, and exam tips.
    4. For YouTube/Social Media Skills: Give practical hooks, SEO tags, algorithm tricks, and content scripts.
    5. Formatting: Use clear headings, bullet points, and bold text for readability.
    """

    full_prompt = f"{system_instruction}\n\nUser Question: {prompt}"

    try:
        if GEMINI_API_KEY:
            response = model.generate_content(full_prompt)
            reply_text = response.text
        else:
            reply_text = f"<b>[{board} | {cls} AI Engine]:</b><br><br>Aapke question <b>'{prompt}'</b> ka concept:<br>1. Key Concept & Formulas for {board}.<br>2. Step-by-step explanation.<br><br><i>(Note: Real Gemini API Key connect hote hi live AI deep answer aane lagega!)</i>"

        return jsonify({"success": True, "reply": reply_text})
    except Exception as e:
        return jsonify({"success": False, "message": f"AI Engine Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
