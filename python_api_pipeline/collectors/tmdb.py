"""TMDB collector (movie).
Requires TMDB_API_KEY env variable."""
import os, requests, time, datetime
from ..db import SessionLocal
from ..models import Work, WorkIdentifier

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def fetch_page(page:int) -> list[dict]:
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])

def _save(items):
    sess = SessionLocal()
    inserted = skipped = 0
    for m in items:
        tid = m["id"]
        if sess.query(Work.id).join(WorkIdentifier).filter(
            WorkIdentifier.sourceName=="tmdb",
            WorkIdentifier.sourceId==str(tid)
        ).first():
            skipped += 1
            continue
        title = m["title"]
        release_date = datetime.datetime.strptime(m["release_date"], "%Y-%m-%d").date() if m.get("release_date") else None
        work = Work(
            titleOriginal=title,
            releaseDate=release_date,
            description=m.get("overview"),
            thumbnailUrl=f"https://image.tmdb.org/t/p/w300{m['poster_path']}" if m.get("poster_path") else None,
            isOriginal=False
        )
        sess.add(work)
        sess.flush()
        sess.add(WorkIdentifier(workId=work.id, sourceName="tmdb", sourceId=str(tid)))
        inserted += 1
    sess.commit()
    sess.close()
    return inserted, skipped

def main(args):
    pages = args.pages or 1
    delay = args.delay or 0.0
    for p in range(1, pages+1):
        items = fetch_page(p)
        ins, skp = _save(items)
        print(f"[TMDB] page {p} saved {len(items)} items (insert {ins}, skip {skp})")
        time.sleep(delay)
