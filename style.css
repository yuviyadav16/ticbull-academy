:root {
    --bg-color: #030712;
    --card-bg: rgba(15, 23, 42, 0.95);
    --accent-color: #2563eb;
    --accent-glow: rgba(37, 99, 235, 0.45);
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border-color: rgba(255, 255, 255, 0.12);
    --success-color: #10b981;
    --gold-color: #f59e0b;
    --chat-bg: #020617;
    --input-bg: #0f172a;
    --danger-color: #ef4444;
}
body.light-theme {
    --bg-color: #f1f5f9; --card-bg: #ffffff; --text-main: #0f172a;
    --text-muted: #64748b; --border-color: #cbd5e1; --chat-bg: #f8fafc; --input-bg: #ffffff;
}
* { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
html, body { height: 100%; width: 100%; overflow: hidden; background: var(--bg-color); color: var(--text-main); transition: background 0.3s, color 0.3s; }
body { display:flex; flex-direction:column; }
#custom-toast { position: fixed; top: -100px; left: 50%; transform: translateX(-50%); background: var(--card-bg); color: var(--text-main); border: 1px solid var(--accent-color); padding: 12px 24px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; gap: 12px; font-size: 13.5px; font-weight: 600; transition: top 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
#custom-toast.show { top: 30px; }
.toast-icon.success { color: var(--success-color); }
.toast-icon.error { color: var(--danger-color); }
#splash-screen { position: fixed; top:0; left:0; width:100%; height:100%; background: radial-gradient(circle at center, #0b1329 0%, #020617 100%); display:flex; flex-direction:column; justify-content:center; align-items:center; z-index:9999; transition: opacity 0.8s ease, visibility 0.8s ease; padding: 20px; }
.splash-logo-container { position: relative; width: 130px; height: 110px; display:flex; justify-content:center; align-items:center; }
.splash-logo-glow { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: radial-gradient(circle, rgba(37, 99, 235, 0.9) 0%, rgba(0,0,0,0) 70%); filter: blur(20px); animation: pulseGlow 2.5s infinite alternate ease-in-out; }
.splash-logo { position: relative; width: 105px; height: 105px; border-radius: 50%; background: #000; border: 2px solid rgba(37, 99, 235, 0.5); display:flex; justify-content:center; align-items:center; overflow:hidden; box-shadow: 0 0 35px var(--accent-glow); }
.splash-logo img { width:90%; height:90%; object-fit:contain; }
.splash-title { margin-top:20px; font-size:26px; font-weight:800; letter-spacing:1px; color:#fff; text-shadow:0 0 15px rgba(255,255,255,0.3); }
.developer-tag { margin-top:6px; font-size:13px; color: var(--accent-color); font-weight:700; letter-spacing:0.5px; }
.progress-bar-container { width: 180px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 25px; overflow: hidden; }
.progress-bar { width: 0%; height: 100%; background: linear-gradient(90deg, var(--accent-color), #f59e0b); animation: loadProgress 3.5s linear forwards; }
@keyframes pulseGlow { 0% { transform: scale(0.85); opacity: 0.5; } 100% { transform: scale(1.2); opacity: 0.95; } }
@keyframes loadProgress { 0% { width: 0%; } 100% { width: 100%; } }
@keyframes popIn { 0% { opacity:0; transform:scale(0.9) translateY(5px); } 100% { opacity:1; transform:scale(1) translateY(0); } }
.btn-primary { width:100%; background: var(--accent-color); color:#fff; font-weight:700; padding:13px; border:none; border-radius:12px; cursor:pointer; font-size:14px; letter-spacing:0.5px; box-shadow:0 8px 20px var(--accent-glow); transition:0.2s; margin-top:8px; }
.btn-primary:active { transform:scale(0.98); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-success { background: var(--success-color); box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4); }
.btn-danger { background: var(--danger-color); box-shadow:0 8px 20px rgba(239, 68, 68, 0.4); }
.input-group { position:relative; margin-bottom:12px; text-align:left; }
.input-group i.left-icon { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:14px; }
.input-group input, .input-group select { width:100%; background:var(--input-bg); border:1px solid var(--border-color); color:var(--text-main); padding:12px 40px; border-radius:12px; font-size:14px; outline:none; transition:0.3s; }
.input-group input:focus { border-color:var(--accent-color); box-shadow: 0 0 12px var(--accent-glow); }
.screen { display:none; flex-direction:column; height:100%; max-width:850px; margin:0 auto; width:100%; padding:10px; overflow:hidden; position:relative; }
.screen.active { display:flex; }
.auth-container { display:flex; flex-direction:column; align-items:center; justify-content:center; flex:1; padding:20px; width:100%; overflow-y:auto; }
.auth-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius:24px; padding:28px 22px; width:100%; max-width:420px; box-shadow:0 20px 50px rgba(0,0,0,0.5); text-align:center; position: relative; }
.brand-header { display:flex; flex-direction:column; align-items:center; margin-bottom:18px; }
.brand-icon-box { width:80px; height:80px; border-radius:50%; background:#000; border:2px solid rgba(37, 99, 235, 0.4); display:flex; justify-content:center; align-items:center; margin-bottom:12px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); overflow:hidden; }
.brand-icon-box img { width:90%; height:90%; object-fit:contain; }
.auth-tabs { display:flex; background:var(--input-bg); padding:4px; border-radius:12px; border:1px solid var(--border-color); margin-bottom:16px; }
.auth-tab { flex:1; padding:10px; font-size:13px; font-weight:600; color:var(--text-muted); border-radius:8px; cursor:pointer; transition:0.3s; }
.auth-tab.active { background:var(--accent-color); color:#fff; }
.signup-extra-fields { display:none; flex-direction:column; gap:0px; }
.forgot-link { font-size:11.5px; color:var(--accent-color); text-decoration:none; display:block; text-align:right; margin:-6px 0 12px 0; cursor:pointer; }
.modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:2000; display:none; justify-content:center; align-items:center; padding:16px; }
.modal-card { background:var(--card-bg); border:1px solid var(--border-color); border-radius:20px; padding:22px; max-width:480px; width:100%; text-align:center; position:relative; max-height:92vh; display:flex; flex-direction:column; animation: popIn 0.3s ease; }
.batches-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; background:var(--card-bg); padding:12px 16px; border-radius:16px; border:1px solid var(--border-color); flex-shrink:0; }
.header-logo { width:38px; height:38px; border-radius:50%; background:#000; border:1px solid rgba(255,255,255,0.2); display:flex; justify-content:center; align-items:center; overflow:hidden; }
.header-logo img { width:90%; height:90%; object-fit:contain; }
.menu-btn { background:none; border:none; color:var(--text-main); font-size:18px; cursor:pointer; padding:6px; }
.category-scroll-bar { display:flex; gap:8px; overflow-x:auto; padding-bottom:10px; margin-bottom:10px; scrollbar-width:none; flex-shrink:0; }
.category-scroll-bar::-webkit-scrollbar { display:none; }
.cat-chip { background:var(--input-bg); border:1px solid var(--border-color); color:var(--text-muted); padding:7px 14px; border-radius:20px; font-size:11.5px; font-weight:700; white-space:nowrap; cursor:pointer; transition:0.2s; }
.cat-chip.active { background:var(--accent-color); color:#fff; border-color:var(--accent-color); box-shadow:0 4px 15px var(--accent-glow); }
.search-batches-box input { padding-left: 42px; }
#batchesContainer { flex:1; overflow-y:auto; padding-bottom:20px; display:flex; flex-direction:column; gap:14px; }
.batch-card { background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)); border: 1px solid rgba(37, 99, 235, 0.3); border-radius: 18px; padding: 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); transition: 0.3s; cursor:pointer; }
.batch-card:hover { border-color: var(--accent-color); transform: translateY(-2px); }
.batch-tag { background: rgba(16, 185, 129, 0.15); color: var(--success-color); font-size: 10.5px; font-weight: 700; padding: 4px 10px; border-radius: 20px; display: inline-block; margin-bottom: 8px; border: 1px solid rgba(16, 185, 129, 0.3); }
.batch-title { font-size: 16.5px; font-weight: 800; color: #fff; margin-bottom: 6px; line-height:1.3; }
.batch-desc { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; line-height:1.4; }
.batch-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 12px; }
.batch-price { font-size: 14.5px; font-weight: 800; color: var(--success-color); }
.btn-view-batch { background: var(--accent-color); color: #fff; border: none; padding: 8px 16px; border-radius: 10px; font-size: 11.5px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 15px var(--accent-glow); }
.teacher-list-container { max-height: 250px; overflow-y: auto; text-align: left; background: var(--chat-bg); border-radius: 12px; padding: 10px; border: 1px solid var(--border-color); margin: 12px 0; }
.teacher-list-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.teacher-list-item:last-child { border-bottom: none; }
.teacher-avatar-mini { width: 36px; height: 36px; border-radius: 50%; border: 2px solid var(--gold-color); object-fit: cover; }
.t-sub { font-size: 12.5px; font-weight: 700; color: var(--text-main); }
.t-name { font-size: 11px; color: var(--text-muted); }
.tier-card-option { background: var(--chat-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px; margin-bottom: 10px; text-align: left; cursor: pointer; transition: 0.2s; }
.tier-card-option:hover, .tier-card-option.selected { border-color: var(--accent-color); background: rgba(37, 99, 235, 0.15); }
.tier-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.tier-name { font-size: 14px; font-weight: 800; color: #fff; }
.tier-price { font-size: 14px; font-weight: 800; color: #fff; }
.tier-desc { font-size: 11px; color: var(--text-muted); line-height: 1.4; }
.dash-banner { background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(15, 23, 42, 0.8)); border: 1px solid var(--accent-color); border-radius: 16px; padding: 16px; margin-bottom: 14px; display:flex; justify-content:space-between; align-items:center; flex-shrink:0; }
.subject-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 12px; overflow-y: auto; padding-bottom:20px; }
.subject-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px 12px; text-align: center; cursor: pointer; transition: 0.3s; display:flex; flex-direction:column; align-items:center; gap:8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
.subject-card:hover { border-color: var(--accent-color); transform: translateY(-3px); }
.subject-icon-box { width: 50px; height: 50px; border-radius: 12px; background: rgba(37, 99, 235, 0.1); display:flex; justify-content:center; align-items:center; font-size:24px; color:var(--accent-color); margin-bottom:4px; }
.subject-card-title { font-size: 13.5px; font-weight: 700; color: var(--text-main); }
.subject-card-teacher { font-size: 11px; color: var(--gold-color); font-weight:600; display:flex; align-items:center; gap:4px; }
.chat-header-clean { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:var(--card-bg); border-bottom:1px solid var(--border-color); flex-shrink:0; }
.chat-header-left { display:flex; align-items:center; gap:12px; }
.back-btn { background:none; border:none; color:var(--text-main); font-size:18px; cursor:pointer; }
.chat-teacher-avatar { width:42px; height:42px; border-radius:50%; border:2px solid var(--success-color); object-fit:cover; }
.chat-title-info { display:flex; flex-direction:column; }
.chat-subject-name { font-size:15px; font-weight:800; color:#fff; }
.chat-teacher-name { font-size:11.5px; color:var(--text-muted); }
.chat-3dot-menu { position:relative; }
.chat-dropdown { display:none; position:absolute; right:0; top:30px; background:var(--card-bg); border:1px solid var(--border-color); border-radius:12px; width:180px; box-shadow:0 10px 30px rgba(0,0,0,0.6); z-index:100; overflow:hidden; }
.chat-dropdown.show { display:block; animation:popIn 0.2s ease; }
.chat-drop-item { padding:12px 16px; font-size:13px; color:var(--text-main); display:flex; align-items:center; gap:10px; border-bottom:1px solid var(--border-color); cursor:pointer; }
.chat-drop-item:hover { background:rgba(255,255,255,0.05); }
.chat-container { background:var(--chat-bg); padding:14px; flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:10px; }
.msg { padding:12px 15px; border-radius:16px; font-size:13.5px; line-height:1.5; max-width:88%; word-break: break-word; overflow-wrap: break-word; animation: popIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards; transform-origin: bottom left; }
.msg.user { background:var(--accent-color); color:#fff; align-self:flex-end; border-bottom-right-radius:4px; transform-origin: bottom right; }
.msg.ai { background:var(--card-bg); color:var(--text-main); border:1px solid var(--border-color); align-self:flex-start; border-bottom-left-radius:4px; width: 100%; max-width: 92%; }
.msg table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12.5px; }
.msg th, .msg td { border: 1px solid var(--border-color); padding: 8px; text-align: left; }
.msg th { background: rgba(37, 99, 235, 0.1); color: var(--accent-color); font-weight: 700; }
.msg-image { max-width:100%; border-radius:12px; margin-top:8px; border:1px solid var(--border-color); }
.chat-input-bar { display:flex; align-items:flex-end; background:var(--card-bg); border-top:1px solid var(--border-color); padding:10px 14px; gap:8px; flex-shrink:0; }
.chat-input-bar textarea { flex:1; background:var(--input-bg); border:1px solid var(--border-color); border-radius:16px; color:var(--text-main); padding:12px 14px; outline:none; font-size:13.5px; word-break: break-word; resize: none; max-height: 120px; overflow-y: auto; }
.action-icon-btn { background:rgba(255,255,255,0.06); color:var(--text-muted); border:1px solid var(--border-color); width:42px; height:42px; border-radius:12px; display:flex; justify-content:center; align-items:center; cursor:pointer; transition:0.2s; flex-shrink:0; }
.send-btn { background:var(--accent-color); color:#fff; border:none; width:42px; height:42px; border-radius:12px; display:flex; justify-content:center; align-items:center; cursor:pointer; flex-shrink:0; }
.ai-tools-menu { display:none; position:absolute; bottom:70px; left:14px; background:var(--card-bg); border:1px solid var(--border-color); border-radius:16px; padding:8px; box-shadow:0 15px 35px rgba(0,0,0,0.5); z-index:500; width:260px; flex-direction:column; gap:4px; }
.tool-btn { display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:10px; background:transparent; border:none; color:var(--text-main); font-size:12.5px; cursor:pointer; text-align:left; }
.tool-btn:hover { background:rgba(37, 99, 235, 0.1); color:var(--accent-color); }
#imagePreview { display:none; padding:6px 12px; background:var(--card-bg); border-radius:10px; font-size:12px; color:var(--accent-color); margin-bottom:8px; align-items:center; justify-content:space-between; flex-shrink:0; }
.drawer-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:1000; display:none; }
.drawer { position:fixed; top:0; left:-310px; width:310px; height:100%; background:var(--card-bg); border-right:1px solid var(--border-color); z-index:1001; transition:0.3s; padding:18px; display:flex; flex-direction:column; overflow-y:auto; }
.drawer.open { left:0; }
.drawer-header { display:flex; justify-content:space-between; align-items:center; padding-bottom:12px; border-bottom:1px solid var(--border-color); margin-bottom:12px; }
.profile-card { background:linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(245, 158, 11, 0.15)); border:1px solid var(--border-color); border-radius:16px; padding:14px; margin-bottom:14px; text-align:left; position:relative; }
.profile-header { display:flex; align-items:center; gap:12px; }
.profile-avatar-box { position:relative; width:46px; height:46px; }
.profile-avatar-img { width:100%; height:100%; border-radius:50%; object-fit:cover; border:2px solid var(--accent-color); }
.profile-avatar-initial { width:100%; height:100%; border-radius:50%; background:var(--accent-color); color:#fff; display:flex; justify-content:center; align-items:center; font-weight:800; font-size:18px; border:2px solid rgba(255,255,255,0.2); }
.drawer-item { padding:11px 12px; border-radius:10px; color:var(--text-main); font-size:12.5px; display:flex; align-items:center; gap:12px; cursor:pointer; margin-bottom:6px; transition:0.2s; }
.drawer-item:hover { background:rgba(255,255,255,0.06); }
.setting-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 13.5px; color: var(--text-main); text-align:left; }
.switch { position: relative; display: inline-block; width: 38px; height: 22px; flex-shrink:0; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--border-color); transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: var(--success-color); }
input:checked + .slider:before { transform: translateX(16px); }
.theme-circle { width: 24px; height: 24px; border-radius: 50%; display:inline-block; cursor:pointer; border:2px solid transparent; margin-left:6px; }
.theme-circle.active { border-color:#fff; transform:scale(1.1); }
.history-list { display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:300px; text-align:left; }
.history-item-block { background:var(--input-bg); border:1px solid var(--border-color); padding:10px 12px; border-radius:10px; font-size:12.5px; color:var(--text-main); }
.syllabus-task { display:flex; align-items:center; gap:10px; background:var(--chat-bg); padding:10px; border:1px solid var(--border-color); border-radius:10px; margin-bottom:6px; text-align:left; }
.syllabus-task input[type="checkbox"] { width:16px; height:16px; accent-color:var(--success-color); }
.syllabus-task.completed span { text-decoration: line-through; color:var(--text-muted); }
    </style>
