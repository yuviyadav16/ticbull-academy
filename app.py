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

# ==========================================
# 1. AUTHENTICATION & USER ACCOUNTS (1 Email = 1 Account)
# ==========================================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    name = data.get('name', 'Student')
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email aur password zaroori hai!"}), 400
        
    if not FIREBASE_URL:
        return jsonify({"success": False, "message": "Firebase Database connect nahi hai!"}), 500

    safe_email = sanitize_email(email)
    
    # Check if user already exists
    check_user = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json()
    if check_user:
        return jsonify({"success": False, "message": "Account already exists! Kripya Login karein."}), 400
        
    # Save new user
    user_data = {"name": name, "email": email, "password": password, "plan": "None"}
    requests.put(f"{FIREBASE_URL}/users/{safe_email}.json", json=user_data)
    
    return jsonify({"success": True, "message": "Account successfully ban gaya! Ab login karein."})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not FIREBASE_URL:
        return jsonify({"success": False, "message": "Database error!"}), 500

    safe_email = sanitize_email(email)
    user_data = requests.get(f"{FIREBASE_URL}/users/{safe_email}.json").json()
    
    if not user_data:
        return jsonify({"success": False, "message": "Account nahi mila! Pehle Register karein."}), 404
        
    if user_data.get('password') != password:
        return jsonify({"success": False, "message": "Galat Password!"}), 401
        
    token = str(random.randint(10000000, 99999999))
    return jsonify({"success": True, "message": "Login successful!", "token": token, "user": user_data})

# ==========================================
# 2. CHAT HISTORY SAVING & FETCHING
# ==========================================

@app.route('/api/save-chat', methods=['POST'])
def save_chat():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    chat_history = data.get('chat_history', []) # Frontend se poori chat array aayegi
    
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        requests.put(f"{FIREBASE_URL}/chats/{safe_email}.json", json=chat_history)
        return jsonify({"success": True, "message": "Chat saved securely!"})
    return jsonify({"success": False, "message": "Failed to save chat."}), 400

@app.route('/api/get-chat', methods=['POST'])
def get_chat():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    
    if email and FIREBASE_URL:
        safe_email = sanitize_email(email)
        chat_data = requests.get(f"{FIREBASE_URL}/chats/{safe_email}.json").json()
        if chat_data:
            return jsonify({"success": True, "chat_history": chat_data})
    return jsonify({"success": True, "chat_history": []})

# ==========================================
# 3. AI CHAT ENGINE (Master Interactive Teacher)
# ==========================================

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    board = data.get('board', 'CBSE Board')
    cls = data.get('class', 'Class 12')
    stream = data.get('stream', 'Science')
    lang = data.get('lang', 'Hinglish')
    student_name = data.get('student_name', 'Mere Pyare Student') 
    
    if not prompt:
        return jsonify({"success": False, "message": "Question empty nahi ho sakta!"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "message": "API Key missing!"}), 500
        
    system_instruction = f"""Tu TicBull Academy ka Main, Akela aur sabse Intelligent Teacher hai. Tujhe MrYuviYadav ne banaya hai.
Student Name: {student_name}
Active Purchased Plan: {board} {cls} {stream}
Language: {lang}

STRICT RULES:
1. INTERACTIVE TEACHING: Lamba bookish text mat chaapna. Concept ko step-by-step, bullet points me aur easy examples se samjhao.
2. PERSONAL CONNECTION: Student ko beech-beech me uske naam ({student_name}) se bulao. 
3. CROSS-CLASS STRICTNESS (UPSELL): Agar student active plan ({cls}) ke bahar ka pooche, toh 2 line ka quick revision do aur bolo: "Detail me padhne ke liye aapko TicBull Academy ka wo specific batch buy karna padega. 🚀"
4. IDENTITY: Tu sirf 'TicBull Teacher' hai. Google, Gemini, AI word use nahi karna."""
    
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
            return jsonify({"success": False, "message": f"AI Error: {res_data['error'].get('message')}"}), 500
        else:
            return jsonify({"success": False, "message": "API Response Error"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500

@app.route('/')
def home():
    return "TicBull Secure Database, Auth & AI Engine is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
