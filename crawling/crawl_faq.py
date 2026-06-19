"""
자동차리콜센터 FAQ 크롤러
https://www.car.go.kr/rs/faq/list.do
"""

import csv
import os
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

BASE_URL = "https://www.car.go.kr/rs/faq/list.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}


def fetch_page(page_no: int) -> str:
    data = urllib.parse.urlencode({
        "divisionCode": "0331",
        "currentPageNo": str(page_no),
        "searchId": "",
        "searchStr": "",
    }).encode("utf-8")

    req = urllib.request.Request(BASE_URL, data=data, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_faq(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    faq_ul = soup.find("ul", class_="faq-list")
    if not faq_ul:
        return []

    items = []
    for li in faq_ul.find_all("li", recursive=False):
        question_tag = li.find("a", class_="uk-accordion-title")
        answer_tag = li.find("div", class_="uk-accordion-content")

        question = question_tag.get_text(strip=True) if question_tag else ""
        answer = answer_tag.get_text(separator=" ", strip=True) if answer_tag else ""

        items.append({"question": question, "answer": answer})

    return items


def get_total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1
    page_items = pagination.find_all("li")
    return len(page_items)


def crawl() -> list[dict]:
    print("1페이지 수집 중...")
    first_html = fetch_page(1)
    total_pages = get_total_pages(first_html)
    print(f"총 {total_pages}페이지 감지")

    all_items = parse_faq(first_html)

    for page in range(2, total_pages + 1):
        print(f"{page}페이지 수집 중...")
        time.sleep(0.5)
        html = fetch_page(page)
        all_items.extend(parse_faq(html))

    # faq_id 부여 (1부터 순번)
    result = []
    for idx, item in enumerate(all_items, start=1):
        result.append({
            "faq_id": idx,
            "question": item["question"],
            "answer": item["answer"],
        })

    return result


def save_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["faq_id", "question", "answer"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"저장 완료: {path}  ({len(rows)}건)")


if __name__ == "__main__":
    rows = crawl()
    save_csv(rows, os.path.join(DATA_DIR, "faq_df.csv"))
