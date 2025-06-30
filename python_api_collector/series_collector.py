#!/usr/bin/env python3
# series_collector.py

import os
import time
import requests
import json
from dotenv import load_dotenv
from db_utils import get_db_connection

# ──────────────────────────────────────────────────────────────────────────────
# 환경변수 로드 & 검증
load_dotenv()
ANILIST_API_URL   = os.getenv("ANILIST_API_URL", "https://graphql.anilist.co")
PAGE_SIZE         = int(os.getenv("ANILIST_PAGE_SIZE", 50))

# ──────────────────────────────────────────────────────────────────────────────
# GraphQL Query: 작품의 관계 정보 포함
SERIES_QUERY = '''
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo { hasNextPage }
    media(type: ANIME) {
      id
      title { romaji native english }
      description(asHtml: false)
      relations {
        edges {
          relationType
          node { id }
        }
      }
    }
  }
}
'''

# ──────────────────────────────────────────────────────────────────────────────
# GraphQL 호출 & 페이지 단위 페칭

def fetch_anilist_series(page: int) -> dict:
    resp = requests.post(
        ANILIST_API_URL,
        json={"query": SERIES_QUERY, "variables": {"page": page, "perPage": PAGE_SIZE}},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["data"]["Page"]

# ──────────────────────────────────────────────────────────────────────────────
# DB Upsert: series & mapping 테이블

def upsert_series_and_mapping(record: dict):
    # relations로부터 동시 속한 시리즈 ID 집합
    rel_ids = [edge["node"]["id"] for edge in record.get("relations", {}).get("edges", [])]
    rel_ids.append(record["id"])
    series_root = min(rel_ids)

    # 타이틀 선택: native > romaji > english
    titles = record.get("title", {})
    series_title = titles.get("native") or titles.get("romaji") or titles.get("english") or f"Series {series_root}"
    series_desc  = record.get("description") or ''

    conn = get_db_connection()
    cursor = conn.cursor()
    # series 테이블 업서트
    cursor.execute(
        """
        INSERT INTO series (id, title, description)
        VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                                 title = VALUES(title),
                                 description = VALUES(description)
        """, (series_root, series_title, series_desc)
    )
    # series_work 매핑
    cursor.execute(
        """
        INSERT IGNORE INTO series_work (series_id, work_id)
        VALUES (%s, %s)
        """, (series_root, record["id"])
    )
    conn.commit()
    cursor.close()
    conn.close()

# ──────────────────────────────────────────────────────────────────────────────
# 메인 로직: 전체 페이지 순차 처리

def main(delay: float = 0.5):
    page = 1
    while True:
        try:
            data = fetch_anilist_series(page)
        except Exception as e:
            print(f"[SeriesCollector] 페이지 {page} 조회 실패: {e}")
            break

        records = data.get("media", [])
        if not records:
            print("[SeriesCollector] 처리할 레코드 없음")
            break

        for rec in records:
            try:
                upsert_series_and_mapping(rec)
                print(f"[SeriesCollector] upsert 완료: work_id={rec['id']} -> series_id={min([e['node']['id'] for e in rec.get('relations', {}).get('edges', [])] + [rec['id']])}")
            except Exception as e:
                print(f"[SeriesCollector] 매핑 실패: work_id={rec['id']}, error={e}")
            time.sleep(delay)

        if not data.get("pageInfo", {}).get("hasNextPage"):
            print("[SeriesCollector] 모든 페이지 처리 완료.")
            break
        page += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AniList 작품 시리즈 업서트 스크립트")
    parser.add_argument("--delay", type=float, default=0.5, help="각 요청 사이 대기 시간(초)")
    args = parser.parse_args()
    main(delay=args.delay)
