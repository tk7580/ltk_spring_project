"""Series builder: groups AniList works into Series by original title."""
import time
from sqlalchemy import select
from ..collectors.anilist import fetch_page
from ..db import SessionLocal
from ..models import Work, Series

def _get_or_create_series(sess, title_orig:str):
    series = sess.scalar(select(Series).where(Series.titleOriginal==title_orig))
    if series:
        return series
    series = Series(titleOriginal=title_orig)    # titleKr NULL
    sess.add(series)
    sess.flush()
    return series

def store_relations(batch):
    sess = SessionLocal()
    new_series = linked = 0
    for media in batch:
        work = sess.scalar(select(Work).where(Work.anilistId==media["id"]))
        if not work:
            continue
        if work.seriesId:
            linked += 1
            continue
        series = _get_or_create_series(sess, media["title"]["romaji"])
        work.seriesId = series.id
        linked += 1
        if series.regDate==series.updateDate:
            new_series += 1
    sess.commit()
    sess.close()
    return new_series, linked

def main(args):
    pages = args.pages or 1
    delay = args.delay or 0.0
    per_page = 50
    total_new=total_link=0
    for p in range(1, pages+1):
        batch = fetch_page(p, per_page)
        new_s, link_s = store_relations(batch)
        total_new += new_s
        total_link += link_s
        print(f"[Series] page {p} | new {new_s} | linked {link_s}")
        time.sleep(delay)
    print(f"[Series] DONE → total new={total_new}, linked={total_link}")
