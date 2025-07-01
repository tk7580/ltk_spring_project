"""
Live-Action 타입만 달린 작품에 Drama 타입을 붙여주는 스크립트
$ python -m python_api_pipeline.run fix-types --limit 300
"""
from argparse import Namespace
from datetime import datetime

from sqlalchemy import select, exists, and_, not_
from ..db      import SessionLocal
from ..models  import Work, WorkType, WorkTypeMapping

def main(args: Namespace) -> None:
    sess  = SessionLocal()
    limit = args.limit or 5000

    dramaId = sess.query(WorkType.id).filter_by(name="Drama").scalar()
    liveId  = sess.query(WorkType.id).filter_by(name="Live-Action").scalar()
    if not (dramaId and liveId):
        raise RuntimeError("WorkType 'Drama' 또는 'Live-Action' 이 없습니다.")

    # Live-Action 은 있지만 Drama 는 없는 작품
    subq = (
        select(1)
        .select_from(WorkTypeMapping)
        .where(
            and_(
                WorkTypeMapping.workId == Work.id,
                WorkTypeMapping.typeId == dramaId
            )
        )
    )

    workIds = (
        sess.query(Work.id)
        .join(WorkTypeMapping, Work.id == WorkTypeMapping.workId)
        .filter(WorkTypeMapping.typeId == liveId)
        .filter(not_(exists(subq)))
        .limit(limit)
        .all()
    )

    toInsert = [
        WorkTypeMapping(
            workId     = w_id,
            typeId     = dramaId,
            regDate    = datetime.utcnow()
        )
        for (w_id,) in workIds
    ]
    if toInsert:
        sess.bulk_save_objects(toInsert)
        sess.commit()
    sess.close()
    print(f"[fix-types] Drama 매핑 추가 {len(toInsert)}건 완료")
