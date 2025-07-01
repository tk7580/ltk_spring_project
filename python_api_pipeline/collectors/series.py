"""
TMDB·AniList 로 수집된 Work 들을 Series 로 묶는 수집기.

사용:
    python -m python_api_pipeline.run collect --source series --pages 5 --delay 0.5
"""
from __future__ import annotations

import time
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Work, Series


# ──────────────────────────────────────────────
# helper
# ──────────────────────────────────────────────
def _get_or_create_series(sess: Session, title_orig: str) -> Series:
    """영어(원어) 제목을 기준으로 Series 레코드를 조회하거나 새로 만든다."""
    series = sess.scalar(
        select(Series).where(Series.titleOriginal == title_orig)
    )
    if series:
        return series

    series = Series(titleOriginal=title_orig)   # titleKr → NULL 허용
    sess.add(series)
    sess.flush()            # PK(id) 확보
    return series


# ──────────────────────────────────────────────
# core
# ──────────────────────────────────────────────
def store_relations(batch: Iterable[dict]) -> tuple[int, int]:
    """
    media 배치(list[dict])를 받아
    - 신규 Series 생성 수
    - 연결된 Work 수
    를 반환한다.
    """
    sess: Session = SessionLocal()
    new_series, linked = 0, 0

    for media in batch:
        work: Work | None = sess.scalar(
            select(Work).where(Work.anilistId == media["id"])
        )
        if not work:
            continue  # 아직 Work 가 수집되지 않음

        if work.seriesId:      # 이미 연결됨
            continue

        series = _get_or_create_series(sess, media["title"]["romaji"])
        work.seriesId = series.id
        linked += 1
        if series.regDate == series.updateDate:   # 방금 만든 경우
            new_series += 1

    sess.commit()
    sess.close()
    return new_series, linked


# ──────────────────────────────────────────────
# CLI entry
# ──────────────────────────────────────────────
def main(args):
    pages     = args.pages or 1
    delay     = args.delay or 0.0
    per_page  = 50

    # AniList GraphQL 페이지 fetch 함수 재사용
    from .anilist import fetch_page

    total_new, total_link = 0, 0
    for p in range(1, pages + 1):
        batch = fetch_page(p, per_page)
        new_s, link_s = store_relations(batch)
        total_new  += new_s
        total_link += link_s
        print(f"[Series] page {p} | new {new_s} | linked {link_s}")
        time.sleep(delay)

    print(f"[Series] DONE → total new={total_new}, linked={total_link}")
