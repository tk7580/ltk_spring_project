#!/usr/bin/env python3
# anilist_collector.py

import os
import time
import requests
from dotenv import load_dotenv
from db_utils import get_db_connection

# ──────────────────────────────────────────────────────────────────────────────
# 환경변수 로드 & 검증
dotenv_path = os.getenv('ENV_PATH', '.env')
load_dotenv(dotenv_path)
ANILIST_API_URL   = "https://graphql.anilist.co"
ANILIST_PAGE_SIZE = int(os.getenv("ANILIST_PAGE_SIZE", 50))

if not ANILIST_API_URL:
    raise EnvironmentError("`ANILIST_API_URL` 환경변수가 없습니다.")
# ──────────────────────────────────────────────────────────────────────────────

def fetch_anilist_media(page: int, per_page: int) -> dict:
    """
    AniList GraphQL API에서 ANIME 타입 작품을 페이지 단위로 조회합니다.
    """
    query = '''
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        pageInfo { total, currentPage, lastPage, hasNextPage }
        media(type: ANIME) {
          id
          title { romaji native english }
          description(asHtml: false)
          episodes
          averageScore
          startDate { year month day }
        }
      }
    }
    '''
    variables = {"page": page, "perPage": per_page}
    res = requests.post(
        ANILIST_API_URL,
        json={"query": query, "variables": variables},
        timeout=30
    )
    res.raise_for_status()
    return res.json()["data"]["Page"]


def save_media_to_db(media_list: list):
    """
    가져온 AniList 미디어 목록을 DB의 series 및 work 테이블에 insert 또는 update 합니다.
    """
    # 날짜 포맷 YYYY-MM-DD 내부 함수
    def fmt_date(d):
        if d and d.get("year"):
            return f"{d['year']}-{d['month']:02d}-{d['day']:02d}"
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    for m in media_list:
        titles = m.get("title", {})
        # English 제목 우선, 없으면 Romaji, 없으면 Native
        original_title = (
                titles.get("english")
                or titles.get("romaji")
                or titles.get("native")
                or f"AniList-{m['id']}"
        )

        # 1) series 테이블 보장
        cursor.execute(
            """
            INSERT IGNORE INTO series
              (id, titleOriginal, description, regDate, updateDate)
            VALUES (%s, %s, %s, NOW(), NOW())
            """, (
                m['id'],
                original_title,
                m.get('description')
            )
        )

        # 2) work 테이블에 삽입/갱신
        cursor.execute(
            """
            INSERT INTO work
              (id,
               seriesId,
               titleOriginal,
               description,
               episodes,
               averageRating,
               releaseDate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              seriesId        = VALUES(seriesId),
              titleOriginal   = VALUES(titleOriginal),
              description     = VALUES(description),
              episodes        = VALUES(episodes),
              averageRating   = VALUES(averageRating),
              releaseDate     = VALUES(releaseDate)
            """, (
                m['id'],
                m['id'],
                original_title,
                m.get('description'),
                m.get('episodes'),
                m.get('averageScore'),
                fmt_date(m.get('startDate'))
            )
        )

    conn.commit()
    cursor.close()
    conn.close()


def main(limit: int = None, delay: float = 1.0):
    page     = 1
    per_page = ANILIST_PAGE_SIZE
    fetched  = 0

    while True:
        try:
            page_data = fetch_anilist_media(page, per_page)
        except Exception as e:
            print(f"[AniList] 페이지 {page} 조회 실패: {e}")
            break

        media = page_data.get("media", [])
        save_media_to_db(media)

        fetched += len(media)
        print(f"[AniList] Page {page}/{page_data.get('lastPage')} 저장 완료 ({len(media)} items)")

        if not page_data.get("hasNextPage"):
            print("[AniList] 더 이상 페이지가 없습니다.")
            break

        if limit and fetched >= limit:
            print(f"[AniList] 설정된 limit({limit}) 도달, 중단합니다.")
            break

        page += 1
        time.sleep(delay)

    print(f"[AniList] 전체 수집 종료. 총 {fetched}개 작품 저장됨.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AniList 애니메이션 정보 수집기")
    parser.add_argument("--limit", type=int,   default=None, help="최대 수집 작품 수")
    parser.add_argument("--delay", type=float, default=1.0,  help="페이지 조회 간 딜레이(초)")
    args = parser.parse_args()
    main(limit=args.limit, delay=args.delay)
