# -*- coding: utf-8 -*-
"""
네이버 검색 API로 자동차 리콜 뉴스를 수집해 news.csv로 저장한다.

[준비물]
    - .env 파일에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

    - data 폴더에 car_df.csv (컬럼: car_id, manufacturer_id, model_name)
    - data 폴더에 manufacturer_df.csv (컬럼: manufacturer_id, name)
        - 두 파일을 manufacturer_id 기준으로 조인해 '제조사명 + 차명 + 리콜' 키워드로 검색한다.

    - 설치: pip install requests python-dotenv
"""

import os
import csv
import re
import html
import time

import requests
from dotenv import load_dotenv



# 1. 상수

NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"

CAR_CSV_PATH          = "../data/car_df.csv"
MANUFACTURER_CSV_PATH = "../data/manufacturer_df.csv"
NEWS_CSV_PATH         = "../data/news_df.csv"

DISPLAY_COUNT = 5       # 모델당 가져올 뉴스 개수
SORT_OPTION = "sim"     # sim: 정확도순 / date: 최신순
REQUEST_INTERVAL = 0.1  # API 호출 간격(초)
TITLE_MAX_LEN = 300     # news_title VARCHAR(300) 길이 제한



# 2. API 인증 정보 로드

def load_api_credentials() -> dict:
    """.env에서 네이버 API 키를 읽어 요청 헤더를 반환한다."""
    load_dotenv()

    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            ".env에서 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET를 찾지 못했습니다."
        )

    # 네이버 오픈 API는 인증 정보를 헤더에 담아 전송한다.
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }



# 3. manufacturer_df.csv 읽기

def load_manufacturers(path: str) -> dict:
    """manufacturer_df.csv를 읽어 {manufacturer_id: name} 딕셔너리로 반환한다."""
    manufacturers = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m_id = (row.get("manufacturer_id") or "").strip()
            name = (row.get("name") or "").strip()
            if m_id:
                manufacturers[m_id] = name
    return manufacturers



# 4. car_df.csv 읽기

def load_cars(car_path: str, manufacturers: dict) -> list[dict]:
    """
    car_df.csv를 읽어 manufacturer_id를 제조사명으로 치환한 뒤
    [{'car_id': 1, 'model_name': '코나', 'manufacturer_name': '현대'}, ...] 형태로 반환한다.
    """
    cars = []
    # utf-8-sig: 엑셀에서 저장한 한글 CSV 호환 인코딩
    with open(car_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            car_id = (row.get("car_id") or "").strip()
            model_name = (row.get("model_name") or "").strip()
            m_id = (row.get("manufacturer_id") or "").strip()
            if not car_id or not model_name:
                continue
            manufacturer_name = manufacturers.get(m_id, "")  # id → 제조사명 변환
            cars.append({"car_id": car_id, "model_name": model_name, "manufacturer_name": manufacturer_name})
    return cars



# 5. 텍스트 정제

def clean_text(raw: str) -> str:
    """API 응답 제목에 섞인 <b> 태그와 HTML 엔티티를 제거한다."""
    no_tags = re.sub(r"<[^>]+>", "", raw)   # <b>, </b> 등 태그 제거
    unescaped = html.unescape(no_tags)       # &quot; -> ", &amp; -> & 변환
    return unescaped.strip()



# 6. 뉴스 검색

def search_news(headers: dict, manufacturer_name: str, model_name: str) -> list[dict]:
    """'제조사 + 차명 + 리콜' 키워드로 네이버 뉴스를 검색해 items 리스트를 반환한다."""
    query = f"{manufacturer_name} {model_name} 리콜" if manufacturer_name else f"{model_name} 리콜"
    params = {
        "query": query,
        "display": DISPLAY_COUNT,
        "sort": SORT_OPTION,
    }

    try:
        response = requests.get(
            NAVER_NEWS_API_URL, headers=headers, params=params, timeout=10
        )
        response.raise_for_status()  # 400, 500번대 응답 시 예외 발생
    except requests.exceptions.Timeout:
        print(f"  [시간초과] {model_name}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"  [요청실패] {model_name}: {e}")
        return []

    return response.json().get("items", [])



# 7. 메인

def main():
    headers = load_api_credentials()
    manufacturers = load_manufacturers(MANUFACTURER_CSV_PATH)
    cars = load_cars(CAR_CSV_PATH, manufacturers)
    print(f"검색할 차명 개수: {len(cars)}")

    news_id = 1  # AUTO_INCREMENT 역할, 1부터 순차 증가
    collected = 0

    # newline="" + utf-8-sig: 엑셀에서 한글이 깨지지 않게 저장
    with open(NEWS_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["news_id", "news_title", "news_link", "car_id"])

        for idx, car in enumerate(cars, start=1):
            car_id = car["car_id"]
            model_name = car["model_name"]
            manufacturer_name = car["manufacturer_name"]

            items = search_news(headers, manufacturer_name, model_name)

            for item in items:
                title = clean_text(item.get("title", ""))[:TITLE_MAX_LEN]
                # originallink: 언론사 원문 주소. 비어 있으면 네이버 링크로 대체.
                link = item.get("originallink") or item.get("link", "")

                if not title or not link:
                    continue

                writer.writerow([news_id, title, link, car_id])
                news_id += 1
                collected += 1

            if idx % 100 == 0:
                print(f"  진행 {idx}/{len(cars)} ... 누적 뉴스 {collected}건")

            time.sleep(REQUEST_INTERVAL)

    print(f"완료! 총 {collected}건의 뉴스를 '{NEWS_CSV_PATH}'에 저장했습니다.")


if __name__ == "__main__":
    main()
