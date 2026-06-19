import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# ── DB 설정 ──────────────────────────────────────────────
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME")

# ── CSV 경로 ─────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

REGION_CSV          = DATA_DIR / 'region_df.csv'
MANUFACTURER_CSV    = DATA_DIR / 'manufacturer_df.csv'
CAR_CSV             = DATA_DIR / 'car_df.csv'
DEFECT_CATEGORY_CSV = DATA_DIR / 'defect_category.csv'
SERVICE_CENTER_CSV  = DATA_DIR / 'service_center_df.csv'
RECALL_CSV          = DATA_DIR / 'recall_df.csv'
FAQ_CSV             = DATA_DIR / 'faq_df.csv'
NEWS_CSV            = DATA_DIR / 'news_df.csv'

# ────────────────────────────────────────────────────────
def main():
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        echo=False
    )

    targets = [
        ("region",          REGION_CSV,          None),
        ("manufacturer",    MANUFACTURER_CSV,    None),
        ("defect_category", DEFECT_CATEGORY_CSV, None),
        ("car",             CAR_CSV,             None),
        ("service_center",  SERVICE_CENTER_CSV,  None),
        ("recall",          RECALL_CSV,          {"recall_reason": ""}),
        ("faq",             FAQ_CSV,             None),
        ("news",            NEWS_CSV,            None),
    ]

    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

    for table, path, fillna_map in targets:
        with engine.connect() as conn:
            existing_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        if existing_count:
            print(f"[SKIP] {table}: already has {existing_count} rows")
            continue

        df = pd.read_csv(path)

        if fillna_map:
            for col, val in fillna_map.items():
                null_count = df[col].isna().sum()
                if null_count > 0:
                    print(f"[INFO] {table}.{col} NULL {null_count}행 → '{val}'로 처리")
                    df[col] = df[col].fillna(val)

        df.to_sql(
            name=table,
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000
        )
        print(f"[OK] {table}: {len(df)}행 insert 완료")

    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    print("\n전체 insert 완료")

if __name__ == "__main__":
    main()