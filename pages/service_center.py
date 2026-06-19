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
.page-title { font-size: 1.8rem; font-weight: 700; color: #1B2A4A; margin-bottom: 0.3rem; }
.page-sub { font-size: 0.9rem; color: #888; margin-bottom: 1.5rem; }
.center-card { background: #f8f9fc; border-radius: 10px; padding: 0.9rem 1.2rem; margin: 0.3rem 0; border-left: 4px solid #FF6B35; }
.center-name { font-size: 0.95rem; font-weight: 700; color: #1B2A4A; }
.center-info { font-size: 0.82rem; color: #666; margin-top: 0.3rem; }
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
def load_regions():
    conn = get_conn()
    df = pd.read_sql("SELECT region_id, city, district FROM region ORDER BY city, district", conn)
    conn.close()
    return df

def load_manufacturers_by_region(region_id=None):
    conn = get_conn()
    if region_id:
        query = f"""
            SELECT DISTINCT m.manufacturer_id, m.name
            FROM service_center s
            JOIN manufacturer m ON s.manufacturer_id = m.manufacturer_id
            WHERE s.region_id = {region_id}
            ORDER BY m.name
        """
    else:
        query = """
            SELECT DISTINCT m.manufacturer_id, m.name
            FROM service_center s
            JOIN manufacturer m ON s.manufacturer_id = m.manufacturer_id
            ORDER BY m.name
        """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_centers(region_id=None, city_region_ids=None, manufacturer_id=None):
    conn = get_conn()
    conditions = []
    if region_id is not None:
        conditions.append(f"s.region_id = {region_id}")
    elif city_region_ids:
        ids = ",".join(map(str, city_region_ids))
        conditions.append(f"s.region_id IN ({ids})")
    if manufacturer_id is not None:
        conditions.append(f"s.manufacturer_id = {manufacturer_id}")
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"SELECT s.center_name, s.address, s.phone, s.latitude, s.longitude, m.name AS manufacturer FROM service_center s JOIN manufacturer m ON s.manufacturer_id = m.manufacturer_id {where} ORDER BY m.name, s.center_name"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.markdown('<div class="page-title">📍 가까운 서비스센터 찾기</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">지역을 선택하면 해당 지역의 서비스센터를 확인할 수 있습니다</div>', unsafe_allow_html=True)

regions = load_regions()
col1, col2, col3 = st.columns(3)

with col1:
    cities = ["전체"] + sorted(regions['city'].unique().tolist())
    selected_city = st.selectbox("🏙️ 시/도", cities)

with col2:
    if selected_city != "전체":
        districts = ["전체"] + sorted(regions[regions['city'] == selected_city]['district'].tolist())
        selected_district = st.selectbox("🏘️ 구/군", districts)
    else:
        selected_district = st.selectbox("🏘️ 구/군", ["전체"], disabled=True)

region_id = None
city_region_ids = None

if selected_city != "전체" and selected_district != "전체":
    region_id = int(regions[
        (regions['city'] == selected_city) &
        (regions['district'] == selected_district)
    ]['region_id'].values[0])
elif selected_city != "전체":
    city_region_ids = regions[regions['city'] == selected_city]['region_id'].tolist()

with col3:
    mfr_df = load_manufacturers_by_region(region_id)
    mfr_options = ["전체"] + mfr_df['name'].tolist()
    selected_mfr = st.selectbox("🏭 제조사", mfr_options)

mfr_id = None
if selected_mfr != "전체":
    mfr_id = int(mfr_df[mfr_df['name'] == selected_mfr]['manufacturer_id'].values[0])

if selected_city == "전체":
    st.info("시/도를 선택하면 서비스센터 목록을 확인할 수 있습니다.")
else:
    centers = load_centers(region_id=region_id, city_region_ids=city_region_ids, manufacturer_id=mfr_id)
    if selected_district != "전체":
        label = f"{selected_city} {selected_district}"
        show_map = True
    else:
        label = selected_city
        show_map = False

    st.markdown(f"<br>**{label}** 서비스센터 **{len(centers)}개**", unsafe_allow_html=True)

    if len(centers) == 0:
        st.info("해당 지역에 서비스센터가 없습니다.")
    else:
        if show_map:
            map_data = centers.dropna(subset=['latitude', 'longitude'])[['latitude', 'longitude']]
            if len(map_data) > 0:
                st.map(map_data, zoom=12)
            st.markdown("<br>", unsafe_allow_html=True)

        for _, row in centers.iterrows():
            name = row['center_name'] or "센터명 없음"
            address = row['address'] or "주소 없음"
            phone = row['phone'] or "전화번호 없음"
            st.markdown(f"""
            <div class="center-card">
                <div class="center-name">🔧 {name}</div>
                <div class="center-info">🏭 {row['manufacturer']} &nbsp;|&nbsp; 📌 {address} &nbsp;|&nbsp; 📞 {phone}</div>
            </div>
            """, unsafe_allow_html=True)
