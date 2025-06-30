#!/usr/bin/env python3
# series_batch_reconciler.py

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
# GraphQL Query: 시리즈 포함된 페이지 단위 fetch
BATCH_QUERY = '''
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo { hasNextPage }
    media(type: ANIME) {
      id
      relations {
        edges { node { id } }
      }
    }
  }
}
'''

def fetch_batch(page: int) -> dict:
    resp = requests.post(
        ANILIST_API_URL,
        json={"query": BATCH_QUERY, "variables": {"page": page, "perPage": PAGE_SIZE}},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["data"]["Page"]

# ──────────────────────────────────────────────────────────────────────────────
# DB 업데이트
def map_series_works(series_id: int, work_ids: list):
    conn = get_db_connection()
    cursor = conn.cursor()
    for wid in work_ids:
        cursor.execute(
            "INSERT IGNORE INTO series_work (series_id, work_id) VALUES (%s, %s)",
            (series_id, wid)
        )
    conn.commit()
    cursor.close()
    conn.close()

def main(delay: float = 0.5):
    page = 1
    while True:
        batch = fetch_batch(page)
        for rec in batch.get("media", []):
            # series root ID = 최소값
            ids = [e["node"]["id"] for e in rec["relations"]["edges"]] + [rec["id"]]
            root = min(ids)
            map_series_works(root, ids)
            print(f"[BatchRecon] series_id={root} mapped works={ids}")
            time.sleep(delay)
        if not batch.get("pageInfo", {}).get("hasNextPage"):
            print("[BatchRecon] 모든 배치 처리 완료.")
            break
        page += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="시리즈-워크 배치 매핑 스크립트")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="각 요청 사이 대기 시간(초)")
    args = parser.parse_args()
    main(delay=args.delay)
