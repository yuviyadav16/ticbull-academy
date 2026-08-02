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
        return jsonify({"success": False, "message": "Email bhejne me error aayi! SMTP settings check karein."}), 500

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
        
    # STRICT PERSONA SYSTEM INSTRUCTION
    system_instruction = f"""Tu TicBull hai, ek real, intelligent aur helpful teacher. 
CRITICAL RULES JINHE KABHI NAHI TODNA HAI:
1. Agar koi puche ki tujhe kisne banaya hai, toh hamesha jawab de: 'Mujhe MrYuviYadav ne banaya hai aur main TicBull dwara powered hu.'
2. KABHI BHI mat bolna ki tu ek AI hai, LLM hai, ya Google/Gemini ne tujhe banaya hai. Agar koi puche toh bolna 'Main ek real intelligent teacher hu TicBull Academy ka'.
3. Har student ki 100% help karni hai ek human expert ki tarah.
4. Jawab {lang} bhasha me, {board} {cls} {stream} ke according de.
"""
    full_prompt = f"{system_instruction}\n\nQuestion: {prompt}"
    
    try:
        # Fixed API Endpoint Model
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()
        
        if "candidates" in res_data:
            reply_text = res_data['candidates'][0]['content']['parts'][0]['text']
            # White-labeling: Double check to remove Gemini from output
            reply_text = reply_text.replace("Gemini", "TicBull Engine").replace("Google", "TicBull")
            return jsonify({"success": True, "reply": reply_text})
        else:
            return jsonify({"success": False, "message": "TicBull AI Server busy hai, thodi der me try karein."}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": "Network Connection Error!"}), 500

@app.route('/')
def home():
    return "TicBull Backend is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
