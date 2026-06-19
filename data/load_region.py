import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent

df = pd.read_csv(DATA_DIR / '국토교통부_전국 법정동_20260609.csv', encoding='utf-8')

today = datetime.today()
df['삭제일자'] = pd.to_datetime(df['삭제일자'], errors='coerce')
df = df[df['삭제일자'].isna() | (df['삭제일자'] > today)]

region_df = df[['시도명', '시군구명']].drop_duplicates()
region_df = region_df.dropna(subset=['시군구명'])
region_df = region_df.reset_index(drop=True)
region_df['region_id'] = region_df.index + 1
region_df = region_df.rename(columns={'시도명': 'city', '시군구명': 'district'})
region_df = region_df[['region_id', 'city', 'district']]

region_df.to_csv(DATA_DIR / 'region_df.csv', index=False, encoding='utf-8-sig')
print(f'총 {len(region_df)}개 지역 저장 완료')
print(region_df.head(5))
