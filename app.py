import streamlit as st
import pandas as pd

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="Career Strategy Application", layout="wide", initial_sidebar_state="expanded")

# Tùy chỉnh CSS để giao diện chuyên nghiệp hơn
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stExpander { background-color: white; border-radius: 10px; }
    h1, h2, h3 { color: #1e3a8a; }
    .tows-box { padding: 15px; border-radius: 10px; border: 1px solid #e5e7eb; height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. KHỞI TẠO TRẠNG THÁI (STATE MANAGEMENT)
if 'data' not in st.session_state:
    st.session_state.data = {
        "step": 1,
        "industry": "Kinh tế quốc tế / Tài chính",
        "opportunities": [], # O từ Step 1
        "threats": [],      # T từ Step 1
        "strengths": [],    # S từ Step 2 & 3
        "weaknesses": [],   # W từ Step 2 & 3
        "strategies": {"SO": "", "ST": "", "WO": "", "WT": ""},
        "smart_goals": []
    }

def go_to(step):
    st.session_state.data["step"] = step

# 3. SIDEBAR ĐIỀU HƯỚNG
with st.sidebar:
    st.title("🎯 Career Strategist")
    st.info(f"📍 Đang ở: Bước {st.session_state.data['step']}/5")
    
    st.markdown("---")
    if st.button("1. Market Radar (PESTLE)"): go_to(1)
    if st.button("2. Enterprise DNA (VRIO)"): go_to(2)
    if st.button("3. Competency (STAR)"): go_to(3)
    if st.button("4. TOWS Matrix"): go_to(4)
    if st.button("5. SMART Roadmap"): go_to(5)
    
    st.markdown("---")
    if st.button("🔄 Reset Toàn bộ dữ liệu"):
        st.session_state.data = {
            "step": 1, "industry": "Kinh tế quốc tế", "opportunities": [], "threats": [],
            "strengths": [], "weaknesses": [], "strategies": {"SO": "", "ST": "", "WO": "", "WT": ""}, "smart_goals": []
        }
        st.rerun()

# 4. CHI TIẾT CÁC BƯỚC
current_step = st.session_state.data["step"]

# --- BƯỚC 1: MARKET RADAR ---
if current_step == 1:
    st.header("🚀 Bước 1: Market Radar (Phân tích ngoại vi)")
    st.write("Sử dụng PESTLE để xác định các yếu tố khách quan từ thị trường.")
    
    with st.expander("➕ Thêm yếu tố thị trường mới", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            factor = st.text_input("Yếu tố (VD: Lạm phát tăng, Xu hướng AI...)")
        with col2:
            cat = st.selectbox("Phân loại", ["Chính trị", "Kinh tế", "Xã hội", "Công nghệ", "Pháp lý", "Môi trường"])
        
        type_ot = st.radio("Đánh giá tác động:", ["Cơ hội (Opportunity)", "Thách thức (Threat)"], horizontal=True)
        
        if st.button("Ghi nhận vào hệ thống"):
            if factor:
                item = f"[{cat}] {factor}"
                if "Cơ hội" in type_ot:
                    st.session_state.data["opportunities"].append(item)
                else:
                    st.session_state.data["threats"].append(item)
                st.success("Đã cập nhật dữ liệu!")
            else:
                st.warning("Vui lòng nhập nội dung yếu tố.")

    col_o, col_t = st.columns(2)
    with col_o:
        st.subheader("🟢 Cơ hội (O)")
        for o in st.session_state.data["opportunities"]: st.write(f"✅ {o}")
    with col_t:
        st.subheader("🔴 Thách thức (T)")
        for t in st.session_state.data["threats"]: st.write(f"⚠️ {t}")

# --- BƯỚC 2: ENTERPRISE DNA ---
elif current_step == 2:
    st.header("🧬 Bước 2: Enterprise DNA (Nội tại Doanh nghiệp)")
    st.write("Phân tích lợi thế cạnh tranh của doanh nghiệp mục tiêu bằng mô hình VRIO.")
    
    with st.form("vrio_form"):
        resource = st.text_input("Nguồn lực/Lợi thế của DN (VD: Hệ thống quản trị rủi ro)")
        v = st.checkbox("Có giá trị (Valuable)?")
        r = st.checkbox("Hiếm (Rare)?")
        i = st.checkbox("Khó sao chép (Inimitable)?")
        o = st.checkbox("Tổ chức tốt (Organized)?")
        submit_vrio = st.form_submit_button("Lưu phân tích")
        
        if submit_vrio and resource:
            status = "S" if (v and r and i and o) else "W"
            tag = "[DN]" if status == "S" else "[Rủi ro DN]"
            if status == "S":
                st.session_state.data["strengths"].append(f"{tag} {resource}")
            else:
                st.session_state.data["weaknesses"].append(f"{tag} {resource}")
            st.success("Đã phân loại vào S/W!")

# --- BƯỚC 3: COMPETENCY MAPPING ---
elif current_step == 3:
    st.header("🧠 Bước 3: Competency Mapping (Năng lực cá nhân)")
    st.write("Sử dụng mô hình STAR để chứng minh kỹ năng của bản thân.")
    
    with st.form("star_form"):
        skill = st.text_input("Kỹ năng/Kinh nghiệm (VD: Phân tích dữ liệu bằng Python)")
        star_detail = st.text_area("Mô tả theo STAR (Situation - Task - Action - Result)")
        level = st.select_slider("Tự đánh giá năng lực:", options=["Yếu", "Trung bình", "Khá", "Tốt", "Xuất sắc"])
        submit_star = st.form_submit_button("Lưu năng lực")
        
        if submit_star and skill:
            if level in ["Khá", "Tốt", "Xuất sắc"]:
                st.session_state.data["strengths"].append(f"[Cá nhân] {skill} ({level})")
            else:
                st.session_state.data["weaknesses"].append(f"[Cá nhân] {skill} ({level})")
            st.success("Đã cập nhật bản đồ năng lực!")

# --- BƯỚC 4: TOWS MATRIX ---
elif current_step == 4:
    st.header("⚔️ Bước 4: Ma trận chiến lược TOWS")
    st.write("Kết hợp các yếu tố để tạo ra chiến lược hành động cụ thể.")
    
    # Hiển thị các danh sách S-W-O-T đã thu thập
    with st.expander("Xem tóm tắt các yếu tố hiện có"):
        c1, c2 = st.columns(2)
        c1.write("**Strengths (S):**")
        for s in st.session_state.data["strengths"]: c1.caption(s)
        c2.write("**Weaknesses (W):**")
        for w in st.session_state.data["weaknesses"]: c2.caption(w)
        c1.write("**Opportunities (O):**")
        for o in st.session_state.data["opportunities"]: c1.caption(o)
        c2.write("**Threats (T):**")
        for t in st.session_state.data["threats"]: c2.caption(t)

    st.markdown("### Thiết lập chiến lược")
    colA, colB = st.columns(2)
    with colA:
        st.session_state.data["strategies"]["SO"] = st.text_area("Chiến lược SO (Dùng S để tận dụng O):", st.session_state.data["strategies"]["SO"])
        st.session_state.data["strategies"]["WO"] = st.text_area("Chiến lược WO (Vượt qua W để nắm bắt O):", st.session_state.data["strategies"]["WO"])
    with colB:
        st.session_state.data["strategies"]["ST"] = st.text_area("Chiến lược ST (Dùng S để né tránh T):", st.session_state.data["strategies"]["ST"])
        st.session_state.data["strategies"]["WT"] = st.text_area("Chiến lược WT (Giảm thiểu W và né tránh T):", st.session_state.data["strategies"]["WT"])

# --- BƯỚC 5: SMART GOALS ---
elif current_step == 5:
    st.header("📅 Bước 5: SMART Roadmap")
    st.write("Chuyển hóa chiến lược thành mục tiêu có thể đo lường.")
    
    with st.form("smart_form"):
        goal_name = st.text_input("Tên mục tiêu (VD: Đạt chứng chỉ CFA Level 1)")
        m = st.text_input("Measure (Đo lường bằng con số cụ thể nào?)")
        t = st.date_input("Time-bound (Hạn chót hoàn thành)")
        submit_goal = st.form_submit_button("Thêm mục tiêu")
        
        if submit_goal and goal_name:
            st.session_state.data["smart_goals"].append({"goal": goal_name, "measure": m, "deadline": str(t)})
            st.success("Đã thêm vào lộ trình!")

    st.subheader("📋 Lộ trình của bạn")
    if st.session_state.data["smart_goals"]:
        df = pd.DataFrame(st.session_state.data["smart_goals"])
        st.table(df)
        
        # Nút xuất báo cáo giả lập
        st.download_button("📥 Tải báo cáo chiến lược (Markdown)", 
                         f"# Career Strategy Report\n\n## Strategies\n{st.session_state.data['strategies']}", 
                         file_name="my_strategy.md")
    else:
        st.info("Chưa có mục tiêu nào được thiết lập.")
