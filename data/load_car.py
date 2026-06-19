import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

df = pd.read_csv(DATA_DIR / '한국교통안전공단_차종별 리콜대수_20251231.csv', encoding='cp949')
manufacturer_df = pd.read_csv(DATA_DIR / 'manufacturer_df.csv', encoding='utf-8-sig')

car_df = df[['제작자', '차명']].drop_duplicates().reset_index(drop=True)
car_df['car_id'] = car_df.index + 1

car_df = car_df.merge(manufacturer_df[['manufacturer_id', 'name']], left_on='제작자', right_on='name', how='left')
car_df = car_df[['car_id', '차명', 'manufacturer_id']]
car_df.columns = ['car_id', 'model_name', 'manufacturer_id']

car_df.to_csv(DATA_DIR / 'car_df.csv', index=False, encoding='utf-8-sig')
print(f'총 {len(car_df)}개 차량 저장 완료')
print(car_df.head(10))
