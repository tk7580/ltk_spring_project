"""Ensure every Work has at least Animation OR Drama type."""
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Work, WorkType, WorkTypeMapping

def main(args):
    limit = args.limit or 300
    sess = SessionLocal()

    animation = sess.scalar(select(WorkType).where(WorkType.name=="Animation"))
    drama = sess.scalar(select(WorkType).where(WorkType.name=="Drama"))

    if not (animation and drama):
        print("[type-fixer] required WorkType rows missing.")
        return

    q = (
        select(Work.id)
        .join(WorkTypeMapping, Work.id==WorkTypeMapping.workId)
        .where(WorkTypeMapping.typeId==animation.id)
        .limit(limit)
    )
    candidate_ids = [row[0] for row in sess.execute(q)]
    fixed = 0
    for wid in candidate_ids:
        exists = sess.scalar(
            select(WorkTypeMapping).where(
                WorkTypeMapping.workId==wid,
                WorkTypeMapping.typeId==drama.id
            )
        )
        if exists:
            continue
        sess.add(WorkTypeMapping(workId=wid, typeId=drama.id))
        fixed += 1
    sess.commit()
    sess.close()
    print(f"[fix-types] Drama 매핑 추가 {fixed}건 완료")
