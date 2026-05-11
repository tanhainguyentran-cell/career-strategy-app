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
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A1A1A; line-height: 1.6; }
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
        border: 1px solid #D4AF37 !important; padding: 1rem; width: 100%; font-weight: bold !important;
    }
    .magic-btn>button:hover { background-color: #D4AF37 !important; color: #FFFFFF !important; }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea { 
        border-radius: 2px; border: 1px solid #E5E7EB; padding: 0.8rem; font-family: 'Inter', sans-serif;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { border-color: #0F172A; box-shadow: none; }
    
    .step-indicator { text-align: center; margin-bottom: 2rem; font-family: 'Playfair Display', serif; color: #888; letter-spacing: 2px; }
    .step-indicator span.active { color: #D4AF37; font-weight: bold; border-bottom: 2px solid #D4AF37; padding-bottom: 5px; }
    
    /* Làm đẹp các khung text area để hiển thị kết quả AI */
    textarea { background-color: #FCFCFC !important; border-left: 3px solid #D4AF37 !important; }
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
# STATE & HÀM AI ĐÃ FIX LỖI 404 VÀ TỐI ƯU PROMPT
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
        # Đã đổi tên model thành bản ổn định nhất
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt).text
        
        # Bắt JSON an toàn hơn
        json_match = re.search(r'\{[\s\S]*\}', res)
        if json_match: 
            return json.loads(json_match.group(0))
        else:
            st.error("AI không trả về đúng định dạng JSON. Vui lòng thử lại.")
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
# SIDEBAR
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
        st.success("Tài liệu đã được load thành công.")
        
        st.markdown("<div class='magic-btn'>", unsafe_allow_html=True)
        if st.button("TỰ ĐỘNG PHÂN TÍCH JD SÂU"):
            if not api_key: st.error("Cần nhập API Key.")
            else:
                with st.spinner("AI đang bóc tách tài liệu và phân tích chuyên sâu..."):
                    # Tinh chỉnh Prompt để AI trả về câu dài, có giải thích rõ ràng
                    prompt = f"""
                    Bạn là Giám đốc Chiến lược. Hãy đọc tài liệu tuyển dụng/công ty sau: {content[:4000]}
                    Nhiệm vụ: Phân tích thật CHI TIẾT nhưng CẤU TRÚC ĐƠN GIẢN. Mỗi ý phải có cụm từ chính và phần giải thích ý nghĩa phía sau.
                    
                    Trả về ĐÚNG định dạng JSON sau:
                    {{
                        "company": "Tên công ty", 
                        "industry": "Ngành nghề", 
                        "framework_used": "Tên framework năng lực (VD: Khung năng lực Lãnh đạo Ngân hàng)",
                        "opportunities": ["Cơ hội 1: [Giải thích tại sao đây là cơ hội]", "Cơ hội 2: [Giải thích]"], 
                        "threats": ["Thách thức 1: [Rủi ro cụ thể là gì]", "Thách thức 2: [Giải thích]"],
                        "company_strengths": ["Điểm mạnh 1: [Lợi thế mang lại]", "Điểm mạnh 2: [Lợi thế]"], 
                        "company_weaknesses": ["Điểm yếu 1: [Hạn chế]", "Điểm yếu 2: [Hạn chế]"],
                        "personal_strengths": ["Kỹ năng 1: [Tại sao JD lại cần kỹ năng này]", "Kỹ năng 2: [Giải thích]"], 
                        "personal_weaknesses": ["Điểm yếu thường gặp 1: [Hậu quả nếu thiếu]", "Điểm yếu 2: [Giải thích]"],
                        "tows_so": "Hành động 1: [Làm gì] để [Đạt được gì] dựa trên [Điểm mạnh nào]. \\nHành động 2: ...", 
                        "tows_wt": "Hành động 1: [Làm gì] để [Né rủi ro gì]. \\nHành động 2: ...",
                        "smart_goals": ["Mục tiêu 1: Đến [thời gian], đạt [con số] bằng cách [hành động].", "Mục tiêu 2: ..."]
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
                        st.success("Hoàn tất! Hãy xem kết quả phân tích chi tiết bên phải.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MAIN WIZARD INTERFACE (TUẦN TỰ)
# ==========================================
step = st.session_state.app_state["step"]
step_names = ["I. RADAR", "II. DNA", "III. COMPETENCY", "IV. TOWS", "V. REPORT"]

indicator_html = "<div class='step-indicator'>"
for i, name in enumerate(step_names, 1):
    active_class = "class='active'" if i == step else ""
    indicator_html += f"<span {active_class}>{name}</span> &nbsp;&nbsp;&nbsp; "
indicator_html += "</div>"
st.markdown(indicator_html, unsafe_allow_html=True)

# --- NỘI DUNG TỪNG BƯỚC ---
if step == 1:
    st.markdown("<div class='app-card'><h2>I. Radar Thị Trường Vĩ Mô (PESTLE)</h2><p style='color:#666;'>Nhận diện các biến động bên ngoài nằm ngoài tầm kiểm soát của doanh nghiệp.</p></div>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    st.session_state.app_state['industry'] = colA.text_input("Ngành nghề:", st.session_state.app_state['industry'])
    st.session_state.app_state['company'] = colB.text_input("Doanh nghiệp:", st.session_state.app_state['company'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='color: #047857;'>Cơ hội Mở rộng (Opportunities)</h4>", unsafe_allow_html=True)
        st.text_area("Chi tiết cơ hội:", value="\n\n".join(st.session_state.app_state["opportunities"]), key="o_input", height=250)
    with c2:
        st.markdown("<h4 style='color: #B91C1C;'>Thách thức Thị trường (Threats)</h4>", unsafe_allow_html=True)
        st.text_area("Chi tiết thách thức:", value="\n\n".join(st.session_state.app_state["threats"]), key="t_input", height=250)

elif step == 2:
    st.markdown("<div class='app-card'><h2>II. Phân Tích DNA Doanh Nghiệp (VRIO)</h2><p style='color:#666;'>Đánh giá xem lợi thế của công ty có bền vững không (Có giá trị? Có hiếm không?).</p></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Lợi thế Cạnh tranh Cốt lõi</h4>", unsafe_allow_html=True)
        st.text_area("Điểm mạnh DN:", value="\n\n".join(st.session_state.app_state["company_strengths"]), height=250)
    with c2:
        st.markdown("<h4>Rủi ro Nội tại & Điểm mù</h4>", unsafe_allow_html=True)
        st.text_area("Điểm yếu DN:", value="\n\n".join(st.session_state.app_state["company_weaknesses"]), height=250)

elif step == 3:
    st.markdown("<div class='app-card'><h2>III. Bản Đồ Năng Lực Cá Nhân (STAR)</h2><p style='color:#666;'>Soi chiếu kỹ năng của bạn vào khung năng lực mà nhà tuyển dụng yêu cầu.</p></div>", unsafe_allow_html=True)
    st.info(f"**Khung Đánh Giá Bắt Buộc:** {st.session_state.app_state['framework_used'] or 'Chưa xác định'}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Kỹ năng Must-have (Strengths)</h4>", unsafe_allow_html=True)
        st.text_area("Kỹ năng bạn cần chứng minh:", value="\n\n".join(st.session_state.app_state["personal_strengths"]), height=250)
    with c2:
        st.markdown("<h4>Lỗ hổng Kỹ năng (Weaknesses)</h4>", unsafe_allow_html=True)
        st.text_area("Điểm yếu bạn cần tìm cách khắc phục:", value="\n\n".join(st.session_state.app_state["personal_weaknesses"]), height=250)

elif step == 4:
    st.markdown("<div class='app-card'><h2>IV. Ma Trận Chiến Lược Kép (TOWS)</h2><p style='color:#666;'>Đây là bước quan trọng nhất. Bạn sẽ làm gì để giao thoa giữa thị trường và bản thân?</p></div>", unsafe_allow_html=True)
    st.markdown("<h4>Chiến lược Khai thác (SO: Strength + Opportunity)</h4>", unsafe_allow_html=True)
    st.session_state.app_state["tows"]["SO"] = st.text_area("Kế hoạch hành động:", st.session_state.app_state["tows"]["SO"], height=150)
    st.markdown("<br><h4>Chiến lược Phòng thủ (WT: Weakness + Threat)</h4>", unsafe_allow_html=True)
    st.session_state.app_state["tows"]["WT"] = st.text_area("Kế hoạch quản trị rủi ro:", st.session_state.app_state["tows"]["WT"], height=150)

elif step == 5:
    st.markdown(f"""
        <div class='app-card' style='text-align: center;'>
            <h4 style='color: #D4AF37; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0;'>EXECUTIVE SUMMARY</h4>
            <h1 style='font-size: 2.5rem; margin-top: 10px;'>{st.session_state.app_state['company'].upper() or 'BÁO CÁO CHIẾN LƯỢC'}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<h3>Lộ trình Thực thi (SMART Execution)</h3>", unsafe_allow_html=True)
    st.text_area("Mục tiêu của bạn (Đã được đo lường):", value="\n\n".join(st.session_state.app_state["smart_goals"]), height=200)
    st.markdown("</div>", unsafe_allow_html=True)

# --- NÚT ĐIỀU HƯỚNG (WIZARD NEXT/BACK) ---
st.markdown("<br><hr style='border: none; border-top: 1px solid #EAEAEA;'><br>", unsafe_allow_html=True)
col_back, col_space, col_next = st.columns([2, 6, 2])

with col_back:
    if step > 1:
        if st.button("← QUAY LẠI BƯỚC TRƯỚC", use_container_width=True):
            st.session_state.app_state["step"] -= 1
            st.rerun()

with col_next:
    if step < 5:
        if st.button("XÁC NHẬN & TIẾP TỤC →", type="primary", use_container_width=True):
            st.session_state.app_state["step"] += 1
            st.rerun()
