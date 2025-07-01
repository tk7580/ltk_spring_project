"""AniList GraphQL collector (simplified)."""
import requests, time, datetime
from typing import Iterable

from ..db import SessionLocal
from ..models import Work, WorkIdentifier

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

def fetch_page(page:int, per_page:int=50) -> list[dict]:
    r = requests.post("https://graphql.anilist.co",
        json={"query": QUERY, "variables": {"page": page, "perPage": per_page}})
    r.raise_for_status()
    return r.json()["data"]["Page"]["media"]

def _save_media(items:Iterable[dict]):
    sess = SessionLocal()
    inserted = skipped = 0
    for m in items:
        aid = m["id"]
        if sess.query(Work.id).filter_by(anilistId=aid).first():
            skipped += 1
            continue

        title = m["title"]["romaji"] or m["title"]["english"] or m["title"]["native"]
        year = m["startDate"].get("year") or 2000
        month = m["startDate"].get("month") or 1
        day = m["startDate"].get("day") or 1

        work = Work(
            anilistId=aid,
            titleOriginal=title,
            releaseDate=datetime.date(year, month, day),
            description=m.get("description"),
            thumbnailUrl=m["coverImage"].get("large"),
            isOriginal=False,
        )
        sess.add(work)
        sess.flush()

        sess.add(WorkIdentifier(workId=work.id, sourceName="anilist", sourceId=str(aid)))
        inserted += 1

    sess.commit()
    sess.close()
    return inserted, skipped

def main(args):
    pages = args.pages or 1
    delay = args.delay or 0.0
    per_page = 50
    for p in range(1, pages+1):
        items = fetch_page(p, per_page)
        ins, skp = _save_media(items)
        print(f"[AniList] page {p} \u2192 inserted {ins} | skipped {skp}")
        time.sleep(delay)
