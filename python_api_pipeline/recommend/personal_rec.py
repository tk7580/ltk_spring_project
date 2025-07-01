
"""Simple personal recommendation engine.

Usage:
    from python_api_pipeline.recommend.personal_rec import recommend_for_member
"""
from sqlalchemy import select, func
from ..db import SessionLocal
from ..models import Work, MemberWatchedWork, WorkGenre

def recommend_for_member(member_id:int, limit:int=10):
    sess = SessionLocal()
    watched_work_ids = {w.workId for w in sess.scalars(
        select(MemberWatchedWork.workId).where(MemberWatchedWork.memberId==member_id)
    )}
    if not watched_work_ids:
        return []
    # get favorite genres
    fav_genres = sess.scalars(
        select(WorkGenre.genreId, func.count()).join(Work, Work.id==WorkGenre.workId)
        .where(WorkGenre.workId.in_(watched_work_ids))
        .group_by(WorkGenre.genreId)
        .order_by(func.count().desc())
        .limit(3)
    ).all()
    genre_ids=[gid for gid,_ in fav_genres]
    q = select(Work).join(WorkGenre).where(
        WorkGenre.genreId.in_(genre_ids),
        Work.id.not_in(watched_work_ids)
    ).order_by(Work.averageRating.desc()).limit(limit)
    recs = sess.scalars(q).all()
    sess.close()
    return recs
