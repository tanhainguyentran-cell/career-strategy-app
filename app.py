import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import date
import PyPDF2
import re

# ==========================================
# CẤU HÌNH GIAO DIỆN EXECUTIVE LUXURY
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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# HỆ THỐNG XÁC THỰC FIREBASE
# ==========================================
FIREBASE_WEB_API_KEY = "AIzaSyD00faEnc-wexp9f3UIdfSJFrMZwNOFm7A"

def firebase_auth(email, password, is_signup=False):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}" if is_signup else f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    try:
        res = requests.post(endpoint, headers={'Content-Type': 'application/json'}, data=payload)
        return res.json()
    except Exception as e: return {"error": {"message": str(e)}}

if 'user_token' not in st.session_state: st.session_state.user_token = None
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        "step": 1, "industry": "", "company": "", "framework_used": "",
        "opportunities": [], "threats": [], "company_strengths": [], "company_weaknesses": [],
        "personal_strengths": [], "personal_weaknesses": [], "tows": {"SO": "", "WT": ""}, "smart_goals": [], "file_content": ""
    }

# ==========================================
# XỬ LÝ AI & FILE
# ==========================================
def ask_ai(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Sửa lỗi 404 bằng cách dùng tên model chuẩn
        res = model.generate_content(prompt).text
        json_match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(json_match.group(0)) if json_match else None
    except Exception as e: st.error(f"Lỗi AI: {e}"); return None

def doc_file(file):
    if file.name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() for page in reader.pages)
    return file.read().decode("utf-8")

# --- LUỒNG AUTH ---
if not st.session_state.user_token:
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>HỆ THỐNG CHIẾN LƯỢC</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["ĐĂNG NHẬP", "ĐĂNG KÝ"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email"); p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("TRUY CẬP", type="primary"):
                res = firebase_auth(e, p)
                if "idToken" in res: st.session_state.user_token = res["idToken"]; st.session_state.user_email = res["email"]; st.rerun()
                else: st.error("Sai thông tin đăng nhập.")
    with t2:
        with st.form("signup"):
            e_s = st.text_input("Email"); p_s = st.text_input("Mật khẩu (6 ký tự)", type="password")
            if st.form_submit_button("TẠO TÀI KHOẢN", type="primary"):
                res = firebase_auth(e_s, p_s, is_signup=True)
                if "idToken" in res: st.success("Đăng ký thành công! Hãy quay lại tab Đăng nhập.")
                else: st.error("Lỗi đăng ký.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# ==========================================
# WIZARD APP CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>EXECUTIVE</h2>", unsafe_allow_html=True)
    st.write(f"👤 {st.session_state.user_email}")
    if st.button("ĐĂNG XUẤT"): st.session_state.user_token = None; st.rerun()
    st.markdown("---")
    api_key = st.text_input("API Key (Gemini):", type="password")
    uploaded = st.file_uploader("Nạp JD/Báo cáo (PDF/TXT)", type=["pdf", "txt"])
    if uploaded:
        st.session_state.app_state["file_content"] = doc_file(uploaded)
        st.success("Tài liệu đã được xác thực.")
        st.markdown("<div class='magic-btn'>", unsafe_allow_html=True)
        if st.button("✨ TỰ ĐỘNG PHÂN TÍCH CHUYÊN SÂU"):
            if not api_key: st.error("Cần API Key.")
            else:
                with st.spinner("AI đang bóc tách chiến lược..."):
                    prompt = f"Phân tích tài liệu sau: {st.session_state.app_state['file_content'][:3000]}. Trả về JSON: {{'company': '...', 'industry': '...', 'framework_used': '...', 'opportunities': ['...'], 'threats': ['...'], 'company_strengths': ['...'], 'company_weaknesses': ['...'], 'personal_strengths': ['...'], 'personal_weaknesses': ['...'], 'tows_so': '...', 'tows_wt': '...', 'smart_goals': ['...']}}"
                    data = ask_ai(prompt, api_key)
                    if data:
                        st.session_state.app_state.update(data)
                        st.session_state.app_state["tows"] = {"SO": data.get("tows_so", ""), "WT": data.get("tows_wt", "")}
                        st.success("Hoàn tất! Hãy nhấn 'Tiếp Tục' để xem chi tiết.")
        st.markdown("</div>", unsafe_allow_html=True)

# Điều hướng Wizard
step = st.session_state.app_state["step"]
names = ["I. RADAR", "II. DNA", "III. NĂNG LỰC", "IV. TOWS", "V. BÁO CÁO"]
indicator = "".join([f"<span class='{'active' if i+1==step else ''}'>{n}</span> &nbsp;&nbsp; " for i, n in enumerate(names)])
st.markdown(f"<div class='step-indicator'>{indicator}</div>", unsafe_allow_html=True)

# Nội dung từng bước
if step == 1:
    st.markdown("<div class='app-card'><h2>I. Radar Thị Trường (Vĩ mô)</h2><p>Phân tích PESTLE để tìm Cơ hội (O) và Thách thức (T).</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<h4>🟢 Cơ hội (O)</h4>", unsafe_allow_html=True); st.write("\n".join([f"- {o}" for o in st.session_state.app_state["opportunities"]]))
    with c2: st.markdown("<h4>🔴 Thách thức (T)</h4>", unsafe_allow_html=True); st.write("\n".join([f"- {t}" for t in st.session_state.app_state["threats"]]))

elif step == 2:
    st.markdown("<div class='app-card'><h2>II. DNA Doanh Nghiệp (VRIO)</h2><p>Đánh giá Điểm mạnh (S) và Điểm yếu (W) của tổ chức.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<h4>💪 Điểm mạnh DN</h4>", unsafe_allow_html=True); st.write("\n".join([f"- {s}" for s in st.session_state.app_state["company_strengths"]]))
    with c2: st.markdown("<h4>📉 Điểm yếu DN</h4>", unsafe_allow_html=True); st.write("\n".join([f"- {w}" for w in st.session_state.app_state["company_weaknesses"]]))

elif step == 3:
    st.markdown("<div class='app-card'><h2>III. Bản Đồ Năng Lực (STAR)</h2><p>Đối chiếu kỹ năng cá nhân với yêu cầu công việc.</p></div>", unsafe_allow_html=True)
    st.info(f"📌 Framework áp dụng: {st.session_state.app_state['framework_used']}")
    c1, c2 = st.columns(2)
    with c1: st.markdown("<h4>🌟 Thế mạnh cá nhân</h4>", unsafe_allow_html=True); st.write("\n".join([f"- {s}" for s in st.session_state.app_state["personal_strengths"]]))
    with c2: st.markdown("<h4>⚠️ Điểm cần cải thiện</h4>", unsafe_allow_html=True); st.write("\n".join([f"- {w}" for w in st.session_state.app_state["personal_weaknesses"]]))

elif step == 4:
    st.markdown("<div class='app-card'><h2>IV. Ma Trận Chiến Lược TOWS</h2></div>", unsafe_allow_html=True)
    st.markdown("<h4>Chiến lược Tấn công (SO)</h4>", unsafe_allow_html=True); st.write(st.session_state.app_state["tows"]["SO"])
    st.markdown("<h4>Chiến lược Phòng thủ (WT)</h4>", unsafe_allow_html=True); st.write(st.session_state.app_state["tows"]["WT"])

elif step == 5:
    st.markdown(f"<div class='app-card' style='text-align: center;'><h1>BÁO CÁO: {st.session_state.app_state['company'].upper()}</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='app-card'><h3>Lộ trình SMART</h3>", unsafe_allow_html=True)
    for g in st.session_state.app_state["smart_goals"]: st.write(f"📍 {g}")
    st.markdown("</div>", unsafe_allow_html=True)

# Điều hướng
st.markdown("---")
b1, b2, b3 = st.columns([2, 6, 2])
if step > 1:
    if b1.button("← QUAY LẠI"): st.session_state.app_state["step"] -= 1; st.rerun()
if step < 5:
    if b3.button("TIẾP TỤC →", type="primary"): st.session_state.app_state["step"] += 1; st.rerun()
