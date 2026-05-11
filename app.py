import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="AI Career Strategy App", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. KHỞI TẠO TRẠNG THÁI (STATE MANAGEMENT)
if 'data' not in st.session_state:
    st.session_state.data = {
        "step": 1,
        "industry": "Tài chính / Ngân hàng",
        "opportunities": [], 
        "threats": [],      
        "strengths": [],    
        "weaknesses": [],   
        "strategies": {"SO": "", "ST": "", "WO": "", "WT": ""},
        "smart_goals": []
    }

def go_to(step):
    st.session_state.data["step"] = step

# --- HÀM GỌI AI ---
def get_ai_suggestion(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        # Sử dụng model gemini mới nhất
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Lỗi kết nối AI: Vui lòng kiểm tra lại API Key. (Chi tiết: {e})"

# 3. SIDEBAR ĐIỀU HƯỚNG & CẤU HÌNH AI
with st.sidebar:
    st.title("🤖 AI Career Strategist")
    
    st.markdown("### 🔑 Cấu hình AI")
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password", help="Lấy key miễn phí tại Google AI Studio")
    if not api_key:
        st.warning("Vui lòng nhập API Key để mở khóa tính năng AI.")
    
    st.markdown("---")
    st.info(f"📍 Đang ở: Bước {st.session_state.data['step']}/5")
    if st.button("1. Market Radar"): go_to(1)
    if st.button("2. Enterprise DNA"): go_to(2)
    if st.button("3. Competency"): go_to(3)
    if st.button("4. AI TOWS Matrix"): go_to(4)
    if st.button("5. AI SMART Roadmap"): go_to(5)

# 4. CHI TIẾT CÁC BƯỚC
current_step = st.session_state.data["step"]

# --- BƯỚC 1: MARKET RADAR ---
if current_step == 1:
    st.header("🚀 Bước 1: Market Radar (Phân tích ngoại vi)")
    st.session_state.data["industry"] = st.selectbox("Ngành nghề mục tiêu của bạn:", 
                                                     ["Tài chính / Ngân hàng", "Kiểm toán (Big4)", "Công nghệ (Tech MNC)", "FMCG", "Khác"])
    
    with st.form("pestle_form", clear_on_submit=True):
        factor = st.text_input("Nhập yếu tố vĩ mô (VD: Chuyển đổi số ngành ngân hàng, Lãi suất...)")
        type_ot = st.radio("Đánh giá:", ["Cơ hội (O)", "Thách thức (T)"], horizontal=True)
        if st.form_submit_button("Thêm dữ liệu") and factor:
            if "Cơ hội" in type_ot:
                st.session_state.data["opportunities"].append(factor)
            else:
                st.session_state.data["threats"].append(factor)
            st.success("Đã ghi nhận!")

    c1, c2 = st.columns(2)
    c1.write("**Cơ hội (O):**", st.session_state.data["opportunities"])
    c2.write("**Thách thức (T):**", st.session_state.data["threats"])

# --- BƯỚC 2: ENTERPRISE DNA ---
elif current_step == 2:
    st.header("🧬 Bước 2: Enterprise DNA (Nội tại Doanh nghiệp)")
    with st.form("vrio_form", clear_on_submit=True):
        resource = st.text_input("Điểm đặc bật của DN mục tiêu (VD: Mạng lưới chi nhánh lớn, Văn hóa Agile...)")
        type_sw = st.radio("Đánh giá:", ["Điểm mạnh (S)", "Điểm yếu (W)"], horizontal=True)
        if st.form_submit_button("Lưu đánh giá") and resource:
            if "Điểm mạnh" in type_sw:
                st.session_state.data["strengths"].append(f"[DN] {resource}")
            else:
                st.session_state.data["weaknesses"].append(f"[DN] {resource}")
            st.success("Đã ghi nhận!")

# --- BƯỚC 3: COMPETENCY MAPPING ---
elif current_step == 3:
    st.header("🧠 Bước 3: Competency Mapping (Năng lực cá nhân)")
    with st.form("star_form", clear_on_submit=True):
        skill = st.text_input("Kỹ năng của bạn (VD: Khả năng phân tích dữ liệu, Tiếng Anh...)")
        level = st.radio("Mức độ:", ["Tốt (S)", "Cần cải thiện (W)"], horizontal=True)
        if st.form_submit_button("Lưu năng lực") and skill:
            if "Tốt" in level:
                st.session_state.data["strengths"].append(f"[Cá nhân] {skill}")
            else:
                st.session_state.data["weaknesses"].append(f"[Cá nhân] {skill}")
            st.success("Đã ghi nhận!")

# --- BƯỚC 4: AI TOWS MATRIX ---
elif current_step == 4:
    st.header("⚔️ Bước 4: AI TOWS Matrix")
    st.write("AI sẽ tổng hợp dữ liệu từ Bước 1,2,3 để đề xuất chiến lược cạnh tranh cho bạn.")
    
    # Hiển thị lại dữ liệu
    st.write(f"**Ngành mục tiêu:** {st.session_state.data['industry']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.caption(f"**S:** {st.session_state.data['strengths']}")
    c2.caption(f"**W:** {st.session_state.data['weaknesses']}")
    c3.caption(f"**O:** {st.session_state.data['opportunities']}")
    c4.caption(f"**T:** {st.session_state.data['threats']}")
    
    if st.button("✨ Nhờ AI Phân tích & Viết Chiến lược TOWS", type="primary"):
        if not api_key:
            st.error("Vui lòng nhập API Key ở thanh bên trái trước.")
        else:
            with st.spinner("AI đang tư duy chiến lược..."):
                prompt = f"""
                Tôi đang ứng tuyển vào ngành {st.session_state.data['industry']}.
                Dưới đây là dữ liệu phân tích của tôi:
                - Điểm mạnh (S): {st.session_state.data['strengths']}
                - Điểm yếu (W): {st.session_state.data['weaknesses']}
                - Cơ hội (O): {st.session_state.data['opportunities']}
                - Thách thức (T): {st.session_state.data['threats']}
                
                Dựa trên mô hình ma trận TOWS, hãy tạo ra 4 chiến lược ngắn gọn, sắc bén:
                1. SO (Phát huy S để tận dụng O)
                2. ST (Phát huy S để né T)
                3. WO (Khắc phục W để nắm bắt O)
                4. WT (Phòng thủ: Khắc phục W và né T)
                Trả về kết quả rõ ràng, thực tế.
                """
                ai_result = get_ai_suggestion(prompt, api_key)
                st.session_state.data["tows_ai_result"] = ai_result
                
    if "tows_ai_result" in st.session_state.data:
        st.success("Phân tích hoàn tất!")
        st.markdown(st.session_state.data["tows_ai_result"])

# --- BƯỚC 5: AI SMART ROADMAP ---
elif current_step == 5:
    st.header("📅 Bước 5: AI SMART Roadmap")
    st.write("Biến chiến lược thành lộ trình hành động cụ thể.")
    
    if st.button("✨ Nhờ AI Lập Lộ Trình Hành Động (Roadmap 6 tháng)", type="primary"):
        if not api_key:
            st.error("Vui lòng nhập API Key ở thanh bên trái trước.")
        elif "tows_ai_result" not in st.session_state.data:
            st.warning("Vui lòng chạy AI ở Bước 4 trước để có dữ liệu chiến lược.")
        else:
            with st.spinner("AI đang xây dựng lộ trình..."):
                prompt = f"""
                Dựa trên chiến lược TOWS sau đây của tôi trong ngành {st.session_state.data['industry']}:
                {st.session_state.data['tows_ai_result']}
                
                Hãy lập cho tôi một lộ trình hành động 6 tháng theo tiêu chí SMART (Cụ thể, Đo lường được, Khả thi, Liên quan, Có thời hạn).
                Trình bày dưới dạng bảng hoặc gạch đầu dòng rõ ràng theo từng tháng.
                """
                ai_roadmap = get_ai_suggestion(prompt, api_key)
                st.session_state.data["ai_roadmap"] = ai_roadmap
                
    if "ai_roadmap" in st.session_state.data:
        st.markdown(st.session_state.data["ai_roadmap"])
