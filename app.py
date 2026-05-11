import streamlit as st

# Cấu hình giao diện
st.set_page_config(page_title="Career Strategy", layout="wide")

# KHỞI TẠO BỘ NHỚ
if 'step' not in st.session_state:
    st.session_state.step = 1
# Tạo 2 mảng rỗng để chứa Cơ hội và Thách thức
if 'opportunities' not in st.session_state:
    st.session_state.opportunities = []
if 'threats' not in st.session_state:
    st.session_state.threats = []

st.title("🎯 Career Strategy Application")
st.markdown("---")

# THANH ĐIỀU HƯỚNG
with st.sidebar:
    st.header("Lộ trình 5 bước")
    if st.button("1. Market Radar", use_container_width=True): st.session_state.step = 1
    if st.button("2. Enterprise DNA", use_container_width=True): st.session_state.step = 2
    if st.button("4. TOWS Matrix (Preview)", use_container_width=True): st.session_state.step = 4

# HIỂN THỊ NỘI DUNG TỪNG BƯỚC
if st.session_state.step == 1:
    st.subheader("Bước 1: Market Radar (Phân tích Vĩ mô & Ngành)")
    st.write("Sử dụng mô hình PESTLE để quét thị trường. Mỗi yếu tố bạn nhập vào sẽ được hệ thống tự động dán nhãn và luân chuyển về ma trận TOWS ở Bước 4.")
    
    st.markdown("### Quét dữ liệu PESTLE")
    
    # Tạo Form nhập liệu
    with st.form("pestle_form", clear_on_submit=True):
        col_input1, col_input2 = st.columns([2, 1])
        with col_input1:
            factor = st.text_input("Nhập một yếu tố thị trường (VD: Lãi suất ngân hàng giảm, Xu hướng AI...)")
        with col_input2:
            category = st.selectbox("Nhóm yếu tố", ["Political", "Economic", "Social", "Technological", "Legal", "Environmental"])
        
        impact = st.radio("Đánh giá tác động:", ["Cơ hội (Opportunity)", "Thách thức (Threat)"], horizontal=True)
        
        submitted = st.form_submit_button("Thêm vào Radar")
        
        # Xử lý khi bấm nút "Thêm vào Radar"
        if submitted and factor:
            formatted_factor = f"**[{category}]** {factor}"
            if "Cơ hội" in impact:
                st.session_state.opportunities.append(formatted_factor)
                st.success("Đã ghi nhận 1 Cơ hội!")
            else:
                st.session_state.threats.append(formatted_factor)
                st.error("Đã ghi nhận 1 Thách thức!")

    # Hiển thị dữ liệu ngay bên dưới
    st.markdown("### Dữ liệu đã thu thập")
    col_o, col_t = st.columns(2)
    with col_o:
        st.info("🟢 CƠ HỘI (Opportunities)")
        for o in st.session_state.opportunities:
            st.write("✓", o)
            
    with col_t:
        st.warning("🔴 THÁCH THỨC (Threats)")
        for t in st.session_state.threats:
            st.write("⚠️", t)

elif st.session_state.step == 2:
    st.subheader("Bước 2: Enterprise DNA")
    st.write("Tính năng đang được xây dựng...")
    
elif st.session_state.step == 4:
    st.subheader("Bước 4: TOWS Matrix (Bản xem trước)")
    st.write("Đây là minh chứng cho việc dữ liệu chảy xuyên suốt. Các yếu tố vĩ mô bạn vừa nhập ở Bước 1 đã tự động bay về đây!")
    st.write("---")
    st.write("🟢 **Danh sách Cơ hội (O):**")
    for o in st.session_state.opportunities:
        st.write("-", o)
    st.write("🔴 **Danh sách Thách thức (T):**")
    for t in st.session_state.threats:
        st.write("-", t)
