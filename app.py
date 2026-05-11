import streamlit as st
import google.generativeai as genai
from datetime import date
import PyPDF2
import io

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX)
# ==========================================
st.set_page_config(page_title="Chiến Lược Sự Nghiệp", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #f0fdf4; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #166534; font-weight: 700; }
    
    .premium-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 6px solid #16a34a;
        transition: transform 0.2s;
    }
    .premium-card:hover { transform: translateY(-2px); }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(22, 163, 74, 0.3);
    }
    .stButton>button[kind="primary"]:hover { box-shadow: 0 6px 12px rgba(22, 163, 74, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO DỮ LIỆU (STATE MANAGER)
# ==========================================
if 'state' not in st.session_state:
    st.session_state.state = {
        "step": 1, 
        "industry": "Tài chính / Ngân hàng", 
        "company": "Techcombank",
        "opportunities": [], "threats": [],
        "strengths": [], "weaknesses": [],
        "tows": {"SO": "", "ST": "", "WO": "", "WT": ""},
        "smart_goals": [], "ai_feedbacks": {},
        "file_content": ""
    }

def chuyen_buoc(step): st.session_state.state["step"] = step

# --- HÀM GỌI AI & ĐỌC FILE ---
def hoi_ai(prompt, api_key):
    if not api_key: return "⚠️ Vui lòng nhập API Key ở thanh bên để kích hoạt Trợ lý AI."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest') 
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Lỗi hệ thống AI: {e}"

def doc_file_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Lỗi đọc file: {e}"

# ==========================================
# 3. THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/mind-map.png", width=80)
    st.title("Trợ Lý Chiến Lược")
    st.caption("Sinh viên Học viện Ngoại giao & Khối Kinh tế")
    
    st.markdown("### ⚙️ Cài Đặt AI")
    api_key = st.text_input("🔑 Google Gemini API Key:", type="password", help="Nhập mã API để AI có thể hoạt động.")
    
    st.markdown("### 📄 Đọc Tài Liệu (JD / Báo Cáo)")
    uploaded_file = st.file_uploader("Tải lên PDF hoặc TXT", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.name.endswith('.pdf'):
            st.session_state.state["file_content"] = doc_file_pdf(uploaded_file)
        else:
            st.session_state.state["file_content"] = uploaded_file.read().decode("utf-8")
        st.success("✅ AI đã đọc và ghi nhớ tài liệu!")
    
    st.markdown("---")
    st.markdown("### 🗺️ Lộ Trình Phân Tích")
    steps = ["1. Vĩ mô (Thị trường)", "2. Vi mô (Doanh nghiệp)", "3. Năng lực (Bản thân)", "4. Chiến lược TOWS", "5. Báo cáo Thực thi"]
    for i, name in enumerate(steps, 1):
        if st.button(name, use_container_width=True, type="primary" if st.session_state.state["step"] == i else "secondary"):
            chuyen_buoc(i)

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
step = st.session_state.state["step"]

# ------------------------------------------
# BƯỚC 1: RADAR THỊ TRƯỜNG
# ------------------------------------------
if step == 1:
    st.markdown("<div class='premium-card'><h2>🌍 Bước 1: Radar Thị Trường (PESTLE)</h2><p>Quét các yếu tố vĩ mô để tìm kiếm Cơ hội và Thách thức từ bên ngoài.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    st.session_state.state["industry"] = col1.text_input("🏢 Ngành mục tiêu:", st.session_state.state["industry"])
    st.session_state.state["company"] = col2.text_input("🎯 Doanh nghiệp mục tiêu:", st.session_state.state["company"])

    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("### 📥 Nhập thủ công hoặc nhờ AI phân tích tài liệu")
    
    # Nút trích xuất từ file
    if st.session_state.state["file_content"]:
        if st.button("✨ Nhờ AI tìm Cơ hội/Thách thức từ file đã tải lên", type="primary"):
            with st.spinner("AI đang quét tài liệu..."):
                prompt = f"Dựa vào tài liệu sau (trích xuất): {st.session_state.state['file_content'][:2000]}... Hãy liệt kê 2 Cơ hội thị trường và 2 Thách thức đối với người ứng tuyển vào {st.session_state.state['company']}. Trả lời ngắn gọn."
                ket_qua_file = hoi_ai(prompt, api_key)
                st.info(ket_qua_file)

    c1, c2, c3 = st.columns([3, 1, 1])
    factor = c1.text_input("Yếu tố (VD: Khuyến khích tín dụng xanh):")
    cat = c2.selectbox("Phân loại:", ["Chính trị", "Kinh tế", "Xã hội", "Công nghệ", "Pháp lý", "Môi trường"])
    impact = c3.radio("Tác động:", ["🟢 Cơ hội", "🔴 Thách thức"], horizontal=True)
    
    col_btn1, col_btn2 = st.columns([1, 1])
    if col_btn1.button("💾 Ghi nhận Yếu tố", type="primary", use_container_width=True):
        if factor:
            item = f"[{cat}] {factor}"
            if "Cơ hội" in impact: st.session_state.state["opportunities"].append(item)
            else: st.session_state.state["threats"].append(item)
            st.toast("Đã lưu dữ liệu thành công!", icon="✅")
            
    if col_btn2.button("🤖 Tranh biện với AI", use_container_width=True):
        if factor:
            with st.spinner("AI đang suy nghĩ..."):
                prompt = f"Tôi cho rằng '{factor}' là một {impact} đối với {st.session_state.state['company']}. Đóng vai Giám đốc Chiến lược, hãy đặt 1 câu hỏi phản biện cực kỳ hóc búa để tôi phải đào sâu hơn. Dưới 50 từ."
                st.session_state.state["ai_feedbacks"][factor] = hoi_ai(prompt, api_key)
    
    if factor in st.session_state.state["ai_feedbacks"]:
        with st.chat_message("assistant", avatar="🧐"):
            st.write("**Giám đốc Chiến lược AI:**", st.session_state.state['ai_feedbacks'][factor])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 2: DNA DOANH NGHIỆP
# ------------------------------------------
elif step == 2:
    st.markdown("<div class='premium-card'><h2>🧬 Bước 2: DNA Doanh Nghiệp (VRIO)</h2><p>Đánh giá nguồn lực nội tại của doanh nghiệp xem họ đang mạnh hay yếu ở đâu.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    resource = st.text_input("💡 Điểm nổi bật của DN (VD: Hệ sinh thái khách hàng đa dạng):")
    col_cb1, col_cb2 = st.columns(2)
    v = col_cb1.checkbox("✅ Mang lại giá trị thực tế cho khách hàng?")
    r = col_cb2.checkbox("💎 Cực kỳ hiếm, đối thủ khó có được?")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    if col_btn1.button("💾 Ghi nhận Nguồn lực", type="primary", use_container_width=True):
        if resource:
            if v and r: st.session_state.state["strengths"].append(f"[DN] Lợi thế: {resource}")
            else: st.session_state.state["weaknesses"].append(f"[DN] Hạn chế: {resource}")
            st.toast("Cập nhật bộ gen doanh nghiệp!", icon="🧬")
            
    if col_btn2.button("🤖 Nhờ AI kiểm định", use_container_width=True):
        if resource:
            with st.spinner("Kiểm tra với dữ liệu thị trường..."):
                prompt = f"Nguồn lực '{resource}' của {st.session_state.state['company']}. Hãy cho tôi biết 1 rủi ro khiến lợi thế này có thể biến mất trong 2 năm tới. Dưới 50 từ."
                st.session_state.state["ai_feedbacks"][resource] = hoi_ai(prompt, api_key)
                
    if resource in st.session_state.state["ai_feedbacks"]:
        with st.chat_message("assistant", avatar="📊"):
            st.write("**Chuyên gia rủi ro AI:**", st.session_state.state['ai_feedbacks'][resource])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 3: NĂNG LỰC CÁ NHÂN
# ------------------------------------------
elif step == 3:
    st.markdown("<div class='premium-card'><h2>🧠 Bước 3: Năng Lực Cốt Lõi (STAR)</h2><p>Lập bản đồ kỹ năng của bản thân.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    skill = st.text_input("🎯 Kỹ năng của bạn (VD: Mô hình hóa tài chính, Kỹ năng tổ chức sự kiện):")
    level = st.radio("Đánh giá thành thạo:", ["🌟 Điểm mạnh (S)", "⚠️ Cần cải thiện (W)"], horizontal=True)
    
    if st.button("💾 Nạp Kỹ Năng", type="primary"):
        if "S" in level: st.session_state.state["strengths"].append(f"[Cá nhân] {skill}")
        else: st.session_state.state["weaknesses"].append(f"[Cá nhân] {skill}")
        st.toast("Đã lưu kỹ năng!", icon="🎯")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 4: CHIẾN LƯỢC TOWS
# ------------------------------------------
elif step == 4:
    st.markdown("<div class='premium-card'><h2>⚔️ Bước 4: Ma Trận Chiến Lược TOWS</h2><p>Hệ thống tự động nối dữ liệu để bạn vạch ra chiến lược.</p></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"💪 **Điểm mạnh (S):**\n" + "\n".join([f"- {s}" for s in st.session_state.state['strengths']]))
        st.success(f"🚀 **Cơ hội (O):**\n" + "\n".join([f"- {o}" for o in st.session_state.state['opportunities']]))
    with c2:
        st.warning(f"📉 **Điểm yếu (W):**\n" + "\n".join([f"- {w}" for w in st.session_state.state['weaknesses']]))
        st.error(f"⚠️ **Thách thức (T):**\n" + "\n".join([f"- {t}" for t in st.session_state.state['threats']]))
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("### ✍️ Viết Chiến Lược Của Bạn")
    st.session_state.state["tows"]["SO"] = st.text_area("🔥 Chiến lược Tấn công (SO - Dùng Điểm mạnh chớp Cơ hội):", st.session_state.state["tows"]["SO"])
    st.session_state.state["tows"]["WT"] = st.text_area("🛡️ Chiến lược Phòng thủ (WT - Sửa Điểm yếu để né Thách thức):", st.session_state.state["tows"]["WT"])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 5: BÁO CÁO THỰC THI
# ------------------------------------------
elif step == 5:
    st.markdown("<div class='premium-card'><h2>🏆 Bước 5: Báo Cáo & Lộ Trình</h2><p>Thiết lập mục tiêu chuẩn SMART và xuất báo cáo phỏng vấn.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    goal = st.text_area("🎯 Viết mục tiêu hành động cụ thể:")
    col_btn1, col_btn2 = st.columns([1, 1])
    
    if col_btn1.button("💾 Thêm Mục Tiêu", type="primary", use_container_width=True):
        st.session_state.state["smart_goals"].append(goal)
        st.toast("Đã thêm vào lộ trình!", icon="🚀")
        
    if col_btn2.button("🤖 AI Chuẩn hóa mục tiêu", use_container_width=True):
        if goal:
            with st.spinner("AI đang kiểm tra tính khả thi..."):
                prompt = f"Hãy sửa mục tiêu '{goal}' thành một mục tiêu chuẩn SMART (Cụ thể, Đo lường được, Khả thi, Liên quan, Có thời hạn). Viết lại thành 1 câu duy nhất đầy sức nặng."
                st.session_state.state["ai_feedbacks"][goal] = hoi_ai(prompt, api_key)
                
    if goal in st.session_state.state["ai_feedbacks"]:
        with st.chat_message("assistant", avatar="💡"):
            st.write("**Gợi ý từ AI:**", st.session_state.state['ai_feedbacks'][goal])
    st.markdown("</div>", unsafe_allow_html=True)

    # NÚT XUẤT BÁO CÁO HOÀNH TRÁNG
    if st.session_state.state["smart_goals"]:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>BẢN TÓM TẮT CHIẾN LƯỢC: {st.session_state.state['company'].upper()}</h3>", unsafe_allow_html=True)
        st.write(f"**🗓️ Ngày lập:** {date.today().strftime('%d/%m/%Y')}")
        st.markdown("---")
        st.markdown("#### 🚀 Lộ Trình Hành Động:")
        for idx, g in enumerate(st.session_state.state["smart_goals"], 1):
            st.write(f"**{idx}.** {g}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🎉 Hoàn Thành Báo Cáo", type="primary", use_container_width=True):
            st.balloons()
            st.success("Tuyệt vời! Báo cáo của bạn đã sẵn sàng cho buổi phỏng vấn sắp tới.")
