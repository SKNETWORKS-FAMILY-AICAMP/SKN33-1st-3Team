import streamlit as st
import mysql.connector
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
[data-testid="stSidebar"] { background: #1B2A4A !important; }
[data-testid="stSidebarNav"] a { color: rgba(255,255,255,0.8) !important; border-radius: 8px; padding: 0.4rem 0.8rem; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,107,53,0.2) !important; color: white !important; }
[data-testid="stSidebarNav"] a[aria-selected="true"] { background: #FF6B35 !important; color: white !important; font-weight: 700; }
[data-testid="stSidebar"] span { color: rgba(255,255,255,0.8) !important; }
div.stButton > button { background-color: #FF6B35 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
div.stButton > button:hover { background-color: #e85a25 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.page-title { font-size: 1.8rem; font-weight: 700; color: #1B2A4A; margin-bottom: 0.3rem; }
.page-sub { font-size: 0.9rem; color: #888; margin-bottom: 1.5rem; }
.news-card {
    background: #f8f9fc;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.4rem 0;
    border-left: 4px solid #FF6B35;
    transition: background 0.2s;
}
.news-title a {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1B2A4A;
    text-decoration: none;
}
.news-title a:hover { color: #FF6B35; }
.news-meta { font-size: 0.8rem; color: #aaa; margin-top: 0.3rem; }
</style>
""", unsafe_allow_html=True)

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
    )

@st.cache_data
def load_manufacturers():
    conn = get_conn()
    df = pd.read_sql("SELECT manufacturer_id, name FROM manufacturer ORDER BY name", conn)
    conn.close()
    return df

@st.cache_data
def load_cars(manufacturer_id):
    conn = get_conn()
    df = pd.read_sql(
        f"SELECT car_id, model_name FROM car WHERE manufacturer_id = {manufacturer_id} ORDER BY model_name",
        conn
    )
    conn.close()
    return df

def search_news(keyword=None, car_id=None):
    conn = get_conn()
    if car_id:
        query = f"""
            SELECT n.news_title, n.news_link, c.model_name, m.name AS manufacturer
            FROM news n
            JOIN car c ON n.car_id = c.car_id
            JOIN manufacturer m ON c.manufacturer_id = m.manufacturer_id
            WHERE n.car_id = {car_id}
            LIMIT 30
        """
    elif keyword:
        query = f"""
            SELECT n.news_title, n.news_link, c.model_name, m.name AS manufacturer
            FROM news n
            JOIN car c ON n.car_id = c.car_id
            JOIN manufacturer m ON c.manufacturer_id = m.manufacturer_id
            WHERE n.news_title LIKE '%{keyword}%'
            LIMIT 30
        """
    else:
        query = """
            SELECT n.news_title, n.news_link, c.model_name, m.name AS manufacturer
            FROM news n
            JOIN car c ON n.car_id = c.car_id
            JOIN manufacturer m ON c.manufacturer_id = m.manufacturer_id
            LIMIT 30
        """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ── 타이틀 ───────────────────────────────────────────────
st.markdown('<div class="page-title">📰 리콜 뉴스</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">자동차 리콜 관련 최신 뉴스를 확인하세요</div>', unsafe_allow_html=True)

# ── 검색 탭 ──────────────────────────────────────────────
tab1, tab2 = st.tabs(["🔍 키워드 검색", "🚗 차종별 검색"])

with tab1:
    keyword = st.text_input("검색어 입력", placeholder="예: 현대, 에어백, 제동장치")
    if st.button("검색", key="keyword_search", type="primary"):
        news = search_news(keyword=keyword)
        st.markdown(f"**{len(news)}건** 검색됨")
        if len(news) == 0:
            st.info("검색 결과가 없습니다.")
        else:
            for _, row in news.iterrows():
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">
                        <a href="{row['news_link']}" target="_blank">📌 {row['news_title']}</a>
                    </div>
                    <div class="news-meta">{row['manufacturer']} · {row['model_name']}</div>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    manufacturers = load_manufacturers()
    col1, col2 = st.columns(2)

    with col1:
        selected_mfr = st.selectbox("제조사", manufacturers['name'].tolist(),
                                    index=None, placeholder="제조사를 선택하세요", key="news_mfr")
    with col2:
        if selected_mfr:
            mfr_id = int(manufacturers[manufacturers['name'] == selected_mfr]['manufacturer_id'].values[0])
            cars = load_cars(mfr_id)
            selected_car = st.selectbox("차종", cars['model_name'].tolist(),
                                        index=None, placeholder="차종을 선택하세요", key="news_car")
        else:
            st.selectbox("차종", [], placeholder="제조사를 먼저 선택하세요", disabled=True, key="news_car_disabled")
            selected_car = None

    if st.button("검색", key="car_search", type="primary"):
        if selected_mfr and selected_car:
            car_id = int(cars[cars['model_name'] == selected_car]['car_id'].values[0])
            news = search_news(car_id=car_id)
            st.markdown(f"**{selected_mfr} {selected_car}** 관련 뉴스 **{len(news)}건**")
            if len(news) == 0:
                st.info("관련 뉴스가 없습니다.")
            else:
                for _, row in news.iterrows():
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">
                            <a href="{row['news_link']}" target="_blank">📌 {row['news_title']}</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("제조사와 차종을 모두 선택해주세요.")
