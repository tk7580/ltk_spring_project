"""
AniList 관계 정보를 이용해 Series 레코드를 생성∙연결.

● 사용 예
python -m python_api_pipeline.run collect --source series --pages 5 --delay 0.5
"""
from __future__ import annotations

import requests, time, datetime
from typing import List, Dict, Tuple

from sqlalchemy.exc import IntegrityError

from ..db     import SessionLocal
from ..models import Work, Series

# ───────────────────────────────────────────────────────────────────
# 0. GraphQL 쿼리
# ───────────────────────────────────────────────────────────────────
GRAPHQL = """
query ($page:Int!, $perPage:Int!) {
  Page(page:$page, perPage:$perPage) {
    media(type:ANIME, sort:POPULARITY_DESC) {
      id
      title { romaji english native }
      description(asHtml:false)
      coverImage { large extraLarge }
      relations {
        edges {
          relationType(version:2)
          node { id title { romaji english native } }
        }
      }
    }
  }
}
"""


def _fetch(page: int, per_page: int = 50) -> List[Dict]:
    """AniList API 한 페이지 가져오기."""
    r = requests.post(
        "https://graphql.anilist.co",
        json={"query": GRAPHQL, "variables": {"page": page, "perPage": per_page}},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["data"]["Page"]["media"]


# ───────────────────────────────────────────────────────────────────
# 1. DB 저장
# ───────────────────────────────────────────────────────────────────
def _store(batch: List[Dict]) -> Tuple[int, int]:
    """
    * 이미 존재하는 Work(anilistId 매칭) ↔ Series 링크
    * 없으면 Series 신규 생성
    반환: (새로 생성한 series 수, 새로 연결한 work 수)
    """
    sess          = SessionLocal()
    new_series    = 0
    linked_works  = 0

    try:
        for media in batch:
            # 1) 우리 DB 에 등록된 Work 찾기
            work: Work | None = (
                sess.query(Work)
                .filter_by(anilistId=media["id"])   # ← camelCase 속성으로 수정
                .one_or_none()
            )
            if work is None:
                continue  # 아직 수집되지 않은 작품이면 스킵

            # 2) Series 찾거나 생성
            title_ori = (
                    media["title"]["romaji"]
                    or media["title"]["english"]
                    or media["title"]["native"]
            )
            series = sess.query(Series).filter_by(titleOriginal=title_ori).one_or_none()

            if series is None:
                series = Series(
                    titleOriginal = title_ori,
                    titleKr       = None,
                    description   = None,
                    thumbnailUrl  = media["coverImage"]["large"],
                    coverImageUrl = media["coverImage"]["extraLarge"],
                    regDate       = datetime.datetime.utcnow(),
                    updateDate    = datetime.datetime.utcnow(),
                )
                sess.add(series)
                sess.flush()  # series.id 확보
                new_series += 1

            # 3) Work ↔ Series 링크
            if work.seriesId is None:
                work.seriesId   = series.id
                work.updateDate = datetime.datetime.utcnow()
                linked_works   += 1

        sess.commit()
    except IntegrityError:
        sess.rollback()
        raise
    finally:
        sess.close()

    return new_series, linked_works


# ───────────────────────────────────────────────────────────────────
# 2. CLI entry
# ───────────────────────────────────────────────────────────────────
def main(args):
    """
    python -m python_api_pipeline.run collect --source series
                                              [--pages N] [--delay S]
    """
    pages = args.pages or 1
    delay = args.delay or 0.0

    total_new   = 0
    total_link  = 0
    for page in range(1, pages + 1):
        media     = _fetch(page, per_page=50)
        created, linked = _store(media)

        total_new  += created
        total_link += linked
        print(f"[Series] page {page} | new series {created} | linked works {linked}")
        time.sleep(delay)

    print(f"[Series] DONE → total new series={total_new}, linked works={total_link}")
