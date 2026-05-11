import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import date
import PyPDF2
import io

# ==========================================
# 1. CẤU HÌNH TRANG & CSS UI/UX CHUYÊN NGHIỆP
# ==========================================
st.set_page_config(page_title="Pro Career Strategy", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
    .auth-container {
        max-width: 450px; margin: auto; padding: 3rem 2rem;
        background: white; border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-top: 6px solid #2563eb;
    }
    .app-card {
        background: white; padding: 2rem; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    .stButton>button[kind="primary"] {
        background: #2563eb; color: white; border-radius: 8px;
        padding: 0.6rem 1.2rem; font-weight: 600; width: 100%; border: none;
        transition: all 0.3s ease;
    }
    .stButton>button[kind="primary"]:hover { background: #1d4ed8; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); }
    .stTextInput>div>div>input { border-radius: 8px; border: 1px solid #cbd5e1; padding: 0.75rem; }
    .stTextInput>div>div>input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }
    .tag-o { color: #047857; font-weight: 600; }
    .tag-t { color: #b91c1c; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CẤU HÌNH FIREBASE AUTHENTICATION
# ==========================================
FIREBASE_WEB_API_KEY = "AIzaSyD00faEnc-wexp9f3UIdfSJFrMZwNOFm7A"

def firebase_auth(email, password, is_signup=False):
    if is_signup:
        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    else:
        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(endpoint, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        return {"error": {"message": str(e)}}

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
        text = "".join(page.extract_text() for page in reader.pages)
        return text
    except Exception as e:
        return f"Lỗi đọc file: {e}"

# ==========================================
# 3. STATE MANAGEMENT
# ==========================================
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        "step": 0, "industry": "Tài chính / Ngân hàng", "company": "Techcombank",
        "opportunities": [], "threats": [], "strengths": [], "weaknesses": [],
        "tows": {"SO": "", "ST": "", "WO": "", "WT": ""}, "smart_goals": [],
        "file_content": "", "ai_feedbacks": {}
    }

def set_step(step): st.session_state.app_state["step"] = step

# ==========================================
# 4. LUỒNG XÁC THỰC (LOGIN / SIGNUP UI)
# ==========================================
if not st.session_state.user_token:
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1e293b;'>Chiến Lược Sự Nghiệp</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Hệ thống phân tích độc quyền</p>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký"])
    
    with tab_login:
        with st.form("login_form"):
            email_login = st.text_input("Email")
            pwd_login = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("Truy cập hệ thống", type="primary"):
                res = firebase_auth(email_login, pwd_login, is_signup=False)
                if "idToken" in res:
                    st.session_state.user_token = res["idToken"]
                    st.session_state.user_email = res["email"]
                    st.rerun()
                else:
                    st.error(f"Đăng nhập thất bại: {res.get('error', {}).get('message', 'Sai thông tin')}")
                    
    with tab_signup:
        with st.form("signup_form"):
            email_signup = st.text_input("Email của bạn")
            pwd_signup = st.text_input("Mật khẩu (Tối thiểu 6 ký tự)", type="password")
            if st.form_submit_button("Tạo tài khoản mới", type="primary"):
                res = firebase_auth(email_signup, pwd_signup, is_signup=True)
                if "idToken" in res:
                    st.success("🎉 Đăng ký thành công! Hãy chuyển sang tab Đăng Nhập.")
                else:
                    st.error(f"Đăng ký thất bại: {res.get('error', {}).get('message', 'Lỗi không xác định')}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. LUỒNG ỨNG DỤNG CHÍNH (MAIN APP)
# ==========================================
st.set_page_config(initial_sidebar_state="expanded") 

with st.sidebar:
    st.markdown(f"👤 **Xin chào:** `{st.session_state.user_email.split('@')[0]}`")
    if st.button("🚪 Đăng xuất"):
        st.session_state.user_token = None
        st.rerun()
        
    st.markdown("### ⚙️ Cài Đặt AI")
    api_key = st.text_input("🔑 Google Gemini API Key:", type="password")
    
    st.markdown("### 📄 Đọc Tài Liệu (JD/Báo Cáo)")
    uploaded_file = st.file_uploader("Tải lên PDF/TXT", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.name.endswith('.pdf'):
            st.session_state.app_state["file_content"] = doc_file_pdf(uploaded_file)
        else:
            st.session_state.app_state["file_content"] = uploaded_file.read().decode("utf-8")
        st.success("✅ AI đã ghi nhớ tài liệu!")
        
    st.markdown("---")
    st.markdown("### 🗺️ Điều hướng")
    if st.button("📖 Hướng Dẫn (Onboarding)", use_container_width=True): set_step(0)
    steps = ["1. Radar Thị Trường", "2. DNA Doanh Nghiệp", "3. Năng Lực Cá Nhân", "4. Ma Trận TOWS", "5. Xuất Báo Cáo"]
    for i, name in enumerate(steps, 1):
        if st.button(name, use_container_width=True, type="primary" if st.session_state.app_state["step"] == i else "secondary"):
            set_step(i)

step = st.session_state.app_state["step"]

# ------------------------------------------
# ONBOARDING (HƯỚNG DẪN)
# ------------------------------------------
if step == 0:
    st.markdown("<div class='app-card'><h1>🎓 Tổng Quan Tư Duy Chiến Lược</h1><p>Hệ thống ép bạn tư duy theo khung logic khắt khe của các tập đoàn lớn.</p></div>", unsafe_allow_html=True)
    with st.expander("📌 BƯỚC 1: PESTLE & Phân tích Vĩ mô", expanded=True):
        st.write("**Mục tiêu:** Quét yếu tố vĩ mô tác động đến ngành. Không đưa cảm tính cá nhân. Ví dụ: Dòng vốn FDI tăng là Cơ hội (O).")
    with st.expander("📌 BƯỚC 2: Mô hình VRIO"):
        st.write("**Mục tiêu:** Đánh giá lợi thế doanh nghiệp có bền vững không (Có Giá trị? Có Hiếm không?).")
    with st.expander("📌 BƯỚC 4: Ma Trận Giao Thoa TOWS"):
        st.write("Trái tim của hệ thống. Kết hợp (S-O) để Tấn công, (W-T) để Phòng thủ.")
    if st.button("🚀 Bắt Đầu Phân Tích", type="primary"):
        set_step(1)
        st.rerun()

# ------------------------------------------
# BƯỚC 1: RADAR THỊ TRƯỜNG
# ------------------------------------------
elif step == 1:
    st.markdown("<div class='app-card'><h2>🌍 Bước 1: Radar Thị Trường</h2><p>Quét các yếu tố vĩ mô để tìm kiếm Cơ hội và Thách thức từ bên ngoài.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    st.session_state.app_state["industry"] = col1.text_input("🏢 Ngành mục tiêu:", st.session_state.app_state["industry"])
    st.session_state.app_state["company"] = col2.text_input("🎯 Doanh nghiệp mục tiêu:", st.session_state.app_state["company"])

    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    if st.session_state.app_state["file_content"]:
        if st.button("✨ AI trích xuất Cơ hội/Thách thức từ File", type="primary"):
            with st.spinner("AI đang quét tài liệu..."):
                prompt = f"Từ tài liệu: {st.session_state.app_state['file_content'][:2000]}... Hãy liệt kê 2 Cơ hội và 2 Thách thức cho ngành {st.session_state.app_state['industry']}. Ngắn gọn."
                st.info(hoi_ai(prompt, api_key))

    c1, c2, c3 = st.columns([3, 1, 1])
    factor = c1.text_input("Yếu tố Vĩ mô (VD: Tín dụng xanh tăng trưởng):")
    cat = c2.selectbox("Phân loại:", ["Chính trị", "Kinh tế", "Xã hội", "Công nghệ", "Pháp lý", "Môi trường"])
    impact = c3.radio("Đánh giá:", ["🟢 Cơ hội (O)", "🔴 Thách thức (T)"])
    
    if st.button("💾 Lưu Yếu Tố", type="primary"):
        if factor:
            item = f"[{cat}] {factor}"
            if "Cơ hội" in impact: st.session_state.app_state["opportunities"].append(item)
            else: st.session_state.app_state["threats"].append(item)
            st.toast("Đã lưu dữ liệu vĩ mô!", icon="✅")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 2: DNA DOANH NGHIỆP
# ------------------------------------------
elif step == 2:
    st.markdown("<div class='app-card'><h2>🧬 Bước 2: DNA Doanh Nghiệp (VRIO)</h2></div>", unsafe_allow_html=True)
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    resource = st.text_input("💡 Nguồn lực cốt lõi của DN (VD: Hệ thống lõi ngân hàng hiện đại):")
    v = st.checkbox("✅ Tạo ra giá trị rõ ràng (Valuable)?")
    r = st.checkbox("💎 Hiếm có, đối thủ khó sao chép (Rare)?")
    
    if st.button("💾 Đánh giá & Lưu", type="primary"):
        if resource:
            if v and r: st.session_state.app_state["strengths"].append(f"[DN] Lợi thế: {resource}")
            else: st.session_state.app_state["weaknesses"].append(f"[DN] Hạn chế: {resource}")
            st.toast("Đã cập nhật DNA doanh nghiệp!", icon="🧬")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 3: NĂNG LỰC CÁ NHÂN
# ------------------------------------------
elif step == 3:
    st.markdown("<div class='app-card'><h2>🧠 Bước 3: Năng Lực Cốt Lõi (STAR)</h2></div>", unsafe_allow_html=True)
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    skill = st.text_input("🎯 Kỹ năng của bạn (VD: Mô hình hóa tài chính, Tiếng Anh):")
    level = st.radio("Mức độ thành thạo:", ["🌟 Điểm mạnh (S)", "⚠️ Cần cải thiện (W)"], horizontal=True)
    
    if st.button("💾 Nạp Kỹ Năng", type="primary"):
        if skill:
            if "S" in level: st.session_state.app_state["strengths"].append(f"[Cá nhân] {skill}")
            else: st.session_state.app_state["weaknesses"].append(f"[Cá nhân] {skill}")
            st.toast("Đã lưu kỹ năng!", icon="🎯")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 4: CHIẾN LƯỢC TOWS
# ------------------------------------------
elif step == 4:
    st.markdown("<div class='app-card'><h2>⚔️ Bước 4: Ma Trận Chiến Lược TOWS</h2></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"💪 **Điểm mạnh (S):**\n" + "\n".join([f"- {s}" for s in st.session_state.app_state['strengths']]))
        st.success(f"🚀 **Cơ hội (O):**\n" + "\n".join([f"- {o}" for o in st.session_state.app_state['opportunities']]))
    with c2:
        st.warning(f"📉 **Điểm yếu (W):**\n" + "\n".join([f"- {w}" for w in st.session_state.app_state['weaknesses']]))
        st.error(f"⚠️ **Thách thức (T):**\n" + "\n".join([f"- {t}" for t in st.session_state.app_state['threats']]))
    
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.session_state.app_state["tows"]["SO"] = st.text_area("🔥 Chiến lược Tấn công (SO - Dùng Điểm mạnh chớp Cơ hội):", st.session_state.app_state["tows"]["SO"])
    st.session_state.app_state["tows"]["WT"] = st.text_area("🛡️ Chiến lược Phòng thủ (WT - Sửa Điểm yếu để né Thách thức):", st.session_state.app_state["tows"]["WT"])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# BƯỚC 5: BÁO CÁO THỰC THI
# ------------------------------------------
elif step == 5:
    st.markdown("<div class='app-card'><h2>🏆 Bước 5: Báo Cáo & Lộ Trình</h2></div>", unsafe_allow_html=True)
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    goal = st.text_area("🎯 Viết mục tiêu hành động cụ thể (SMART):")
    
    if st.button("💾 Thêm Mục Tiêu", type="primary"):
        if goal:
            st.session_state.app_state["smart_goals"].append(goal)
            st.toast("Đã thêm vào lộ trình!", icon="🚀")
            
    if st.button("🤖 AI Chuẩn hóa mục tiêu", type="secondary"):
        if goal:
            with st.spinner("AI đang kiểm tra tính khả thi..."):
                prompt = f"Hãy sửa mục tiêu '{goal}' thành mục tiêu chuẩn SMART. Dưới 50 từ."
                st.info(hoi_ai(prompt, api_key))
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.app_state["smart_goals"]:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #1e293b;'>BẢN TÓM TẮT CHIẾN LƯỢC: {st.session_state.app_state['company'].upper()}</h3>", unsafe_allow_html=True)
        st.markdown("---")
        for idx, g in enumerate(st.session_state.app_state["smart_goals"], 1):
            st.write(f"**{idx}.** {g}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🎉 Hoàn Thành Báo Cáo", type="primary"):
            st.balloons()
            st.success("Tuyệt vời! Báo cáo của bạn đã sẵn sàng.")
