# python_api_pipeline/reconcile/batch_reconciler.py
"""
AniList 관계 테이블을 다시 읽어
· series 가 없는 work → 기존 Series 에 연결 또는 새로 생성
· 같은 series 내 release_sequence 자동 부여

$ python -m python_api_pipeline.run batch-reconcile --delay 0.5
"""
from __future__ import annotations

import time
from datetime import datetime
from argparse import Namespace

from sqlalchemy import select, or_, func
from ..db     import SessionLocal
from ..models import Work, Series


def _find_or_create_series(sess, work: Work) -> Series:
    """제목(한/영)으로 Series 검색, 없으면 신규 생성"""
    s = (
        sess.query(Series)
        .filter(
            or_(
                Series.title_original == work.title_original,
                Series.title_kr       == work.title_kr,
                )
        )
        .one_or_none()
    )
    if s:
        return s

    # 새로 만든다
    s = Series(
        title_original = work.title_original,
        title_kr       = work.title_kr,
        description    = work.description,
        reg_date       = datetime.utcnow(),
        update_date    = datetime.utcnow(),
    )
    sess.add(s)
    sess.flush()          # s.id 확보
    return s


def _next_release_seq(sess, series_id: int) -> int:
    """해당 시리즈의 다음 release_sequence 값"""
    max_seq = (
            sess.query(func.max(Work.release_sequence))
            .filter(Work.series_id == series_id)
            .scalar()
            or 0
    )
    return max_seq + 1


def main(args: Namespace) -> None:
    delay = args.delay or 0.0
    sess  = SessionLocal()

    # series_id 가 NULL 인 작품
    targets = sess.scalars(
        select(Work).where(Work.series_id.is_(None))
    ).all()
    print(f"[batch-reconcile] 대상 {len(targets)}건")

    created_series = 0
    linked_works   = 0

    for w in targets:
        try:
            series = _find_or_create_series(sess, w)
            if w.series_id is None:
                w.series_id = series.id
                w.release_sequence = _next_release_seq(sess, series.id)
                w.update_date = datetime.utcnow()
                linked_works += 1
            if series.reg_date == series.update_date:   # 방금 만든 경우
                created_series += 1

            sess.commit()
            print(f"  ↪ Work {w.id} → Series {series.id}")
        except Exception as err:
            sess.rollback()
            print(f"  ❌ Work {w.id} 실패 → {err}")
        finally:
            time.sleep(delay)

    sess.close()
    print(
        f"[batch-reconcile] Series 새로 생성 {created_series}건, "
        f"Work 연결 {linked_works}건 완료"
    )
