
"""Very basic recommendation: top rated works."""
from ..db import SessionLocal
from ..models import Work
from sqlalchemy import select, desc

def top_n(n:int=10):
    session = SessionLocal()
    stmt = select(Work).order_by(desc(Work.average_rating), desc(Work.rating_count)).limit(n)
    results = session.scalars(stmt).all()
    session.close()
    return results
