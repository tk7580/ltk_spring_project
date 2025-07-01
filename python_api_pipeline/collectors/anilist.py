"""Simple AniList GraphQL collector – camelCase DB 컬럼용."""
from __future__ import annotations

import requests, time
from datetime import datetime, date
from typing import Iterable

from ..db import SessionLocal
from ..models import Work
from sqlalchemy.exc import IntegrityError

QUERY = """
query ($page:Int!, $perPage:Int!) {
  Page(page:$page, perPage:$perPage) {
    media(type:ANIME, sort:POPULARITY_DESC) {
      id
      title { romaji english native }
      description(asHtml:false)
      coverImage { large }
      startDate { year month day }
      episodes
    }
  }
}
"""

def _safe_date(yr: int | None, mo: int | None, dy: int | None) -> date | None:
    if not yr:
        return None
    return date(yr, mo or 1, dy or 1)

def _save_media(items: Iterable[dict]) -> tuple[int,int]:
    sess = SessionLocal()
    inserted = skipped = 0
    for m in items:
        aid = m["id"]
        if sess.query(Work.id).filter_by(anilistId=aid).first():
            skipped += 1
            continue

        title = m["title"]["romaji"] or m["title"]["english"] or m["title"]["native"]
        work = Work(
            seriesId     = None,                     # 아직 시리즈 미정
            anilistId    = aid,
            titleOriginal= title,
            titleKr      = None,
            description  = m["description"],
            thumbnailUrl = m["coverImage"]["large"],
            releaseDate  = _safe_date(
                m["startDate"]["year"],
                m["startDate"]["month"],
                m["startDate"]["day"]),
            episodes     = m["episodes"],
            isOriginal   = False,
            regDate      = datetime.utcnow(),
            updateDate   = datetime.utcnow()
        )
        sess.add(work)
        inserted += 1

    try:
        sess.commit()
    except IntegrityError:
        sess.rollback()
    finally:
        sess.close()

    return inserted, skipped

def main(args):
    pages = args.pages or 1
    delay = args.delay or 0.0
    for p in range(1, pages + 1):
        media = requests.post(
            "https://graphql.anilist.co",
            json={"query": QUERY, "variables": {"page": p, "perPage": 50}}
        ).json()["data"]["Page"]["media"]

        ins, skp = _save_media(media)
        print(f"[AniList] page {p} → inserted {ins} | skipped {skp}")
        time.sleep(delay)
