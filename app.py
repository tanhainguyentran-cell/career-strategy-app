import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="Executive Strategy Board", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A1A1A; }
    .stApp { background-color: #FAFAFA; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #0F172A; margin-bottom: 1rem; }
    .executive-card { background: white; padding: 2.5rem; border-radius: 2px; box-shadow: 0 10px 30px rgba(0,0,0,0.02); margin-bottom: 2rem; border: 1px solid #F0F0F0; border-top: 4px solid #D4AF37; }
    .auth-container { max-width: 420px; margin: 5rem auto; padding: 3rem 2rem; background: white; border-top: 4px solid #D4AF37; border-bottom: 4px solid #1A1A1A; box-shadow: 0 20px 40px rgba(0,0,0,0.05); }
    .stButton>button[kind="primary"] { background-color: #1A1A1A !important; color: white !important; border-radius: 0px !important; width: 100%; border: none !important; padding: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; transition: 0.4s; }
    .stButton>button[kind="primary"]:hover { background-color: #D4AF37 !important; transform: translateY(-2px); }
    .step-label { color: #D4AF37; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "AIzaSyCNigw85FMCdi0HsRI1RUU5lwwq1tNMOwg"

def call_ai_safe(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = response.json()
        
        if 'error' in res_data:
            return f"Lỗi từ Google API: {res_data['error'].get('message', 'Không rõ chi tiết')}"
            
        if 'candidates' in res_data and len(res_data['candidates']) > 0:
            text = res_data['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '')
            if text:
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except:
                        pass
                return text
        return "Hệ thống AI trả về dữ liệu rỗng."
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

FIREBASE_KEY = "AIzaSyD00faEnc-wexp9f3UIdfSJFrMZwNOFm7A"

def firebase_auth(email, password, is_signup=False):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{'signUp' if is_signup else 'signInWithPassword'}?key={FIREBASE_KEY}"
    try:
        res = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
        return res.json()
    except: return {"error": {"message": "Lỗi kết nối Server"}}

if 'state' not in st.session_state:
    st.session_state.state = {
        "logged_in": False, "email": "", "step": 1,
        "profile": {"info": "", "skills": ""},
        "goal": {"task": "", "time": ""},
        "feasibility": None, "sub_tasks": None, "final_roadmap": None
    }

if not st.session_state.state["logged_in"]:
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>STRATEGY PORTAL</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["ĐĂNG NHẬP", "ĐĂNG KÝ"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("TIẾP TỤC", type="primary"):
                res = firebase_auth(e, p)
                if "idToken" in res:
                    st.session_state.state["logged_in"] = True
                    st.session_state.state["email"] = res["email"]
                    st.rerun()
                else: st.error(res.get("error", {}).get("message", "Đăng nhập thất bại"))
    with t2:
        with st.form("signup"):
            es = st.text_input("Email")
            ps = st.text_input("Mật khẩu (6 ký tự)", type="password")
            if st.form_submit_button("TẠO TÀI KHOẢN", type="primary"):
                res = firebase_auth(es, ps, True)
                if "idToken" in res: st.success("Đã tạo tài khoản thành công!")
                else: st.error(res.get("error", {}).get("message", "Đăng ký thất bại"))
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

step = st.session_state.state["step"]

with st.sidebar:
    st.markdown("<h3 style='color: #D4AF37;'>EXECUTIVE BOARD</h3>", unsafe_allow_html=True)
    st.write(f"👤 {st.session_state.state['email']}")
    if st.button("ĐĂNG XUẤT"):
        st.session_state.state["logged_in"] = False
        st.rerun()

if step == 1:
    st.markdown("<div class='executive-card'><p class='step-label'>GIAI ĐOẠN 01</p><h1>Thiết lập Hồ sơ & Mục tiêu</h1>", unsafe_allow_html=True)
    
    with st.form("step1"):
        col1, col2 = st.columns(2)
        info = col1.text_input("Vị trí & Trình độ:", placeholder="VD: Sinh viên năm 3 - DAV")
        skills = col2.text_input("Năng lực & Bằng cấp:", placeholder="VD: IELTS 7.5, Python, CFA")
        
        st.markdown("---")
        target = st.text_area("Mục tiêu cụ thể:", placeholder="VD: Trúng tuyển thực tập sinh Techcombank")
        deadline = st.text_input("Thời gian thực hiện:", placeholder="VD: 4 tháng")
        
        if st.form_submit_button("THẨM ĐỊNH CHIẾN LƯỢC", type="primary"):
            if target and deadline:
                with st.spinner("AI đang thẩm định tính khả thi..."):
                    prompt = f"Hồ sơ: {info}, Kỹ năng: {skills}. Mục tiêu: {target} trong {deadline}. Hãy thẩm định tính khả thi. Nếu phi lý (như trúng số), hãy giải thích và từ chối. Nếu thực tế, nhận xét ngắn gọn. Dưới 100 chữ tiếng Việt."
                    st.session_state.state["feasibility"] = call_ai_safe(prompt)
                    st.session_state.state["profile"] = {"info": info, "skills": skills}
                    st.session_state.state["goal"] = {"task": target, "time": deadline}
            else: st.warning("Vui lòng điền đủ thông tin.")
    
    if st.session_state.state["feasibility"]:
        st.markdown(f"<div class='executive-card'><h3>Phản hồi từ Mentor AI</h3><p>{st.session_state.state['feasibility']}</p></div>", unsafe_allow_html=True)
        if "Lỗi từ Google API" not in st.session_state.state["feasibility"] and "phi thực tế" not in st.session_state.state["feasibility"].lower():
            if st.button("XÁC NHẬN & VẠCH LỘ TRÌNH"): 
                st.session_state.state["step"] = 2
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif step == 2:
    st.markdown("<div class='executive-card'><p class='step-label'>GIAI ĐOẠN 02</p><h1>Phân rã Hạng mục Thực thi</h1>", unsafe_allow_html=True)
    
    if not st.session_state.state["sub_tasks"]:
        with st.spinner("AI đang bóc tách lộ trình..."):
            prompt = f"Mục tiêu: {st.session_state.state['goal']['task']} trong {st.session_state.state['goal']['time']}. Vạch ra 4 hạng mục nhỏ cần chuẩn bị (Kiến thức, Kỹ năng, Công cụ, Network). Trả về JSON: {{\\\"items\\\": {{\\\"Tên mục\\\": \\\"Gợi ý chi tiết\\\"}}}}"
            st.session_state.state["sub_tasks"] = call_ai_safe(prompt)
    
    if isinstance(st.session_state.state["sub_tasks"], dict):
        for item, detail in st.session_state.state["sub_tasks"].get("items", {}).items():
            st.subheader(f"📍 {item}")
            st.text_area(f"Ghi chú cho {item}:", value=detail, height=100)
    elif isinstance(st.session_state.state["sub_tasks"], str):
        st.write(st.session_state.state["sub_tasks"])
    
    if st.button("XUẤT BÁO CÁO CUỐI CÙNG", type="primary"):
        st.session_state.state["step"] = 3
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif step == 3:
    st.markdown("<div style='text-align: center;'><h1>BẢN ĐỒ CHIẾN LƯỢC THỰC THI</h1><p>Executive Personal Roadmap</p></div>", unsafe_allow_html=True)
    
    if not st.session_state.state["final_roadmap"]:
        with st.spinner("Đang đúc kết báo cáo..."):
            prompt = f"Hồ sơ: {st.session_state.state['profile']}. Mục tiêu: {st.session_state.state['goal']}. Lập 1 lộ trình hành động chuyên nghiệp, chia theo giai đoạn. Định dạng Markdown."
            st.session_state.state["final_roadmap"] = call_ai_safe(prompt)
            
    st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
    st.markdown(st.session_state.state["final_roadmap"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("LÀM MỚI CHIẾN LƯỢC"):
        st.session_state.state["step"] = 1
        st.session_state.state["sub_tasks"] = None
        st.session_state.state["final_roadmap"] = None
        st.session_state.state["feasibility"] = None
        st.rerun()
