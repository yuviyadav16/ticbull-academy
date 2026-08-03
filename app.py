import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Keys from Vercel
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ticbull.support@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "").rstrip('/')
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

otp_store = {}

def sanitize_email(email):
    return email.replace('.', '_').replace('@', '_at_')

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
        return jsonify({"success": True, "message": f"OTP sent to {email}"})
    return jsonify({"success": False, "message": "Email error!"}), 500

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
    return jsonify({"success": False, "message": "Galat OTP!"}), 400

@app.route('/api/check-session', methods=['POST'])
def check_session():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    token = data.get('token', '')
    device_id = data.get('device_id', '')
    
    if not FIREBASE_URL:
        return jsonify({"success": True, "active": True})
        
    safe_email = sanitize_email(email)
    res = requests.get(f"{FIREBASE_URL}/sessions/{safe_email}.json")
    if res.status_code == 200 and res.json():
        db_session = res.json()
        if db_session.get("token") == token and db_session.get("device_id") == device_id:
            return jsonify({"success": True, "active": True})
            
    return jsonify({"success": True, "active": False, "message": "Logged in from another device!"})

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    data = request.get_json() or {}
    amount = data.get('amount', 0)
    
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return jsonify({"success": False, "message": "Payment Gateway setup pending."}), 500
        
    try:
        url = "https://api.razorpay.com/v1/orders"
        payload = {
            "amount": amount * 100,
            "currency": "INR",
            "receipt": f"receipt_{random.randint(1000,9999)}"
        }
        res = requests.post(url, json=payload, auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        if res.status_code == 200:
            return jsonify({"success": True, "order_id": res.json()["id"], "key": RAZORPAY_KEY_ID})
        return jsonify({"success": False, "message": "Order creation failed"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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
        return jsonify({"success": False, "message": "API Key missing in Vercel Environment Variables!"}), 500
        
    # YAHAN HUMNE AI KO SMART AUR FRIENDLY BANAYA HAI 👇
    system_instruction = f"""Tu TicBull Academy ka ek friendly, smart aur helpful teacher hai. Tujhe MrYuviYadav ne banaya hai.
Student {board} {cls} {stream} ka hai aur wo {lang} language me padhna chahta hai.

Follow these STRICT rules:
1. NO REPETITION: Baar-baar apna introduction (jaise "Hello Beta", "Main aapka teacher hu", "Mujhe MrYuviYadav ne banaya hai") kabhie mat dena. Seedha to-the-point question ka answer do.
2. TONE: Student ko motivate karo, hamesha happy aur friendly raho. Emojis ka use karo taaki padhai boring na lage.
3. CLEAR & SHORT: Answers ko zyada lamba mat kheencho. Bullet points me samjhao.
4. IDENTITY: Kabhie mat kehna ki tu AI, Google ya Gemini hai. Khud ko hamesha 'TicBull' bolna.
5. OUT OF SYLLABUS: Agar sawal study se related nahi hai, toh politely mana kar do."""
    
    full_prompt = f"{system_instruction}\n\nStudent Question: {prompt}"
    
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        
        # Superfast Latest Free Model
        model_name = "gemini-flash-latest"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        res_data = response.json()
        
        if "candidates" in res_data:
            reply_text = res_data['candidates'][0]['content']['parts'][0]['text']
            reply_text = reply_text.replace("Gemini", "TicBull Engine").replace("Google", "TicBull").replace("gemini", "ticbull")
            return jsonify({"success": True, "reply": reply_text})
        elif "error" in res_data:
            err_msg = res_data["error"].get("message", "API Error")
            return jsonify({"success": False, "message": f"AI Error: {err_msg}"}), 500
        else:
            return jsonify({"success": False, "message": f"API Response Error: {str(res_data)}"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "TicBull Database & Super Smart AI Engine is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
