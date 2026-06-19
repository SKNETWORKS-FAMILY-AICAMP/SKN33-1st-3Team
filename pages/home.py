import streamlit as st



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

[data-testid="stSidebar"] { background: #1B2A4A !important; }
[data-testid="stSidebarNav"] a { color: rgba(255,255,255,0.8) !important; border-radius: 8px; padding: 0.4rem 0.8rem; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,107,53,0.2) !important; color: white !important; }
[data-testid="stSidebarNav"] a[aria-selected="true"] { background: #FF6B35 !important; color: white !important; font-weight: 700; }
[data-testid="stSidebar"] span { color: rgba(255,255,255,0.8) !important; }

div.stButton > button {
    background-color: #FF6B35 !important; color: white !important;
    border: none !important; border-radius: 8px !important; font-weight: 600 !important;
}
div.stButton > button:hover { background-color: #e85a25 !important; }

.hero {
    background: linear-gradient(135deg, #1B2A4A 0%, #2d4270 100%);
    border-radius: 16px; padding: 3.5rem 2.5rem;
    color: white; text-align: center; margin-bottom: 2rem;
}
.hero-title { font-size: 2.4rem; font-weight: 700; margin-bottom: 0.5rem; }
.hero-sub { font-size: 1rem; opacity: 0.75; }

.card {
    background: #f8f9fc; border-radius: 14px;
    padding: 1.8rem 1.5rem; border-top: 4px solid #FF6B35;
    text-align: center; height: 170px;
}
.card-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.card-title { font-size: 1rem; font-weight: 700; color: #1B2A4A; margin-bottom: 0.3rem; }
.card-desc { font-size: 0.82rem; color: #888; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

_, col_c, _ = st.columns([1, 4, 1])
with col_c:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">📡 Recall Radar</div>
        <div class="hero-sub">내 차의 리콜 여부를 확인하고, 가까운 서비스센터를 찾아보세요</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
cards = [
    (col1, "🔍", "리콜 조회", "브랜드와 차종을 선택해 리콜 대상 여부를 확인하세요", "리콜 조회하기", "pages/recall.py"),
    (col2, "📊", "데이터 분석", "제조사별, 연도별 리콜 현황을 파악하세요", "분석 보기", "pages/analysis.py"),
    (col3, "📍", "서비스센터", "내 지역 근처 서비스센터를 찾아보세요", "센터 찾기", "pages/service_center.py"),
    (col4, "📰", "리콜 뉴스", "최신 자동차 리콜 관련 뉴스를 확인하세요", "뉴스 보기", "pages/news.py"),
]

for col, icon, title, desc, btn, page in cards:
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button(btn, use_container_width=True, key=page):
            st.switch_page(page)
