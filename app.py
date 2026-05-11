import streamlit as st
import requests
import json
import re
import PyPDF2

# ==========================================
# CẤU HÌNH GIAO DIỆN LUXURY EXECUTIVE
# ==========================================
st.set_page_config(page_title="Executive Strategy", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A1A1A; }
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #0F172A; }
    .app-card { background: white; padding: 2.5rem; border-radius: 4px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 2rem; border-top: 4px solid #D4AF37; }
    .stButton>button[kind="primary"] { background-color: #1A1A1A !important; color: white !important; border-radius: 0px !important; width: 100%; border: none !important; padding: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button[kind="primary"]:hover { background-color: #D4AF37 !important; }
    .ai-warning { font-size: 0.8rem; color: #888; font-style: italic; margin-top: 10px; }
    textarea, input { border-radius: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# HÀM KẾT NỐI AI SIÊU ỔN ĐỊNH
# ==========================================
# Key của Tân Hải đã được nhúng trực tiếp để ai cũng dùng được
API_KEY = "AIzaSyCNigw85FMCdi0HsRI1RUU5lwwq1tNMOwg"

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        # Kiểm tra cấu trúc phản hồi an toàn
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            candidate = res_json['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                text_out = candidate['content']['parts'][0]['text']
                # Tìm JSON nếu có yêu cầu
                json_match = re.search(r'\{.*\}', text_out, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                return text_out
        return "⚠️ AI hiện đang quá tải hoặc phản hồi không đúng cấu trúc. Vui lòng thử lại sau vài giây."
    except Exception as e:
        return f"❌ Lỗi kết nối: {str(e)}"

# ==========================================
# QUẢN LÝ TRẠNG THÁI
# ==========================================
if 'state' not in st.session_state:
    st.session_state.state = {
        "step": 1,
        "profile": {"location": "", "level": "Sinh viên", "skills": "", "degree": ""},
        "goal": {"target": "", "deadline": ""},
        "feasibility": None,
        "framework_data": None,
        "final_roadmap": None
    }

def move_to(s): 
    st.session_state.state["step"] = s
    st.rerun()

# ==========================================
# BƯỚC 1: HỒ SƠ & MỤC TIÊU
# ==========================================
step = st.session_state.state["step"]

if step == 1:
    st.markdown("<div class='app-card'><h1>01. Hồ Sơ & Mục Tiêu</h1><p>Hệ thống AI sẽ thẩm định nền tảng và mục tiêu của bạn trước khi vạch lộ trình.</p></div>", unsafe_allow_html=True)
    
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        loc = col1.text_input("Vị trí/Nơi ở:", value=st.session_state.state["profile"]["location"])
        lvl = col2.selectbox("Trình độ:", ["Sinh viên", "Cử nhân", "Thạc sĩ", "Khác"], index=0)
        skills = st.text_area("Năng lực & Bằng cấp:", value=st.session_state.state["profile"]["skills"], placeholder="VD: IELTS 7.5, Python, Kế toán...")
        
        st.markdown("---")
        target = st.text_input("Mục tiêu cụ thể:", placeholder="VD: Trúng tuyển Techcombank / Đạt điểm A môn Kinh tế")
        deadline = st.text_input("Thời gian dự kiến:", placeholder="VD: 2 tháng / 2 tuần")
        
        if st.form_submit_button("THẨM ĐỊNH MỤC TIÊU", type="primary"):
            if target and deadline:
                with st.spinner("AI đang phân tích tính khả thi..."):
                    prompt = f"""
                    Phân tích hồ sơ: {lvl}, kỹ năng: {skills}. 
                    Mục tiêu: {target} trong {deadline}.
                    Hãy đánh giá tính khả thi. Nếu phi lý (như trúng số, làm giám đốc trong 1 ngày), hãy giải thích xác suất cực thấp và từ chối. 
                    Nếu thực tế, hãy nhận xét ngắn gọn. Trả lời dưới 100 từ tiếng Việt.
                    """
                    st.session_state.state["feasibility"] = call_gemini(prompt)
                    st.session_state.state["profile"] = {"location": loc, "level": lvl, "skills": skills}
                    st.session_state.state["goal"] = {"target": target, "deadline": deadline}
            else:
                st.warning("Vui lòng điền đầy đủ mục tiêu và thời gian.")

    if st.session_state.state["feasibility"]:
        st.markdown(f"<div class='app-card'><h3>Kết quả thẩm định AI</h3><p>{st.session_state.state['feasibility']}</p></div>", unsafe_allow_html=True)
        # Chỉ cho đi tiếp nếu mục tiêu không bị coi là phi thực tế
        if "phi thực tế" not in st.session_state.state["feasibility"].lower():
            if st.button("XÁC NHẬN & VẠCH LỘ TRÌNH CHI TIẾT"): move_to(2)

# ==========================================
# BƯỚC 2: PHÂN TÍCH CẤU PHẦN CHIẾN LƯỢC
# ==========================================
elif step == 2:
    st.markdown("<div class='app-card'><h1>02. Phân Tích Cấu Phần</h1><p>AI tự động vạch ra các hạng mục cần chuẩn bị dựa trên mục tiêu của bạn.</p></div>", unsafe_allow_html=True)
    
    if not st.session_state.state["framework_data"]:
        with st.spinner("AI đang bóc tách hạng mục..."):
            prompt = f"""
            Mục tiêu: {st.session_state.state['goal']['target']} trong {st.session_state.state['goal']['deadline']}.
            Hãy vạch ra 4 hạng mục quan trọng nhất cần thực hiện (Ví dụ: Kiến thức chuyên môn, Kỹ năng mềm, Hồ sơ...).
            Trả về JSON duy nhất: {{"items": {{"Tên hạng mục": "Gợi ý chi tiết"}}}}
            """
            st.session_state.state["framework_data"] = call_gemini(prompt)

    if isinstance(st.session_state.state["framework_data"], dict):
        for item, detail in st.session_state.state["framework_data"].get("items", {}).items():
            st.subheader(f"📍 {item}")
            st.text_area(f"Nội dung chuẩn bị cho {item}:", value=detail, height=100)
    
    st.markdown("<p class='ai-warning'>⚠️ Lưu ý: Thông tin AI hỗ trợ có thể sai sót, hãy kiểm chứng trước khi thực hiện.</p>", unsafe_allow_html=True)
    if st.button("TỔNG HỢP CHIẾN LƯỢC CUỐI", type="primary"): move_to(3)

# ==========================================
# BƯỚC 3: LỘ TRÌNH THỰC THI (FINAL REPORT)
# ==========================================
elif step == 3:
    st.markdown("<div class='app-card' style='text-align: center;'><h1>LỘ TRÌNH THỰC THI CHIẾN LƯỢC</h1></div>", unsafe_allow_html=True)
    
    if not st.session_state.state["final_roadmap"]:
        with st.spinner("Đang đúc kết lộ trình..."):
            prompt = f"""
            Hồ sơ: {st.session_state.state['profile']}
            Mục tiêu: {st.session_state.state['goal']}
            Hãy lập 1 lộ trình thực thi ngắn gọn, chuyên nghiệp, chia theo giai đoạn thời gian cụ thể.
            Trình bày bằng Markdown thật đẹp.
            """
            st.session_state.state["final_roadmap"] = call_gemini(prompt)
            
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown(st.session_state.state["final_roadmap"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("LÀM LẠI TỪ ĐẦU"):
        st.session_state.state = {"step": 1, "profile": {}, "goal": {}, "feasibility": None, "framework_data": None, "final_roadmap": None}
        st.rerun()
