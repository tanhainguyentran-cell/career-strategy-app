import streamlit as st
import google.generativeai as genai
from datetime import date

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX TIER 1)
# ==========================================
st.set_page_config(page_title="Strategic Career App", layout="wide", initial_sidebar_state="expanded")

# CSS Cao cấp: Nền xám nhạt, thẻ trắng bo góc có shadow, nút bấm gradient
st.markdown("""
    <style>
    /* Tổng thể */
    .stApp { background-color: #f3f4f6; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #1e3a8a; font-weight: 700; }
    
    /* Thiết kế thẻ (Card) */
    .premium-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        border-top: 5px solid #1d4ed8;
    }
    
    /* Nút bấm (Buttons) */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
    }
    .stButton>button[kind="primary"]:hover {
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    
    /* Các ô nhập liệu */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO STATE MANAGER
# ==========================================
if 'state' not in st.session_state:
    st.session_state.state = {
        "step": 1, "industry": "", "company": "",
        "opportunities": [], "threats": [],
        "strengths": [], "weaknesses": [],
        "tows": {"SO": "", "ST": "", "WO": "", "WT": ""},
        "smart_goals": [], "ai_feedbacks": {}
    }

def navigate(step): st.session_state.state["step"] = step

# --- HÀM GỌI AI ĐÃ FIX LỖI 404 ---
def ask_ai_coach(prompt, api_key):
    if not api_key: return "Vui lòng nhập API Key ở thanh bên để kích hoạt Mentor."
    try:
        genai.configure(api_key=api_key)
        # Sửa thành flash-latest để tránh lỗi version
        model = genai.GenerativeModel('gemini-1.5-flash-latest') 
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Lỗi hệ thống AI: {e}. Hãy kiểm tra lại API Key hoặc mạng của bạn."

# ==========================================
# 3. SIDEBAR (ĐIỀU HƯỚNG & CẤU HÌNH)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/strategy-board.png", width=70)
    st.title("Strategy Wizard")
    st.caption("5-Step Strategic Management")
    
    st.markdown("### ⚙️ Thiết lập AI")
    api_key = st.text_input("🔑 Gemini API Key:", type="password", help="Dùng để kích hoạt phản biện AI")
    
    st.markdown("---")
    st.markdown("### 🗺️ Lộ trình")
    steps = ["1. Market Radar", "2. Enterprise DNA", "3. Competency", "4. TOWS Strategy", "5. Final Output"]
    for i, name in enumerate(steps, 1):
        if st.button(name, use_container_width=True, type="primary" if st.session_state.state["step"] == i else "secondary"):
            navigate(i)

# ==========================================
# 4. LUỒNG GIAO DIỆN CHÍNH
# ==========================================
step = st.session_state.state["step"]

# --- BƯỚC 1: MARKET RADAR ---
if step == 1:
    st.markdown("<div class='premium-card'><h2>🌍 Bước 1: Market Radar</h2><p>Phân tích môi trường vĩ mô (PESTLE) để tìm kiếm Cơ hội và rủi ro thị trường.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    st.session_state.state["industry"] = col1.text_input("🏢 Ngành mục tiêu (VD: Ngân hàng):", st.session_state.state["industry"])
    st.session_state.state["company"] = col2.text_input("🎯 Doanh nghiệp (VD: Techcombank):", st.session_state.state["company"])

    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("### 📥 Nhập dữ liệu PESTLE")
    c1, c2, c3 = st.columns([3, 1, 1])
    factor = c1.text_input("Yếu tố thị trường (VD: Lãi suất huy động giảm):")
    cat = c2.selectbox("Phân loại:", ["Political", "Economic", "Social", "Technological", "Legal", "Environmental"])
    impact = c3.radio("Tác động:", ["🟢 Cơ hội", "🔴 Thách thức"], horizontal=True)
    
    col_btn1, col_btn2 = st.columns([1, 1])
    
    if col_btn1.button("💾 Phân tích & Ghi nhận", type="primary", use_container_width=True):
        if factor:
            item = f"[{cat}] {factor}"
            if "Cơ hội" in impact: st.session_state.state["opportunities"].append(item)
            else: st.session_state.state["threats"].append(item)
            st.success("Đã nạp vào cơ sở dữ liệu chiến lược!")
            
    if col_btn2.button("🤖 Nhờ AI phản biện (Socratic Coach)", use_container_width=True):
        if factor:
            with st.spinner("Đang kết nối với Cố vấn AI..."):
                prompt = f"Tôi đang chuẩn bị ứng tuyển vào {st.session_state.state['company']} ngành {st.session_state.state['industry']}. Yếu tố thị trường tôi đưa ra là: '{factor}'. Hãy đóng vai một Giám đốc khối chiến lược khó tính. Hãy đặt ra 1 câu hỏi thật hóc búa để buộc tôi phải suy nghĩ sâu hơn về tác động thực sự của yếu tố này đến mảng kinh doanh cốt lõi của công ty. Ngắn gọn dưới 60 từ."
                st.session_state.state["ai_feedbacks"][factor] = ask_ai_coach(prompt, api_key)
    
    # Hiển thị AI Coach bằng giao diện Chat Message của Streamlit
    if factor in st.session_state.state["ai_feedbacks"]:
        st.markdown("---")
        with st.chat_message("assistant", avatar="🤖"):
            st.write("**Cố vấn Chiến lược:**")
            st.write(st.session_state.state['ai_feedbacks'][factor])
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- BƯỚC 2: ENTERPRISE DNA ---
elif step == 2:
    st.markdown("<div class='premium-card'><h2>🧬 Bước 2: Enterprise DNA</h2><p>Đánh giá VRIO để tìm Lợi thế cạnh tranh nội tại của doanh nghiệp.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    resource = st.text_input("💡 Nhập Nguồn lực/Điểm mạnh của DN (VD: Hệ sinh thái khách hàng số):")
    col_cb1, col_cb2 = st.columns(2)
    v = col_cb1.checkbox("✅ Valuable (Mang lại giá trị thực tế)?")
    r = col_cb2.checkbox("💎 Rare (Hiếm, đối thủ khó có được)?")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    if col_btn1.button("💾 Ghi nhận VRIO", type="primary", use_container_width=True):
        if resource:
            if v and r: st.session_state.state["strengths"].append(f"[DN] {resource}")
            else: st.session_state.state["weaknesses"].append(f"[DN] {resource} (Thiếu tính V/R)")
            st.success("Đã phân tích xong!")
            
    if col_btn2.button("🤖 AI Kiểm định mức độ 'Hiếm'", use_container_width=True):
        if resource and v and r:
            with st.spinner("AI đang check chéo với dữ liệu ngành..."):
                prompt = f"Tôi cho rằng '{resource}' của {st.session_state.state['company']} là một nguồn lực Hiếm. Đóng vai một chuyên gia phân tích ngành, hãy chỉ ra 1 lý do vì sao lợi thế này có thể dễ dàng bị sao chép bởi các đối thủ lớn khác. Trả lời ngắn gọn dưới 60 từ."
                st.session_state.state["ai_feedbacks"][resource] = ask_ai_coach(prompt, api_key)
                
    if resource in st.session_state.state["ai_feedbacks"]:
        st.markdown("---")
        with st.chat_message("assistant", avatar="🤖"):
            st.write("**Chuyên gia Phân tích:**")
            st.write(st.session_state.state['ai_feedbacks'][resource])
    st.markdown("</div>", unsafe_allow_html=True)

# --- BƯỚC 3: COMPETENCY ---
elif step == 3:
    st.markdown("<div class='premium-card'><h2>🧠 Bước 3: Competency Mapping</h2><p>Bản đồ năng lực cá nhân (S/W).</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    skill = st.text_input("🎯 Kỹ năng cốt lõi của bạn (VD: Lập trình Python, Phân tích dữ liệu tài chính):")
    level = st.radio("Đánh giá thành thạo:", ["🌟 Điểm mạnh (S)", "⚠️ Cần cải thiện (W)"], horizontal=True)
    
    if st.button("💾 Lưu Năng lực", type="primary"):
        if "S" in level: st.session_state.state["strengths"].append(f"[Cá nhân] {skill}")
        else: st.session_state.state["weaknesses"].append(f"[Cá nhân] {skill}")
        st.success("Đã nạp vào kho dữ liệu!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- BƯỚC 4: TOWS STRATEGY ---
elif step == 4:
    st.markdown("<div class='premium-card'><h2>⚔️ Bước 4: Ma trận TOWS</h2><p>Phối hợp S-W-O-T để thiết lập chiến lược thực chiến.</p></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"💪 **Điểm mạnh (S):**\n" + "\n".join([f"- {s}" for s in st.session_state.state['strengths']]))
        st.success(f"🚀 **Cơ hội (O):**\n" + "\n".join([f"- {o}" for o in st.session_state.state['opportunities']]))
    with c2:
        st.warning(f"📉 **Điểm yếu (W):**\n" + "\n".join([f"- {w}" for w in st.session_state.state['weaknesses']]))
        st.error(f"⚠️ **Thách thức (T):**\n" + "\n".join([f"- {t}" for t in st.session_state.state['threats']]))
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("### ✍️ Lập Chiến Lược")
    st.session_state.state["tows"]["SO"] = st.text_area("🔥 SO Strategy (Dùng Điểm mạnh để nắm bắt Cơ hội):", st.session_state.state["tows"]["SO"])
    st.session_state.state["tows"]["WT"] = st.text_area("🛡️ WT Strategy (Khắc phục Điểm yếu để né Thách thức):", st.session_state.state["tows"]["WT"])
    st.markdown("</div>", unsafe_allow_html=True)

# --- BƯỚC 5: FINAL OUTPUT & SMART ---
elif step == 5:
    st.markdown("<div class='premium-card'><h2>🏆 Bước 5: Execution & SMART Goals</h2><p>Chuyển hóa chiến lược thành số liệu đo lường được.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    goal = st.text_area("🎯 Thiết lập Mục tiêu (Dựa trên Chiến lược Bước 4):")
    col_btn1, col_btn2 = st.columns([1, 1])
    
    if col_btn1.button("💾 Thêm vào Lộ trình", type="primary", use_container_width=True):
        st.session_state.state["smart_goals"].append(goal)
        st.success("Đã lưu!")
        
    if col_btn2.button("🤖 AI Soi chiếu chuẩn SMART", use_container_width=True):
        if goal:
            with st.spinner("AI đang kiểm tra tính cụ thể và đo lường..."):
                prompt = f"Mục tiêu: '{goal}'. Đóng vai Cố vấn thực thi. Hãy chỉ ra mục tiêu này đang thiếu yếu tố Đo lường (M) hoặc Thời gian (T) ở chỗ nào, và viết lại giúp tôi 1 phiên bản chuẩn SMART cực kỳ sắc bén. Trả lời dưới 80 từ."
                st.session_state.state["ai_feedbacks"][goal] = ask_ai_coach(prompt, api_key)
                
    if goal in st.session_state.state["ai_feedbacks"]:
        st.markdown("---")
        with st.chat_message("assistant", avatar="🤖"):
            st.write("**Cố vấn Thực thi:**")
            st.write(st.session_state.state['ai_feedbacks'][goal])
    st.markdown("</div>", unsafe_allow_html=True)

    # FINAL OUTPUT
    if st.session_state.state["smart_goals"]:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown(f"### 📋 EXECUTIVE SUMMARY: {st.session_state.state['company'].upper()}")
        st.write(f"**Ngày lập:** {date.today().strftime('%d/%m/%Y')}")
        st.markdown("#### Lộ trình hành động:")
        for idx, g in enumerate(st.session_state.state["smart_goals"], 1):
            st.write(f"**{idx}.** {g}")
        st.markdown("</div>", unsafe_allow_html=True)
