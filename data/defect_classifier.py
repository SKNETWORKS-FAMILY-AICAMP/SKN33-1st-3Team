import csv
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent

DEFECT_CATEGORIES = [
    (1, "제동장치"),
    (2, "조향장치"),
    (3, "원동기/엔진"),
    (4, "동력전달장치"),
    (5, "연료장치"),
    (6, "전기/전자장치"),
    (7, "에어백/안전벨트"),
    (8, "차체/구조장치"),
    (9, "현가장치"),
    (10, "시야/등화장치"),
    (11, "타이어/휠"),
    (12, "배출가스/환경장치"),
    (13, "기타"),
]

CLASSIFICATION_RULES = [
    (1, ["브레이크", "제동", "ABS", "제동장치", "브레이크오일", "브레이크 오일", "주차브레이크"]),
    (2, ["조향", "스티어링", "핸들", "타이로드", "조향장치"]),
    (3, ["엔진", "냉각수", "냉각", "터보", "흡기", "타이밍체인", "오일", "EGR", "DPF", "배기가스재순환"]),
    (4, ["변속", "변속기", "기어", "클러치", "구동", "동력전달", "드라이브샤프트", "프로펠러샤프트"]),
    (5, ["연료", "연료필터", "연료호스", "연료펌프", "연료탱크", "연료라인"]),
    (7, ["에어백", "안전벨트", "좌석안전띠", "인플레이터", "SRS"]),
    (10, ["전조등", "후미등", "방향지시등", "제동등", "브레이크 등", "램프", "와이퍼", "후방 영상", "후방영상", "카메라"]),
    (11, ["타이어", "휠", "바퀴", "림"]),
    (9, ["현가", "서스펜션", "쇼크업소버", "스프링", "스태빌라이저", "로어암", "어퍼암"]),
    (12, ["배출가스", "배기가스", "촉매", "요소수", "SCR", "질소산화물", "환경부"]),
    (8, ["차체", "도어", "문", "트렁크", "시트", "좌석", "선루프", "유리", "범퍼", "프레임", "안전삼각대"]),
    (6, ["전기", "전자", "소프트웨어", "ECU", "모듈", "퓨즈", "커넥터", "배선", "센서", "계기판", "디스플레이", "통신"]),
]


def classify_defect_id(reason: str) -> int:
    text = str(reason or "").lower()
    for defect_id, keywords in CLASSIFICATION_RULES:
        if any(keyword.lower() in text for keyword in keywords):
            return defect_id
    return 13


def write_defect_category_csv(path: Path = DATA_DIR / "defect_category.csv") -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["defect_id", "defect_group"])
        writer.writeheader()
        for defect_id, defect_group in DEFECT_CATEGORIES:
            writer.writerow({"defect_id": defect_id, "defect_group": defect_group})


def update_recall_csv(
    source_path: Path = DATA_DIR / "recall_df.csv",
    output_path: Path | None = None,
) -> dict[int, int]:
    if output_path is None:
        output_path = source_path

    with source_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "defect_id" not in fieldnames:
        fieldnames.append("defect_id")

    counts = {defect_id: 0 for defect_id, _ in DEFECT_CATEGORIES}
    for row in rows:
        defect_id = classify_defect_id(row.get("recall_reason", ""))
        row["defect_id"] = defect_id
        counts[defect_id] += 1

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return counts
