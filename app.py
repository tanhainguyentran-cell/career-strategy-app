import streamlit as st
import google.generativeai as genai
from datetime import date

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX)
# ==========================================
st.set_page_config(page_title="Strategic Career App", layout="wide", initial_sidebar_state="expanded")

# CSS làm sạch và làm đẹp giao diện
st.markdown("""
    <style>
    :root { --primary: #0f172a; --secondary: #3b82f6; --bg: #f8fafc; }
    .stApp { background-color: var(--bg); }
    h1, h2, h3 { color: var(--primary); font-family: 'Inter', sans-serif; }
    .card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 1rem; border-top: 4px solid var(--secondary); }
    .ai-bubble { background: #eff6ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; font-style: italic; margin-top: 10px; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: 0.2s; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO STATE MANAGER
# ==========================================
if 'state' not in st.session_state:
    st.session_state.state = {
        "step": 1,
        "industry": "",
        "company": "",
        "opportunities": [], "threats": [],
        "strengths": [], "weaknesses": [],
        "tows": {"SO": "", "ST": "", "WO": "", "WT": ""},
        "smart_goals": [],
        "ai_feedbacks": {} # Lưu trữ phản hồi của AI
    }

def navigate(step): st.session_state.state["step"] = step

# Hàm gọi AI Socratic Coach
def ask_ai_coach(prompt, api_key):
    if not api_key: return "Vui lòng nhập API Key ở thanh bên."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Lỗi kết nối AI: {e}"

# ==========================================
# 3. SIDEBAR (ĐIỀU HƯỚNG & CẤU HÌNH)
# ==========================================
with st.sidebar:
    st.title("🧭 Strategy Wizard")
    st.caption("5-Step Personal Strategic Management Framework")
    api_key = st.text_input("🔑 Gemini API Key:", type="password", help="Bắt buộc để kích hoạt AI Coach")
    st.markdown("---")
    
    steps = ["1. Market Radar", "2. Enterprise DNA", "3. Competency", "4. TOWS Strategy", "5. Execution & Output"]
    for i, name in enumerate(steps, 1):
        if st.button(name, use_container_width=True, type="primary" if st.session_state.state["step"] == i else "secondary"):
            navigate(i)

# ==========================================
# 4. LUỒNG GIAO DIỆN CHÍNH
# ==========================================
step = st.session_state.state["step"]

# --- BƯỚC 1: MARKET RADAR ---
if step == 1:
    st.markdown("<div class='card'><h2>🌍 Bước 1: Market Radar</h2><p>Phân tích vĩ mô PESTLE.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    st.session_state.state["industry"] = col1.text_input("Ngành mục tiêu (VD: Ngân hàng, FMCG):", st.session_state.state["industry"])
    st.session_state.state["company"] = col2.text_input("Doanh nghiệp mục tiêu:", st.session_state.state["company"])

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 1, 1])
        factor = c1.text_input("Nhập yếu tố thị trường (VD: Lãi suất tăng):")
        cat = c2.selectbox("Phân loại:", ["Political", "Economic", "Social", "Technological", "Legal", "Environmental"])
        impact = c3.radio("Tác động:", ["Cơ hội", "Thách thức"], horizontal=True)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("Phân tích & Thêm vào Dữ liệu", use_container_width=True):
            if factor:
                item = f"[{cat}] {factor}"
                if "Cơ hội" in impact: st.session_state.state["opportunities"].append(item)
                else: st.session_state.state["threats"].append(item)
                st.success("Đã ghi nhận!")
                
        # AI CRITIQUE (PESTLE)
        if col_btn2.button("🤖 Phản biện AI (Socratic Coach)", type="secondary", use_container_width=True):
            if factor:
                with st.spinner("AI đang tư duy phản biện..."):
                    prompt = f"Tôi đang chuẩn bị phỏng vấn ngành {st.session_state.state['industry']}. Yếu tố vĩ mô tôi đưa ra là: '{factor}'. Hãy đóng vai Giám đốc Chiến lược (McKinsey). Áp dụng tư duy bậc 2, hãy đặt ra 2 câu hỏi sắc bén buộc tôi phải đào sâu về hệ quả khôn lường của yếu tố này đến chuỗi cung ứng hoặc quyền lực định giá. Trả lời ngắn gọn dưới 50 từ."
                    feedback = ask_ai_coach(prompt, api_key)
                    st.session_state.state["ai_feedbacks"][factor] = feedback
        
        if factor in st.session_state.state["ai_feedbacks"]:
            st.markdown(f"<div class='ai-bubble'><strong>AI Coach:</strong> {st.session_state.state['ai_feedbacks'][factor]}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- BƯỚC 2: ENTERPRISE DNA ---
elif step == 2:
    st.markdown("<div class='card'><h2>🧬 Bước 2: Enterprise DNA</h2><p>Đánh giá VRIO để tìm Lợi thế cạnh tranh nội tại.</p></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        resource = st.text_input("Nguồn lực của DN (VD: Văn hóa Agile, Dữ liệu khách hàng lớn):")
        v = st.checkbox("Valuable (Có giá trị)?")
        r = st.checkbox("Rare (Hiếm có)?")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        if col_btn1.button("Ghi nhận VRIO", use_container_width=True):
            if resource:
                if v and r: st.session_state.state["strengths"].append(f"[DN] {resource}")
                else: st.session_state.state["weaknesses"].append(f"[DN] {resource}")
                st.success("Đã phân loại!")
                
        # AI VALIDATION (VRIO)
        if col_btn2.button("🤖 Kiểm định VRIO bằng AI", type="secondary", use_container_width=True):
            if resource and v and r:
                with st.spinner("Đang kiểm định tính Hiếm..."):
                    prompt = f"Tôi cho rằng '{resource}' của công ty {st.session_state.state['company']} là một nguồn lực Hiếm và Khó sao chép (VRIO). Đóng vai một học giả khắt khe, hãy bác bỏ luận điểm này. Hãy giải thích tại sao đối thủ dễ dàng sao chép nó, và yêu cầu tôi chứng minh có công nghệ lõi nào bảo vệ nó không."
                    feedback = ask_ai_coach(prompt, api_key)
                    st.session_state.state["ai_feedbacks"][resource] = feedback
                    
        if resource in st.session_state.state["ai_feedbacks"]:
            st.markdown(f"<div class='ai-bubble'><strong>AI Coach:</strong> {st.session_state.state['ai_feedbacks'][resource]}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- BƯỚC 3: COMPETENCY ---
elif step == 3:
    st.markdown("<div class='card'><h2>🧠 Bước 3: Competency Mapping</h2><p>Lập bản đồ năng lực cá nhân (S/W).</p></div>", unsafe_allow_html=True)
    with st.form("competency_form"):
        skill = st.text_input("Kỹ năng của bạn (VD: Mô hình hóa tài chính):")
        level = st.radio("Mức độ thành thạo:", ["Điểm mạnh (S)", "Điểm yếu (W)"], horizontal=True)
        if st.form_submit_button("Thêm năng lực"):
            if "S" in level: st.session_state.state["strengths"].append(f"[Cá nhân] {skill}")
            else: st.session_state.state["weaknesses"].append(f"[Cá nhân] {skill}")
            st.success("Đã ghi nhận!")

# --- BƯỚC 4: TOWS STRATEGY ---
elif step == 4:
    st.markdown("<div class='card'><h2>⚔️ Bước 4: TOWS Matrix</h2><p>Giao diện ma trận ép buộc tư duy chéo.</p></div>", unsafe_allow_html=True)
    # Nhờ thiết kế này, sức lực nhận thức của người dùng chỉ dành cho việc tạo chiến lược [cite: 20]
    c1, c2 = st.columns(2)
    c1.info(f"**Strengths (S):** {', '.join(st.session_state.state['strengths'])}")
    c2.error(f"**Weaknesses (W):** {', '.join(st.session_state.state['weaknesses'])}")
    c1.success(f"**Opportunities (O):** {', '.join(st.session_state.state['opportunities'])}")
    c2.warning(f"**Threats (T):** {', '.join(st.session_state.state['threats'])}")
    
    st.markdown("### Thiết lập chiến lược (Dựa trên S-W-O-T đã nhập)")
    colA, colB = st.columns(2)
    st.session_state.state["tows"]["SO"] = colA.text_area("SO Strategy (Dùng S nắm bắt O):", st.session_state.state["tows"]["SO"])
    st.session_state.state["tows"]["WT"] = colB.text_area("WT Strategy (Phòng thủ W trước T):", st.session_state.state["tows"]["WT"])

# --- BƯỚC 5: FINAL OUTPUT & SMART ---
elif step == 5:
    st.markdown("<div class='card'><h2>🏆 Bước 5: Báo Cáo & Lộ trình SMART</h2></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        goal = st.text_area("Nhập mục tiêu SMART dựa trên chiến lược TOWS của bạn:")
        col_btn1, col_btn2 = st.columns([1, 1])
        
        if col_btn1.button("Thêm Mục tiêu", use_container_width=True):
            st.session_state.state["smart_goals"].append(goal)
            st.success("Đã thêm vào lộ trình!")
            
        # AI SMART REFINEMENT
        if col_btn2.button("🤖 AI Góp ý Mục tiêu", type="secondary", use_container_width=True):
            if goal:
                with st.spinner("AI đang soi chiếu tiêu chí SMART..."):
                    prompt = f"Mục tiêu của tôi là: '{goal}'. Hãy đóng vai Huấn luyện viên Doanh nghiệp. Đánh giá tính Cụ thể (Specific) và Đo lường (Measurable) của nó. Chỉ ra điểm còn mơ hồ và đề xuất cách gắn một con số/metric chuẩn xác hơn vào mục tiêu này. Trả lời 1 đoạn văn ngắn."
                    feedback = ask_ai_coach(prompt, api_key)
                    st.session_state.state["ai_feedbacks"][goal] = feedback
                    
        if goal in st.session_state.state["ai_feedbacks"]:
            st.markdown(f"<div class='ai-bubble'><strong>AI Refinement:</strong> {st.session_state.state['ai_feedbacks'][goal]}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # FINAL OUTPUT GENERATION
    st.markdown("### 📄 Bản Tóm Tắt Chiến Lược Dành Cho Phỏng Vấn")
    report = f"""
    ### Thông tin chung
    * **Ngành:** {st.session_state.state['industry']} | **Doanh nghiệp:** {st.session_state.state['company']}
    * **Ngày xuất:** {date.today().strftime('%d/%m/%Y')}
    
    ---
    ### 1. Dữ liệu Đầu vào (Foundations)
    * **Điểm mạnh nội tại (S):** {', '.join(st.session_state.state['strengths'])}
    * **Điểm yếu nội tại (W):** {', '.join(st.session_state.state['weaknesses'])}
    * **Cơ hội thị trường (O):** {', '.join(st.session_state.state['opportunities'])}
    * **Thách thức thị trường (T):** {', '.join(st.session_state.state['threats'])}
    
    ---
    ### 2. Chiến lược Cốt lõi (TOWS Synthesis)
    * **Chiến lược Tấn công (SO):** {st.session_state.state['tows']['SO']}
    * **Chiến lược Phòng thủ (WT):** {st.session_state.state['tows']['WT']}
    
    ---
    ### 3. Lộ trình Hành động (SMART Execution)
    """
    for idx, g in enumerate(st.session_state.state["smart_goals"], 1):
        report += f"{idx}. {g}\n"
        
    st.markdown(f"<div class='card'>{report}</div>", unsafe_allow_html=True)
    st.download_button("📥 Tải Báo Cáo Định dạng Markdown", report, "Strategic_Plan.md", use_container_width=True)
