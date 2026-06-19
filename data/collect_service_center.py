import requests
import pandas as pd
import time
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
BASE_URL = 'https://dapi.kakao.com/v2/local/search/keyword.json'

DATA_DIR = Path(__file__).resolve().parent

df_recall = pd.read_csv(DATA_DIR / '한국교통안전공단_차종별 리콜대수_20251231.csv', encoding='cp949')
brands = df_recall['제작자'].unique().tolist()

manufacturer_df = pd.read_csv(DATA_DIR / 'manufacturer_df.csv', encoding='utf-8-sig')
manufacturer_map = dict(zip(manufacturer_df['name'], manufacturer_df['manufacturer_id']))

region_df = pd.read_csv(DATA_DIR / 'region_df.csv', encoding='utf-8-sig')
region_df['search_query'] = region_df['city'] + ' ' + region_df['district']
region_map = dict(zip(region_df['search_query'], region_df['region_id']))
search_queries = region_df['search_query'].tolist()

rows = []

for brand in brands:
    for query in search_queries:
        page = 1
        while page <= 3:
            params = {
                'query': f'{brand} 서비스센터 {query}',
                'size': 15,
                'page': page
            }
            headers = {'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
            res = requests.get(BASE_URL, params=params, headers=headers)
            data = res.json()

            documents = data.get('documents', [])
            if not documents:
                break

            for doc in documents:
                rows.append({
                    'manufacturer_id': manufacturer_map.get(brand),
                    'center_name': doc['place_name'],
                    'address': doc['road_address_name'],
                    'phone': doc['phone'],
                    'latitude': float(doc['y']) if doc['y'] else None,
                    'longitude': float(doc['x']) if doc['x'] else None,
                    'region_id': region_map.get(query)
                })

            if data['meta']['is_end']:
                break

            page += 1
            time.sleep(0.3)

    print(f'{brand} 수집 완료')

df = pd.DataFrame(rows)
df = df.drop_duplicates(subset=['center_name', 'address'])
print(f'\n총 {len(df)}개 수집')

df.to_csv(DATA_DIR / 'service_center_df.csv', index=False, encoding='utf-8-sig')
print('CSV 저장 완료')
