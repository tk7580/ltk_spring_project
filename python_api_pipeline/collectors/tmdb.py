"""TMDB API collector – camelCase 컬럼 대응 + pages 옵션 지원."""
from __future__ import annotations

import os, requests, time, math
from datetime import datetime, date
from typing import Iterable, List

from sqlalchemy.exc import IntegrityError
from ..db     import SessionLocal
from ..models import Work, WorkIdentifier

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL     = "https://api.themoviedb.org/3"


# ───────────────────────────────────────────────────────────────────
# 0. 공통 유틸
# ───────────────────────────────────────────────────────────────────
def _tmdb_req(path: str, **params) -> dict:
    params["api_key"] = TMDB_API_KEY
    resp = requests.get(f"{BASE_URL}/{path}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _safe_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return date(y, m, d)
    except Exception:
        return None


# ───────────────────────────────────────────────────────────────────
# 1. DB 저장
# ───────────────────────────────────────────────────────────────────
def _save(items: Iterable[dict]) -> tuple[int, int]:
    """
    TMDB 응답 배열을 DB에 저장하고 (inserted, skipped) 카운트를 반환.
    skip 조건: 같은 TMDB ID 가 이미 work_identifier 에 존재.
    """
    sess = SessionLocal()
    inserted = skipped = 0

    # 미리 해당 batch 의 TMDB id 집합 -> 이미 존재하는 row 조회 후 set 으로
    src_ids: List[str] = [str(m["id"]) for m in items]
    existing = {
        r[0]
        for r in sess.query(WorkIdentifier.sourceId)
        .filter(
            WorkIdentifier.sourceName == "tmdb",
            WorkIdentifier.sourceId.in_(src_ids),
            )
        .all()
    }

    for m in items:
        src_id = str(m["id"])
        if src_id in existing:
            skipped += 1
            continue

        work = Work(
            seriesId      = None,
            anilistId     = None,
            titleOriginal = m.get("title") or m.get("name"),
            titleKr       = None,
            description   = m.get("overview"),
            thumbnailUrl  = (
                f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                if m.get("poster_path") else None
            ),
            releaseDate   = _safe_date(m.get("release_date") or m.get("first_air_date")),
            isOriginal    = True,
            regDate       = datetime.utcnow(),
            updateDate    = datetime.utcnow(),
        )
        sess.add(work)
        sess.flush()                      # work.id 확보

        sess.add(WorkIdentifier(
            workId     = work.id,
            sourceName = "tmdb",
            sourceId   = src_id,
            regDate    = datetime.utcnow(),
            updateDate = datetime.utcnow(),
        ))
        inserted += 1

    try:
        sess.commit()
    except IntegrityError:
        sess.rollback()
    finally:
        sess.close()

    return inserted, skipped


# ───────────────────────────────────────────────────────────────────
# 2. CLI entry
# ───────────────────────────────────────────────────────────────────
def main(args):
    """
    python -m python_api_pipeline.run collect --source tmdb [--type movie|tv]
                                              [--pages N] [--batch N] [--delay S]
    * pages : 수집할 페이지 수(1 페이지 ≈ 20 항목).
    * batch : 최대 수집 아이템 수.
      둘 다 주면 pages 우선.
    """
    if not TMDB_API_KEY:
        raise RuntimeError("환경변수 TMDB_API_KEY 가 설정되어 있지 않습니다.")

    media_type = args.type   or "movie"       # movie | tv
    pages      = args.pages  or None          # 우선순위 1
    batch      = args.batch  or 100           # 우선순위 2
    delay      = args.delay  or 0.0

    page = 1
    fetched = 0
    max_pages = pages if pages is not None else math.inf
    max_items = batch if pages is None else math.inf   # pages 있으면 batch 무시

    while page <= max_pages and fetched < max_items:
        data  = _tmdb_req(f"discover/{media_type}", sort_by="popularity.desc", page=page)
        items = data.get("results", [])
        if not items:
            break

        ins, skp = _save(items)
        fetched += len(items)
        print(f"[TMDB] page {page} saved {len(items)} items (insert {ins}, skip {skp})")

        page += 1
        time.sleep(delay)
