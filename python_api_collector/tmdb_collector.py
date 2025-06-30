#!/usr/bin/env python3
# tmdb_collector.py

import os
import time
import requests
from dotenv import load_dotenv
from db_utils import get_db_connection

# ──────────────────────────────────────────────────────────────────────────────
# 환경변수 로드 & 검증
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_API_URL = os.getenv("TMDB_API_URL", "https://api.themoviedb.org/3")

if not TMDB_API_KEY:
    raise EnvironmentError("환경변수 TMDB_API_KEY가 설정되지 않았습니다.")

# ──────────────────────────────────────────────────────────────────────────────
# HTTP 세션 및 공통 파라미터 설정
session = requests.Session()
session.params = {
    "api_key": TMDB_API_KEY,
    "language": "ko-KR"  # 한국어 메타데이터 요청
}


def retryable_get(url, params=None, retries=3, backoff=1.0):
    """
    HTTP GET 요청을 재시도 로직과 함께 수행합니다.
    """
    for i in range(1, retries + 1):
        try:
            res = session.get(url, params=params, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(f"[TMDB] 요청 실패 (시도 {i}): {e}")
            if i < retries:
                time.sleep(backoff * i)
    print(f"[TMDB] 모든 재시도 실패: {url}")
    return {}


def search_tmdb(title: str) -> list:
    """
    주어진 타이틀로 TMDB TV 시리즈를 검색하여 결과 리스트 반환
    """
    url = f"{TMDB_API_URL}/search/tv"
    data = retryable_get(url, params={"query": title})
    return data.get("results", [])


def fetch_series_details(tmdb_id: int) -> dict:
    """
    TMDB TV 시리즈 상세 정보를 조회
    """
    url = f"{TMDB_API_URL}/tv/{tmdb_id}"
    return retryable_get(url)


def update_work_tmdb(work_id: int, details: dict):
    """
    DB의 work 레코드에 TMDB 정보 업데이트
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE work SET
                        tmdb_id = %s,
                        tmdb_name = %s,
                        tmdb_overview = %s,
                        tmdb_first_air_date = %s,
                        tmdb_poster_path = %s
        WHERE id = %s
        """,
        (
            details.get("id"),
            details.get("name"),
            details.get("overview"),
            details.get("first_air_date"),
            details.get("poster_path"),
            work_id
        )
    )
    conn.commit()
    cursor.close()
    conn.close()


def main(batch_size: int = 100, delay: float = 0.5):
    # DB에서 아직 TMDB 매핑이 없는 작품 리스트 조회
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, title_english, title_romaji, title_native
        FROM work
        WHERE tmdb_id IS NULL
            LIMIT %s
        """, (batch_size,)
    )
    works = cursor.fetchall()
    cursor.close()
    conn.close()

    for w in works:
        titles = [w["title_english"], w["title_romaji"], w["title_native"]]
        tmdb_results = []
        # 순차적으로 영어, 로마지, 네이티브 타이틀로 검색
        for title in filter(None, titles):
            tmdb_results = search_tmdb(title)
            if tmdb_results:
                break
        if not tmdb_results:
            print(f"[TMDB] 매칭 못함: work_id={w['id']}, titles={titles}")
            continue

        # 가장 유사도가 높은 첫 번째 결과 사용
        result = tmdb_results[0]
        details = fetch_series_details(result["id"])
        if details:
            update_work_tmdb(w["id"], details)
            print(f"[TMDB] 업데이트 완료: work_id={w['id']}, tmdb_id={result['id']}")
        time.sleep(delay)

    print("[TMDB] 전체 처리 완료.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TMDB 시리즈 정보 수집기")
    parser.add_argument("--batch", type=int, default=100,
                        help="한 번에 조회할 작품 수 (default: 100)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="각 요청 사이 대기 시간(초, default: 0.5)")
    args = parser.parse_args()
    main(batch_size=args.batch, delay=args.delay)
