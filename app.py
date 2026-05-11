import streamlit as st

st.set_page_config(page_title="Career Strategy", layout="wide")

# Khởi tạo bộ nhớ cho App
if 'step' not in st.session_state:
    st.session_state.step = 1

# Tiêu đề chính
st.title("🎯 Career Strategy Application")
st.markdown("---")

# Thanh điều hướng bên trái
with st.sidebar:
    st.header("Lộ trình 5 bước")
    if st.button("1. Market Radar"): st.session_state.step = 1
    if st.button("2. Enterprise DNA"): st.session_state.step = 2
    # Tương tự cho các bước khác...

# Hiển thị nội dung dựa trên bước hiện tại
if st.session_state.step == 1:
    st.subheader("Bước 1: Phân tích môi trường vĩ mô")
    st.write("Chào mừng bạn! Hãy bắt đầu phân tích thị trường tại đây.")
    # Sau này mình sẽ thêm form nhập liệu vào đây
