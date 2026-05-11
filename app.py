import streamlit as st
import requests
import json
from datetime import date
import PyPDF2
import re

# ==========================================
# CẤU HÌNH GIAO DIỆN LUXURY EXECUTIVE
# ==========================================
st.set_page_config(page_title="Executive Career Strategist", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A1A1A; }
    .stApp { background-color: #FAFAFA; }
    
    /* Thiết kế tiêu đề sang trọng */
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #0F172A; letter-spacing: -0.5px; }
    
    /* Thẻ Card nội dung */
    .app-card { 
        background: white; padding: 2.5rem; border-radius: 4px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.02); margin-bottom: 2rem; 
        border-top: 4px solid #D4AF37; /* Màu Vàng Champagne */
    }
    
    /* Nút bấm Executive */
    .stButton>button[kind="primary"] { 
        background-color: #1A1A1A !important; color: white !important; 
        border-radius: 0px !important; width: 100%; border: none !important; 
        padding: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;
    }
    .stButton>button[kind="primary"]:hover { background-color: #D4AF37 !important; color: white !important; }
    
    /* Input Fields */
    input, textarea, select { border-radius: 0px !important; border: 1px solid #E2E8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# HÀM KẾT NỐI AI (SỬ DỤNG KEY CỦA TÂN HẢI)
# ==========================================
GEMINI_API_KEY = "AIzaSyCNigw85FMCdi0HsRI1RUU5lwwq1tNMOwg"

def call_ai(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        res_json = res.json()
        output = res_json['candidates'][0]['content']['parts'][0]['text']
        # Trích xuất JSON nếu có
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match: return json.loads(json_match.group(0))
        return output
    except Exception as e:
        return f"Lỗi kết nối hệ thống: {str(e)}"

# ==========================================
# QUẢN LÝ TRẠNG THÁI (STATE)
# ==========================================
if 'state' not in st.session_state:
    st.session_state.state = {
        "step": 1,
        "profile": {"location": "", "level": "Sinh viên", "skills": "", "degree": ""},
        "goal": {"target": "", "deadline": ""},
        "feasibility": None,
        "roadmap_data": None
    }

def move_to(s): st.session_state.state["step"] = s

# ==========================================
# BƯỚC 1: KHỞI TẠO HỒ SƠ & ĐÁNH GIÁ MỤC TIÊU
# ==========================================
step = st.session_state.state["step"]

if step == 1:
    st.markdown("<div class='app-card'><h1>01. Thiết Lập Hồ Sơ Chiến Lược</h1><p>Hệ thống AI sẽ dựa trên nền tảng của bạn để xây dựng lộ trình cá nhân hóa.</p></div>", unsafe_allow_html=True)
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        st.session_state.state["profile"]["location"] = col1.text_input("Vị trí hiện tại (Nơi ở/Nơi làm việc):", value=st.session_state.state["profile"]["location"])
        st.session_state.state["profile"]["level"] = col2.selectbox("Trình độ học vấn:", ["Sinh viên", "Cử nhân", "Thạc sĩ", "Khác"])
        st.session_state.state["profile"]["skills"] = st.text_area("Năng lực & Kỹ năng cốt lõi:", placeholder="Ví dụ: Phân tích dữ liệu, Tiếng Anh Ielts 7.5, Python...", value=st.session_state.state["profile"]["skills"])
        st.session_state.state["profile"]["degree"] = st.text_input("Bằng cấp/Chứng chỉ hiện có:", value=st.session_state.state["profile"]["degree"])
        
        st.markdown("---")
        st.markdown("### Xác định Mục tiêu")
        target = st.text_input("Mục tiêu cụ thể của bạn là gì?", placeholder="Ví dụ: Đạt điểm A môn Kinh tế Chính trị / Trúng tuyển Techcombank")
        deadline = st.text_input("Thời gian hoàn thành (Ví dụ: 2 tuần / 5 tháng):")
        
        if st.form_submit_button("PHÂN TÍCH TÍNH KHẢ THI", type="primary"):
            if target and deadline:
                with st.spinner("AI đang thẩm định lộ trình..."):
                    prompt = f"""
                    Đóng vai chuyên gia tư vấn chiến lược. 
                    Hồ sơ: {st.session_state.state['profile']}
                    Mục tiêu: {target} trong {deadline}
                    
                    YÊU CẦU:
                    1. Đánh giá tính khả thi (Thực tế hay Phi thực tế).
                    2. Nếu phi thực tế (Ví dụ: 'Làm sao để trúng số', 'Làm giám đốc trong 1 ngày'), hãy giải thích dựa trên logic/xác suất và từ chối vạch lộ trình.
                    3. Nếu thực tế, hãy đưa ra nhận xét ngắn gọn và khuyến nghị sơ bộ.
                    4. Trả lời bằng tiếng Việt, chuyên nghiệp, dưới 120 chữ.
                    """
                    st.session_state.state["feasibility"] = call_ai(prompt)
                    st.session_state.state["goal"] = {"target": target, "deadline": deadline}
            else:
                st.error("Vui lòng nhập đầy đủ mục tiêu và thời gian.")

    if st.session_state.state["feasibility"]:
        st.markdown(f"<div class='app-card'><h3>Kết quả thẩm định từ AI</h3><p>{st.session_state.state['feasibility']}</p></div>", unsafe_allow_html=True)
        
        # Nếu mục tiêu khả thi, cho phép đi tiếp
        if "phi thực tế" not in st.session_state.state["feasibility"].lower():
            if st.button("XÁC NHẬN & VẠCH CHIẾN LƯỢC CHI TIẾT"):
                move_to(2)
                st.rerun()
        else:
            st.warning("Mục tiêu hiện tại chưa phù hợp để triển khai chiến lược. Vui lòng điều chỉnh lại.")

# (Các bước 2, 3, 4 sẽ được tôi code tiếp khi bạn xác nhận Bước 1 đã chạy ổn định với Key mới)
