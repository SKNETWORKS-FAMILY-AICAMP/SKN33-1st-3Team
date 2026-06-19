import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

df = pd.read_csv(DATA_DIR / '한국교통안전공단_차종별 리콜대수_20251231.csv', encoding='cp949')

manufacturer_df = df[['제작자']].drop_duplicates().reset_index(drop=True)
manufacturer_df['manufacturer_id'] = manufacturer_df.index + 1
manufacturer_df.columns = ['name', 'manufacturer_id']
manufacturer_df = manufacturer_df[['manufacturer_id', 'name']]

manufacturer_df.to_csv(DATA_DIR / 'manufacturer_df.csv', index=False, encoding='utf-8-sig')
print(f'총 {len(manufacturer_df)}개 제조사 저장 완료')
print(manufacturer_df.head(10))