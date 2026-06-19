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
.result-box { border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }
.result-recall { background: #fff3f3; border-left: 5px solid #FF6B35; }
.result-safe { background: #f0fff4; border-left: 5px solid #38a169; }
.result-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; }
.recall-item { background: white; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border: 1px solid #f0e0d6; }
.recall-date { font-size: 0.78rem; color: #888; }
.recall-reason { font-size: 0.9rem; color: #333; margin-top: 0.3rem; line-height: 1.6; }
.news-item { background: #f8f9fc; border-radius: 8px; padding: 0.8rem 1rem; margin: 0.4rem 0; }
.news-title { font-size: 0.9rem; color: #1B2A4A; font-weight: 500; }
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

def search_recall(car_id):
    conn = get_conn()
    df = pd.read_sql(
        f"""SELECT recall_date, recall_count, recall_reason, prod_start, prod_end
            FROM recall WHERE car_id = {car_id}
            ORDER BY recall_date DESC""",
        conn
    )
    conn.close()
    return df

def load_news(car_id):
    conn = get_conn()
    df = pd.read_sql(
        f"SELECT news_title, news_link FROM news WHERE car_id = {car_id} LIMIT 10",
        conn
    )
    conn.close()
    return df

# ── 타이틀 ───────────────────────────────────────────────
st.markdown('<div class="page-title">🔍 내 차 리콜 조회</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">브랜드와 차종을 선택해 리콜 대상 여부를 확인하세요</div>', unsafe_allow_html=True)

# ── 선택 UI ──────────────────────────────────────────────
manufacturers = load_manufacturers()
col1, col2 = st.columns(2)

with col1:
    selected_mfr_name = st.selectbox(
        "🏭 제조사 선택",
        manufacturers['name'].tolist(),
        index=None,
        placeholder="제조사를 선택하세요"
    )

selected_car_id = None
selected_car_name = None

with col2:
    if selected_mfr_name:
        mfr_id = manufacturers[manufacturers['name'] == selected_mfr_name]['manufacturer_id'].values[0]
        cars = load_cars(int(mfr_id))
        selected_car_name = st.selectbox(
            "🚗 차종 선택",
            cars['model_name'].tolist(),
            index=None,
            placeholder="차종을 선택하세요"
        )
        if selected_car_name:
            selected_car_id = int(cars[cars['model_name'] == selected_car_name]['car_id'].values[0])
    else:
        st.selectbox("🚗 차종 선택", [], placeholder="제조사를 먼저 선택하세요", disabled=True)

# ── 조회 버튼 ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
search_btn = st.button("🔍 리콜 조회", type="primary", disabled=(selected_car_id is None), use_container_width=False)

# ── 결과 ─────────────────────────────────────────────────
if search_btn and selected_car_id:
    recalls = search_recall(selected_car_id)

    if len(recalls) > 0:
        st.markdown(f"""
        <div class="result-box result-recall">
            <div class="result-title">⚠️ 리콜 대상 차량입니다</div>
            <p style="color:#666;font-size:0.9rem;">
                <b>{selected_mfr_name} {selected_car_name}</b>에 대한 리콜 이력이 
                <b>{len(recalls)}건</b> 확인되었습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 리콜 이력")
        for _, row in recalls.iterrows():
            st.markdown(f"""
            <div class="recall-item">
                <div class="recall-date">
                    📅 리콜 개시일: {row['recall_date']} &nbsp;|&nbsp;
                    🏭 생산 기간: {row['prod_start']} ~ {row['prod_end']} &nbsp;|&nbsp;
                    🚗 리콜 대수: {int(row['recall_count']):,}대
                </div>
                <div class="recall-reason">{row['recall_reason']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── 관련 뉴스 ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📰 관련 뉴스 보기"):
            news = load_news(selected_car_id)
            if len(news) > 0:
                for _, row in news.iterrows():
                    st.markdown(f"""
                    <div class="news-item">
                        <a href="{row['news_link']}" target="_blank" class="news-title">
                            📌 {row['news_title']}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("관련 뉴스가 없습니다.")

    else:
        st.markdown(f"""
        <div class="result-box result-safe">
            <div class="result-title">✅ 리콜 대상이 아닙니다</div>
            <p style="color:#666;font-size:0.9rem;">
                <b>{selected_mfr_name} {selected_car_name}</b>에 대한 리콜 이력이 없습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
