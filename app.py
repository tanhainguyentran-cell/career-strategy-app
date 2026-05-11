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
    /* Import Fonts: Playfair Display cho sự sang trọng, Inter cho sự sắc nét */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        color: #1A1A1A;
    }
    
    /* Background màu Off-white siêu sang */
    .stApp { background-color: #FAFAFA; }
    
    /* Tiêu đề mang phong cách Editorial / High-end */
    h1, h2, h3 { 
        font-family: 'Playfair Display', serif; 
        color: #0F172A; 
        letter-spacing: -0.5px;
    }
    
    /* Thẻ nội dung (Cards): Viền mỏng, không viền màu mè, bóng đổ siêu nhẹ */
    .app-card { 
        background: #FFFFFF; 
        padding: 3rem; 
        border-radius: 4px; 
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.04); 
        margin-bottom: 2rem; 
        border: 1px solid #F0F0F0; 
        border-top: 3px solid #D4AF37; /* Điểm nhấn Vàng Champagne */
    }
    
    /* Nút bấm (Buttons): Đen nhám, chữ in hoa, khoảng cách chữ rộng */
    .stButton>button { 
        border-radius: 2px !important; 
        font-weight: 500 !important; 
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        font-size: 0.85rem !important;
        transition: all 0.4s ease; 
        border: 1px solid #1A1A1A !important;
    }
    
    /* Nút Primary: Nền đen chữ trắng */
    .stButton>button[kind="primary"] { 
        background-color: #1A1A1A !important; 
        color: #FFFFFF !important; 
        padding: 0.8rem 2rem;
    }
    .stButton>button[kind="primary"]:hover { 
        background-color: #D4AF37 !important; /* Đổi sang Vàng Champagne khi hover */
        border-color: #D4AF37 !important;
        color: #FFFFFF !important;
    }
    
    /* Nút Magic (Auto-Pilot): Viền vàng */
    .magic-btn>button { 
        background-color: transparent !important; 
        color: #D4AF37 !important; 
        border: 1px solid #D4AF37 !important; 
        padding: 1rem; 
        width: 100%;
    }
    .magic-btn>button:hover { 
        background-color: #D4AF37 !important; 
        color: #FFFFFF !important; 
    }
    
    /* Ô nhập liệu (Inputs): Tối giản, chỉ viền dưới hoặc viền xám cực nhạt */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea { 
        border-radius: 2px; 
        border: 1px solid #E5E7EB; 
        padding: 0.8rem;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { 
        border-color: #0F172A; 
        box-shadow: none; 
    }
    
    /* Tinh chỉnh Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #F0F0F0;
    }
    </style>
    """, unsafe_allow_html=True)

# THAY BẰNG WEB API KEY CỦA BẠN (NẾU CẦN LOGIN)
FIREBASE_WEB_API_KEY = "AIzaSyD00faEnc-wexp9f3UIdfSJFrMZwNOFm7A"

# ==========================================
# STATE & HÀM AI (JSON AUTO-PILOT)
# ==========================================
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        "step": 1, "industry": "", "company": "", "framework_used": "",
        "opportunities": [], "threats": [], "strengths": [], "weaknesses": [],
        "tows": {"SO": "", "ST": "", "WO": "", "WT": ""}, "smart_goals": [],
        "file_content": ""
    }

def hoi_ai_json(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        res = model.generate_content(prompt).text
        json_match = re.search(r'\{.*\}', res, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return None
    except Exception as e:
        st.error(f"System Error: {e}")
        return None

def doc_file_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join(page.extract_text() for page in reader.pages)

def chuyen_buoc(step): st.session_state.app_state["step"] = step

# ==========================================
# SIDEBAR: KHU VỰC ĐIỀU KHIỂN & UPLOAD
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #D4AF37; margin-bottom: 0;'>EXECUTIVE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem; letter-spacing: 2px; color: #888;'>STRATEGY PORTAL</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    api_key = st.text_input("GCP Authentication Key:", type="password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 01. NẠP DỮ LIỆU (JD/BÁO CÁO)")
    uploaded_file = st.file_uploader("Upload PDF/TXT Document", type=["pdf", "txt"], label_visibility="collapsed")
    if uploaded_file:
        content = doc_file_pdf(uploaded_file) if uploaded_file.name.endswith('.pdf') else uploaded_file.read().decode("utf-8")
        st.session_state.app_state["file_content"] = content
        st.success("Tài liệu đã được xác thực.")
        
        st.markdown("<div class='magic-btn'>", unsafe_allow_html=True)
        if st.button("TỰ ĐỘNG PHÂN TÍCH TOÀN BỘ"):
            if not api_key:
                st.error("Authentication Key is required.")
            else:
                with st.spinner("Đang định tuyến Framework & Phân tích chiến lược..."):
                    prompt = f"""
                    Đọc tài liệu tuyển dụng/công ty sau: {content[:4000]}
                    YÊU CẦU:
                    1. Xác định loại hình tổ chức (Ngân hàng, Big 4, Tech MNC...) và chọn Framework đánh giá năng lực phù hợp.
                    2. Trích xuất toàn bộ 5 bước chiến lược: PESTLE (O, T), VRIO (S, W), STAR (S, W), TOWS, SMART Goals.
                    TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON, KHÔNG CÓ TEXT KHÁC:
                    {{
                        "company": "Tên công ty",
                        "industry": "Ngành nghề",
                        "framework_used": "Tên framework",
                        "opportunities": ["Cơ hội 1", "Cơ hội 2"],
                        "threats": ["Thách thức 1", "Thách thức 2"],
                        "strengths": ["[DN] Lợi thế 1", "[Cá nhân] Kỹ năng 1"],
                        "weaknesses": ["[DN] Rủi ro", "[Cá nhân] Điểm yếu"],
                        "tows_so": "Chiến lược Tấn công SO",
                        "tows_wt": "Chiến lược Phòng thủ WT",
                        "smart_goals": ["Mục tiêu SMART 1", "Mục tiêu SMART 2"]
                    }}
                    """
                    data = hoi_ai_json(prompt, api_key)
                    if data:
                        st.session_state.app_state.update({
                            "company": data.get("company", ""),
                            "industry": data.get("industry", ""),
                            "framework_used": data.get("framework_used", ""),
                            "opportunities": data.get("opportunities", []),
                            "threats": data.get("threats", []),
                            "strengths": data.get("strengths", []),
                            "weaknesses": data.get("weaknesses", []),
                            "tows": {"SO": data.get("tows_so", ""), "WT": data.get("tows_wt", "")},
                            "smart_goals": data.get("smart_goals", [])
                        })
                        chuyen_buoc(5)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 02. ĐIỀU HƯỚNG")
    for i, name in enumerate(["I. Radar Thị Trường", "II. DNA & Năng Lực", "III. Bỏ Qua", "IV. Ma Trận TOWS", "V. Báo Cáo Tổng Quan"], 1):
        if i != 3: 
            if st.button(name, use_container_width=True, type="primary" if st.session_state.app_state["step"] == i else "secondary"):
                chuyen_buoc(i)

# ==========================================
# GIAO DIỆN CHÍNH (HIỂN THỊ DỮ LIỆU)
# ==========================================
step = st.session_state.app_state["step"]

if step == 1:
    st.markdown("<div class='app-card'><h2>I. Radar Thị Trường Vĩ Mô</h2></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #888; letter-spacing: 1px;'>NGÀNH: {st.session_state.app_state['industry'].upper()} | DOANH NGHIỆP: {st.session_state.app_state['company'].upper()}</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Cơ hội (Opportunities)</h4>", unsafe_allow_html=True)
        for o in st.session_state.app_state["opportunities"]: 
            st.markdown(f"<div style='padding: 10px; border-left: 3px solid #D4AF37; background: #FAFAFA; margin-bottom: 8px;'>{o}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<h4>Thách thức (Threats)</h4>", unsafe_allow_html=True)
        for t in st.session_state.app_state["threats"]: 
            st.markdown(f"<div style='padding: 10px; border-left: 3px solid #1A1A1A; background: #FAFAFA; margin-bottom: 8px;'>{t}</div>", unsafe_allow_html=True)

elif step == 2:
    st.markdown("<div class='app-card'><h2>II. Phân Tích Nội Tại Tổ Chức & Cá Nhân</h2></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #D4AF37; font-weight: 600;'>Framework Định Tuyến: {st.session_state.app_state['framework_used']}</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4>Lợi thế Cạnh tranh (Strengths)</h4>", unsafe_allow_html=True)
        for s in st.session_state.app_state["strengths"]: 
            st.markdown(f"<div style='padding: 10px; border-bottom: 1px solid #EAEAEA;'>+ {s}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<h4>Điểm khuyết (Weaknesses)</h4>", unsafe_allow_html=True)
        for w in st.session_state.app_state["weaknesses"]: 
            st.markdown(f"<div style='padding: 10px; border-bottom: 1px solid #EAEAEA;'>- {w}</div>", unsafe_allow_html=True)

elif step == 4:
    st.markdown("<div class='app-card'><h2>IV. Giao Thoa Chiến Lược (TOWS)</h2></div>", unsafe_allow_html=True)
    st.markdown("<h4>Chiến lược Khai thác (SO)</h4>", unsafe_allow_html=True)
    st.text_area("SO Strategy:", st.session_state.app_state["tows"]["SO"], height=120, label_visibility="collapsed")
    st.markdown("<br><h4>Chiến lược Phòng thủ (WT)</h4>", unsafe_allow_html=True)
    st.text_area("WT Strategy:", st.session_state.app_state["tows"]["WT"], height=120, label_visibility="collapsed")

elif step == 5:
    st.markdown(f"""
        <div class='app-card' style='text-align: center;'>
            <h4 style='color: #D4AF37; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0;'>EXECUTIVE SUMMARY</h4>
            <h1 style='font-size: 2.5rem; margin-top: 10px;'>{st.session_state.app_state['company'].upper()}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    if not st.session_state.app_state['company']:
        st.info("Vui lòng tải tài liệu và kích hoạt hệ thống Auto-Pilot để xuất báo cáo.")
    else:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Lộ trình Thực thi (SMART Execution)</h3>", unsafe_allow_html=True)
        for idx, g in enumerate(st.session_state.app_state["smart_goals"], 1):
            st.markdown(f"<p style='font-size: 1.1rem;'><b>0{idx}.</b> {g}</p>", unsafe_allow_html=True)
        st.markdown("<br><hr style='border-top: 1px solid #EAEAEA;'><br>", unsafe_allow_html=True)
        st.markdown("<h3>Dữ liệu Cơ sở (Foundations)</h3>", unsafe_allow_html=True)
        colA, colB = st.columns(2)
        colA.markdown("<b>Core Strengths:</b>\n" + "\n".join([f"- {s}" for s in st.session_state.app_state['strengths']]))
        colB.markdown("<b>Market Opportunities:</b>\n" + "\n".join([f"- {o}" for o in st.session_state.app_state['opportunities']]))
        st.markdown("</div>", unsafe_allow_html=True)
