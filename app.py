import streamlit as st
import requests
import json
from datetime import date
import PyPDF2
import re

# ==========================================
# CẤU HÌNH GIAO DIỆN EXECUTIVE MINIMALISM
# ==========================================
st.set_page_config(page_title="Executive Strategy Wizard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A1A1A; }
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif; color: #0F172A; letter-spacing: -0.5px; }
    .app-card { background: #FFFFFF; padding: 2.5rem; border-radius: 4px; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.04); margin-bottom: 2rem; border: 1px solid #F0F0F0; border-top: 3px solid #D4AF37; }
    .auth-container { max-width: 450px; margin: 4rem auto; padding: 3rem 2rem; background: white; border-radius: 4px; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border-top: 3px solid #D4AF37; }
    .stButton>button { border-radius: 2px !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.8rem !important; transition: all 0.4s ease; border: 1px solid #1A1A1A !important; }
    .stButton>button[kind="primary"] { background-color: #1A1A1A !important; color: #FFFFFF !important; padding: 0.8rem 2rem; }
    .stButton>button[kind="primary"]:hover { background-color: #D4AF37 !important; border-color: #D4AF37 !important; }
    .magic-btn>button { background-color: transparent !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important; width: 100%; font-weight: bold !important; }
    .magic-btn>button:hover { background-color: #D4AF37 !important; color: #FFFFFF !important; }
    .step-indicator { text-align: center; margin-bottom: 2rem; font-family: 'Playfair Display', serif; color: #888; letter-spacing: 2px; }
    .step-indicator span.active { color: #D4AF37; font-weight: bold; border-bottom: 2px solid #D4AF37; padding-bottom: 5px; }
    textarea { background-color: #FCFCFC !important; border-left: 3px solid #D4AF37 !important; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH XÁC THỰC FIREBASE & AI API
# ==========================================
FIREBASE_KEY = "AIzaSyD00faEnc-wexp9f3UIdfSJFrMZwNOFm7A"

def firebase_auth(email, password, is_signup=False):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{'signUp' if is_signup else 'signInWithPassword'}?key={FIREBASE_KEY}"
    try:
        res = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
        return res.json()
    except: return {"error": {"message": "Lỗi kết nối"}}

def call_gemini_api(prompt, api_key):
    # Sử dụng endpoint v1 ổn định thay vì v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        res_json = res.json()
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except Exception as e:
        st.error(f"Lỗi AI: {str(e)}")
        return None

# ==========================================
# STATE MANAGEMENT
# ==========================================
if 'user_token' not in st.session_state: st.session_state.user_token = None
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        "step": 1, "industry": "", "company": "", "framework": "",
        "opportunities": [], "threats": [], "company_s": [], "company_w": [],
        "personal_s": [], "personal_w": [], "tows": {"SO": "", "WT": ""}, "smart": [], "file": ""
    }

# --- AUTH UI ---
if not st.session_state.user_token:
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>EXECUTIVE STRATEGY</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["ĐĂNG NHẬP", "ĐĂNG KÝ"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email"); p = st.text_input("Password", type="password")
            if st.form_submit_button("TRUY CẬP", type="primary"):
                res = firebase_auth(e, p)
                if "idToken" in res: st.session_state.user_token = res["idToken"]; st.session_state.user_email = res["email"]; st.rerun()
                else: st.error("Thông tin không chính xác.")
    with t2:
        with st.form("signup"):
            e_s = st.text_input("Email"); p_s = st.text_input("Mật khẩu (6 ký tự)", type="password")
            if st.form_submit_button("TẠO TÀI KHOẢN", type="primary"):
                res = firebase_auth(e_s, p_s, is_signup=True)
                if "idToken" in res: st.success("Đã đăng ký! Vui lòng Đăng nhập.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# ==========================================
# WIZARD UI
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37; margin-bottom: 0;'>EXECUTIVE</h2>", unsafe_allow_html=True)
    st.write(f"👤 {st.session_state.user_email}")
    if st.button("ĐĂNG XUẤT", use_container_width=True): st.session_state.user_token = None; st.rerun()
    st.markdown("---")
    api_key = st.text_input("Gemini API Key:", type="password")
    uploaded = st.file_uploader("Nạp JD/Báo cáo (PDF)", type=["pdf"])
    if uploaded:
        reader = PyPDF2.PdfReader(uploaded)
        st.session_state.app_state["file"] = "".join(p.extract_text() for p in reader.pages)
        st.success("Tài liệu đã được xác thực.")
        st.markdown("<div class='magic-btn'>", unsafe_allow_html=True)
        if st.button("✨ TỰ ĐỘNG PHÂN TÍCH CHUYÊN SÂU"):
            if not api_key: st.error("Cần API Key.")
            else:
                with st.spinner("AI đang giải mã chiến lược..."):
                    prompt = f"""
                    Phân tích tài liệu: {st.session_state.app_state['file'][:3500]}
                    Hãy đóng vai Giám đốc Chiến lược của McKinsey. Phân tích thật CHI TIẾT nhưng trình bày ĐƠN GIẢN.
                    Trả về JSON: {{
                        'company': '...', 'industry': '...', 'framework': '...',
                        'opportunities': ['Cơ hội 1: [Giải thích]', 'Cơ hội 2: [Giải thích]'],
                        'threats': ['Thách thức 1: [Giải thích]', 'Thách thức 2: [Giải thích]'],
                        'company_s': ['Điểm mạnh 1: [Giải thích]', 'Điểm mạnh 2: [Giải thích]'],
                        'company_w': ['Điểm yếu 1: [Giải thích]', 'Điểm yếu 2: [Giải thích]'],
                        'personal_s': ['Kỹ năng 1: [Tại sao JD cần]', 'Kỹ năng 2: [Tại sao JD cần]'],
                        'personal_w': ['Lỗ hổng 1: [Cách khắc phục]', 'Lỗ hổng 2: [Cách khắc phục]'],
                        'tows_so': 'Chiến lược SO: ...', 'tows_wt': 'Chiến lược WT: ...',
                        'smart': ['Mục tiêu 1: ...', 'Mục tiêu 2: ...']
                    }}
                    """
                    data = call_gemini_api(prompt, api_key)
                    if data:
                        st.session_state.app_state.update(data)
                        st.session_state.app_state["tows"] = {"SO": data.get("tows_so", ""), "WT": data.get("tows_wt", "")}
                        st.success("Hoàn tất! Vui lòng nhấn 'Tiếp Tục'.")
        st.markdown("</div>", unsafe_allow_html=True)

# Điều hướng Wizard
step = st.session_state.app_state["step"]
names = ["I. RADAR", "II. DNA", "III. NĂNG LỰC", "IV. TOWS", "V. REPORT"]
indicator_html = "<div class='step-indicator'>"
for i, name in enumerate(names, 1):
    active_class = "class='active'" if i == step else ""
    indicator_html += f"<span {active_class}>{name}</span> &nbsp;&nbsp;&nbsp; "
indicator_html += "</div>"
st.markdown(indicator_html, unsafe_allow_html=True)

# --- NỘI DUNG TỪNG BƯỚC ---
if step == 1:
    st.markdown("<div class='app-card'><h2>I. Radar Thị Trường (Vĩ mô)</h2><p>Phân tích PESTLE để tìm Cơ hội và Thách thức.</p></div>", unsafe_allow_html=True)
    st.session_state.app_state['industry'] = st.text_input("Ngành nghề mục tiêu:", st.session_state.app_state['industry'])
    st.session_state.app_state['company'] = st.text_input("Công ty mục tiêu:", st.session_state.app_state['company'])
    c1, c2 = st.columns(2)
    with c1: st.markdown("<h4>🟢 Cơ hội (Opportunities)</h4>", unsafe_allow_html=True); st.text_area("O:", "\n\n".join(st.session_state.app_state["opportunities"]), height=300)
    with c2: st.markdown("<h4>🔴 Thách thức (Threats)</h4>", unsafe_allow_html=True); st.text_area("T:", "\n\n".join(st.session_state.app_state["threats"]), height=300)

elif step == 2:
    st.markdown("<div class='app-card'><h2>II. DNA Doanh Nghiệp (VRIO)</h2><p>Phân tích nội tại tổ chức mục tiêu.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<h4>💪 Điểm mạnh DN (Strengths)</h4>", unsafe_allow_html=True); st.text_area("S:", "\n\n".join(st.session_state.app_state["company_s"]), height=300)
    with c2: st.markdown("<h4>📉 Điểm yếu DN (Weaknesses)</h4>", unsafe_allow_html=True); st.text_area("W:", "\n\n".join(st.session_state.app_state["company_w"]), height=300)

elif step == 3:
    st.markdown("<div class='app-card'><h2>III. Bản Đồ Năng Lực Cá Nhân (STAR)</h2><p>Định tuyến khung năng lực.</p></div>", unsafe_allow_html=True)
    st.info(f"📌 Framework áp dụng: {st.session_state.app_state['framework']}")
    c1, c2 = st.columns(2)
    with c1: st.markdown("<h4>🌟 Thế mạnh cá nhân</h4>", unsafe_allow_html=True); st.text_area("S:", "\n\n".join(st.session_state.app_state["personal_s"]), height=300)
    with c2: st.markdown("<h4>⚠️ Điểm cần bổ trợ</h4>", unsafe_allow_html=True); st.text_area("W:", "\n\n".join(st.session_state.app_state["personal_w"]), height=300)

elif step == 4:
    st.markdown("<div class='app-card'><h2>IV. Ma Trận Chiến Lược TOWS</h2></div>", unsafe_allow_html=True)
    st.markdown("<h4>🚀 Chiến lược Tấn công (SO)</h4>", unsafe_allow_html=True); st.text_area("SO:", st.session_state.app_state["tows"]["SO"], height=150)
    st.markdown("<h4>🛡️ Chiến lược Phòng thủ (WT)</h4>", unsafe_allow_html=True); st.text_area("WT:", st.session_state.app_state["tows"]["WT"], height=150)

elif step == 5:
    st.markdown(f"<div class='app-card' style='text-align: center;'><h1>STRATEGY REPORT: {st.session_state.app_state['company'].upper()}</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='app-card'><h3>Kế hoạch thực thi SMART</h3>", unsafe_allow_html=True)
    for g in st.session_state.app_state["smart"]: st.markdown(f"<p style='font-size: 1.1rem; border-bottom: 1px solid #EEE; padding: 10px 0;'>📍 {g}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Điều hướng
st.markdown("---")
b1, b2, b3 = st.columns([2, 6, 2])
if step > 1 and b1.button("← QUAY LẠI"): st.session_state.app_state["step"] -= 1; st.rerun()
if step < 5 and b3.button("TIẾP TỤC →", type="primary"): st.session_state.app_state["step"] += 1; st.rerun()
