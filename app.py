import streamlit as st

st.set_page_config(page_title="자동차 리콜 서비스", page_icon="🚗", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1B2A4A !important; }
[data-testid="stSidebarNav"]::before {
    content: "📡 Recall Radar";
    display: block;
    font-size: 1.1rem;
    font-weight: 700;
    color: white;
    padding: 1.2rem 1rem 0.2rem;
}
[data-testid="stSidebarNav"]::after {
    content: "Recall Safety Platform";
    display: block;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.45);
    padding: 0 1rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 0.4rem;
}
[data-testid="stSidebarNav"] a { color: rgba(255,255,255,0.8) !important; border-radius: 8px; padding: 0.4rem 0.8rem; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,107,53,0.2) !important; color: white !important; }
[data-testid="stSidebarNav"] a[aria-selected="true"] { background: #FF6B35 !important; color: white !important; font-weight: 700; }
[data-testid="stSidebar"] span { color: rgba(255,255,255,0.8) !important; }
div.stButton > button { background-color: #FF6B35 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
div.stButton > button:hover { background-color: #e85a25 !important; }
</style>
""", unsafe_allow_html=True)

home     = st.Page("pages/home.py",           title="HOME",      icon="🏠")
recall   = st.Page("pages/recall.py",         title="리콜 조회",  icon="🔍")
analysis = st.Page("pages/analysis.py",       title="데이터 분석", icon="📊")
service  = st.Page("pages/service_center.py", title="서비스센터",  icon="📍")
news     = st.Page("pages/news.py",           title="뉴스",       icon="📰")
faq      = st.Page("pages/faq.py",            title="FAQ",        icon="❓")

pg = st.navigation([home, recall, analysis, service, news, faq])
pg.run()
