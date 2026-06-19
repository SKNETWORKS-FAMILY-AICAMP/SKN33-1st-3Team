from pathlib import Path

from defect_classifier import DATA_DIR, DEFECT_CATEGORIES, update_recall_csv, write_defect_category_csv


def main() -> None:
    write_defect_category_csv(DATA_DIR / "defect_category.csv")
    counts = update_recall_csv(DATA_DIR / "recall_df.csv")

    category_names = dict(DEFECT_CATEGORIES)
    print("defect_category.csv 생성 완료")
    print("recall_df.csv defect_id 갱신 완료")
    print("\n분류 결과")
    for defect_id, count in sorted(counts.items()):
        print(f"{defect_id:02d}. {category_names[defect_id]}: {count}건")


if __name__ == "__main__":
    main()
