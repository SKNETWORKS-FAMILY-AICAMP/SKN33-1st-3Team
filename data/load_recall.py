import pandas as pd
from pathlib import Path
from defect_classifier import classify_defect_id, write_defect_category_csv

DATA_DIR = Path(__file__).resolve().parent

df = pd.read_csv(DATA_DIR / '한국교통안전공단_차종별 리콜대수_20251231.csv', encoding='cp949')
car_df = pd.read_csv(DATA_DIR / 'car_df.csv', encoding='utf-8-sig')
manufacturer_df = pd.read_csv(DATA_DIR / 'manufacturer_df.csv', encoding='utf-8-sig')

recall_df = df.merge(manufacturer_df[['manufacturer_id', 'name']], left_on='제작자', right_on='name', how='left')
recall_df = recall_df.merge(car_df[['car_id', 'model_name', 'manufacturer_id']],
                             left_on=['차명', 'manufacturer_id'],
                             right_on=['model_name', 'manufacturer_id'], how='left')

recall_df = recall_df[['제작자', '차명', '생산기간(부터)', '생산기간(까지)', '리콜개시일', '리콜대수', '리콜사유', 'car_id']]
recall_df.columns = ['manufacturer', 'model_name', 'prod_start', 'prod_end', 'recall_date', 'recall_count', 'recall_reason', 'car_id']
recall_df['recall_id'] = recall_df.index + 1
recall_df['defect_id'] = recall_df['recall_reason'].apply(classify_defect_id)

recall_df = recall_df[['recall_id', 'prod_start', 'prod_end', 'recall_date', 'recall_count', 'recall_reason', 'car_id', 'defect_id']]

write_defect_category_csv(DATA_DIR / 'defect_category.csv')
recall_df.to_csv(DATA_DIR / 'recall_df.csv', index=False, encoding='utf-8-sig')
print(f'총 {len(recall_df)}개 리콜 저장 완료')
print(recall_df.head(10))
