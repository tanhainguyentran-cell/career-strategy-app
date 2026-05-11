import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import date
import PyPDF2
import re

# ==========================================
# CẤU HÌNH TRANG & CSS "EXECUTIVE LUXURY"
# ==========================================
st.set_page_config(page_title="Executive Strategy", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A1A1A; }
    .stApp { background-color: #FAFAFA; }
    
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif; color: #0F172A; letter-spacing: -0.5px; }
    
    .app-card { 
        background: #FFFFFF; padding: 3rem; border-radius: 4px; 
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.04); margin-bottom: 2rem; 
        border: 1px solid #F0F0F0; border-top: 3px solid #D4AF37; 
    }
    
    .auth-container {
        max-width: 450px; margin: 4rem auto; padding: 3rem 2rem;
        background: white; border-radius: 4px;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
        border-top: 3px solid #D4AF37; border-bottom: 3px solid #1A1A1A;
    }
    
    .stButton>button { 
        border-radius: 2px !important; font-weight: 500 !important; 
        text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.85rem !important;
        transition: all 0.4s ease; border: 1px solid #1A1A1A !important;
    }
    
    .stButton>button[kind="primary"] { 
        background-color: #1A1A1A !important; color: #FFFFFF !important; padding: 0.8rem 2rem;
    }
    .stButton>button[kind="primary"]:hover { 
        background-color: #D4AF37 !important; border-color: #D4AF37 !important; color: #FFFFFF !important;
    }
    
    .magic-btn>button { 
        background-color: transparent !important; color: #D4AF37 !important; 
        border: 1px solid #D4AF37 !important; padding: 1rem; width: 100%;
    }
    .magic-btn>button:hover { background-color: #D4AF37 !important; color: #FFFFFF !important; }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea { 
        border-radius: 2px; border: 1px solid #E5E7EB; padding: 0.8rem; font-family: 'Inter', sans-serif;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { border-color: #0F172A; box-shadow: none; }
    
    /* Progress bar steps */
    .step-indicator { text-align: center; margin-bottom: 2rem; font-family: 'Playfair Display', serif; color: #888; letter-spacing: 2px; }
    .step-indicator span.active { color: #D4AF37; font-weight: bold; border-bottom: 2px solid #D4AF37; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH FIREBASE
# ==========================================
FIREBASE_WEB_API_KEY = "AIzaSyD00faEnc-wexp9f3UIdfSJFrMZwNOFm7A"

def firebase_auth(email, password, is_signup=False):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}" if is_signup else f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    try:
        res = requests.post(endpoint, headers={'Content-Type': 'application/json'}, data=payload)
        return res.json()
    except Exception as e:
        return {"error": {"message": str(e)}}

# ==========================================
# STATE & HÀM AI 
# ==========================================
if 'user_token' not in st.session_state: st.session_state.user_token = None
if 'user_email' not in st.session_state: st.session_state.user_email = None

if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        "step": 1, "industry": "", "company": "", "framework_used": "",
        "opportunities": [], "threats": [], 
        "company_strengths": [], "company_weaknesses": [],
        "personal_strengths": [], "personal_weaknesses": [],
        "tows": {"SO": "", "ST": "", "WO": "", "WT": ""}, "smart_goals": [],
        "file_content": ""
    }

def hoi_ai_json(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        res = model.generate_content(prompt).text
        # Làm sạch JSON nếu AI bọc trong markdown
        res = res.replace("```json", "").replace("```", "").strip()
        json_match = re.search(r'\{.*\}', res, re.DOTALL)
        if json_match: return json.loads(json_match.group(0))
        return None
    except Exception as e:
        st.error(f"Lỗi AI: {e}")
        return None

def doc_file_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join(page.extract_text() for page in reader.pages)

# ==========================================
# LUỒNG XÁC THỰC (LOGIN / SIGNUP)
# ==========================================
if not st.session_state.user_token:
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0F172A;'>EXECUTIVE PORTAL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-family: Inter; letter-spacing: 1px;'>RESTRICTED ACCESS</p><br>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["ĐĂNG NHẬP", "ĐĂNG KÝ"])
    with tab_login:
        with st.form("login"):
            e_log = st.text_input("Email")
            p_log = st.text_input("Password", type="password")
            if st.form_submit_button("TRUY CẬP", type="primary"):
                res = firebase_auth(e_log, p_log, is_signup=False)
                if "idToken" in res:
                    st.session_state.user_token = res["idToken"]
                    st.session_state.user_email = res["email"]
                    st.rerun()
                else: st.error(f"Lỗi: {res.get('error', {}).get('message', 'Sai thông tin')}")
                    
    with tab_signup:
        with st.form("signup"):
            e_sign = st.text_input("Email")
            p_sign = st.text_input("Password (min 6 chars)", type="password")
            if st.form_submit_button("TẠO TÀI KHOẢN", type="primary"):
                res = firebase_auth(e_sign, p_sign, is_signup=True)
                if "idToken" in res: st.success("Thành công! Vui lòng chuyển sang tab Đăng nhập.")
                else: st.error(f"Lỗi: {res.get('error', {}).get('message', '')}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# SIDEBAR (CHỈ CHỨA CÔNG CỤ, KHÔNG ĐIỀU HƯỚNG BƯỚC)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #D4AF37; margin-bottom: 0;'>EXECUTIVE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.7rem; letter-spacing: 2px; color: #888;'>STRATEGY WIZARD</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 0.8rem;'>👤 {st.session_state.user_email}</p>", unsafe_allow_html=True)
    if st.button("ĐĂNG XUẤT", use_container_width=True):
        st.session_state.user_token = None
        st.rerun()
        
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    api_key = st.text_input("GCP Authentication Key (AI):", type="password")
    
    st.markdown("### DATA INGESTION")
    uploaded_file = st.file_uploader("Upload PDF/TXT Document", type=["pdf", "txt"], label_visibility="collapsed")
    if uploaded_file:
        content = doc_file_pdf(uploaded_file) if uploaded_file.name.endswith('.pdf') else uploaded_file.read().decode("utf-8")
        st.session_state.app_state["file_content"] = content
        st.success("Tài liệu đã được xác thực.")
        
        st.markdown("<div class='magic-btn'>", unsafe_allow_html=True)
        if st.button("TỰ ĐỘNG PHÂN TÍCH JD"):
            if not api_key: st.error("Cần nhập API Key.")
            else:
                with st.spinner("Đang định tuyến Framework & Phân tích chiến lược..."):
                    prompt = f"""
                    Đọc tài liệu tuyển dụng/công ty sau: {content[:4000]}
                    Trích xuất 5 bước chiến lược và trả về ĐÚNG định dạng JSON sau:
                    {{
                        "company": "Tên công ty", "industry": "Ngành nghề", "framework_used": "Tên framework đánh giá năng lực",
                        "opportunities": ["Cơ hội 1"], "threats": ["Thách thức 1"],
                        "company_strengths": ["[DN] Lợi thế 1"], "company_weaknesses": ["[DN] Rủi ro 1"],
                        "personal_strengths": ["[Cá nhân] Kỹ năng cần có 1"], "personal_weaknesses": ["[Cá nhân] Điểm yếu thường gặp"],
                        "tows_so": "Chiến lược Tấn công SO", "tows_wt": "Chiến lược Phòng thủ WT",
                        "smart_goals": ["Mục tiêu SMART 1"]
                    }}
                    """
                    data = hoi_ai_json(prompt, api_key)
                    if data:
                        st.session_state.app_state.update({
                            "company": data.get("company", ""), "industry": data.get("industry", ""), "framework_used": data.get("framework_used", ""),
                            "opportunities": data.get("opportunities", []), "threats": data.get("threats", []),
                            "company_strengths": data.get("company_strengths", []), "company_weaknesses": data.get("company_weaknesses", []),
                            "personal_strengths": data.get("personal_strengths", []), "personal_weaknesses": data.get("personal_weaknesses", []),
                            "tows": {"SO": data.get("tows_so", ""), "WT": data.get("tows_wt", "")}, "smart_goals": data.get("smart_goals", [])
                        })
                        st.success("Hoàn tất! Hãy bấm 'Tiếp Tục' để xem kết quả.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MAIN WIZARD INTERFACE (TUẦN TỰ)
# ==========================================
step = st.session_state.app_state["step"]
step_names = ["I. RADAR", "II. DNA", "III. COMPETENCY", "IV. TOWS", "V. REPORT"]

# Hiển thị thanh tiến trình (Progress Indicator)
indicator_html = "<div class='step-indicator'>"
for i, name in enumerate(step_names, 1):
    active_class = "class='active'" if i == step else ""
    indicator_html += f"<span {active_class}>{name}</span> &nbsp;&nbsp;&nbsp; "
indicator_html += "</div>"
st.markdown(indicator_html, unsafe_allow_html=True)

# --- NỘI DUNG TỪNG BƯỚC ---
if step == 1:
    st.markdown("<div class='app-card'><h2>I. Radar Thị Trường Vĩ Mô (PESTLE)</h2></div>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    st.session_state.app_state['industry'] = colA.text_input("Ngành nghề:", st.session_state.app_state['industry'])
    st.session_state.app_state['company'] = colB.text_input("Doanh nghiệp:", st.session_state.app_state['company'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Cơ hội (Opportunities)</h4>", unsafe_allow_html=True)
        st.text_area("Thêm cơ hội (Mỗi dòng 1 ý):", value="\n".join(st.session_state.app_state["opportunities"]), key="o_input", height=150)
    with c2:
        st.markdown("<h4>Thách thức (Threats)</h4>", unsafe_allow_html=True)
        st.text_area("Thêm thách thức (Mỗi dòng 1 ý):", value="\n".join(st.session_state.app_state["threats"]), key="t_input", height=150)

elif step == 2:
    st.markdown("<div class='app-card'><h2>II. DNA Doanh Nghiệp (VRIO)</h2></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #D4AF37; font-weight: 600;'>Framework Định Tuyến: {st.session_state.app_state['framework_used'] or 'Chưa xác định'}</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Lợi thế Cạnh tranh DN</h4>", unsafe_allow_html=True)
        st.text_area("Điểm mạnh DN:", value="\n".join(st.session_state.app_state["company_strengths"]), height=150)
    with c2:
        st.markdown("<h4>Rủi ro / Điểm yếu DN</h4>", unsafe_allow_html=True)
        st.text_area("Điểm yếu DN:", value="\n".join(st.session_state.app_state["company_weaknesses"]), height=150)

elif step == 3:
    st.markdown("<div class='app-card'><h2>III. Bản Đồ Năng Lực Cá Nhân (STAR)</h2></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Kỹ năng cốt lõi (Strengths)</h4>", unsafe_allow_html=True)
        st.text_area("Điểm mạnh cá nhân:", value="\n".join(st.session_state.app_state["personal_strengths"]), height=150)
    with c2:
        st.markdown("<h4>Lỗ hổng kỹ năng (Weaknesses)</h4>", unsafe_allow_html=True)
        st.text_area("Điểm yếu cá nhân:", value="\n".join(st.session_state.app_state["personal_weaknesses"]), height=150)

elif step == 4:
    st.markdown("<div class='app-card'><h2>IV. Giao Thoa Chiến Lược (TOWS)</h2></div>", unsafe_allow_html=True)
    st.markdown("<h4>Chiến lược Khai thác (SO)</h4>", unsafe_allow_html=True)
    st.session_state.app_state["tows"]["SO"] = st.text_area("Dùng Điểm mạnh chớp Cơ hội:", st.session_state.app_state["tows"]["SO"], height=120)
    st.markdown("<br><h4>Chiến lược Phòng thủ (WT)</h4>", unsafe_allow_html=True)
    st.session_state.app_state["tows"]["WT"] = st.text_area("Khắc phục Điểm yếu né Thách thức:", st.session_state.app_state["tows"]["WT"], height=120)

elif step == 5:
    st.markdown(f"""
        <div class='app-card' style='text-align: center;'>
            <h4 style='color: #D4AF37; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0;'>EXECUTIVE SUMMARY</h4>
            <h1 style='font-size: 2.5rem; margin-top: 10px;'>{st.session_state.app_state['company'].upper() or 'BÁO CÁO CHIẾN LƯỢC'}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Lộ trình Thực thi (SMART Execution)</h3>", unsafe_allow_html=True)
    st.text_area("Mục tiêu của bạn:", value="\n".join(st.session_state.app_state["smart_goals"]), height=150)
    st.markdown("</div>", unsafe_allow_html=True)

# --- NÚT ĐIỀU HƯỚNG (WIZARD NEXT/BACK) ---
st.markdown("<br><hr style='border: none; border-top: 1px solid #EAEAEA;'><br>", unsafe_allow_html=True)
col_back, col_space, col_next = st.columns([2, 6, 2])

with col_back:
    if step > 1:
        if st.button("← QUAY LẠI", use_container_width=True):
            st.session_state.app_state["step"] -= 1
            st.rerun()

with col_next:
    if step < 5:
        if st.button("TIẾP TỤC →", type="primary", use_container_width=True):
            st.session_state.app_state["step"] += 1
            st.rerun()
