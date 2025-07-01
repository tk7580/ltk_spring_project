
"""Generate or update viewing guides for each series.

Run:
    python -m python_api_pipeline.guide.generate_guide --series-id 123 --strategy release
"""

import argparse
from datetime import datetime
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Work, ViewingGuide, ViewingGuideItem, Series

def build_steps(works, strategy="release"):
    if strategy == "timeline":
        works = sorted(works, key=lambda w: (w.timelineSequence or 0, w.releaseDate or datetime.min))
    else:  # default release order
        works = sorted(works, key=lambda w: (w.releaseDate or datetime.min, w.releaseSequence or 0))
    for idx, w in enumerate(works, start=1):
        yield dict(stepNumber=idx, workId=w.id,
                   stepDescription=f"시청 순서 {idx}: {w.titleKr or w.titleOriginal}")

def generate(series_id:int, strategy:str="release", name:str|None=None, desc:str|None=None):
    sess = SessionLocal()
    series = sess.get(Series, series_id)
    assert series, f"Series {series_id} not found"
    works = sess.scalars(select(Work).where(Work.seriesId==series_id)).all()
    if not works:
        print("[guide] No works in series")
        return
    guide = ViewingGuide(seriesId=series_id,
                         guideName=name or f"{series.titleKr or series.titleOriginal} 기본 가이드",
                         guideDescription=desc or f"{strategy} 기준 자동 생성되었습니다.")
    sess.add(guide)
    sess.flush()
    steps = [ViewingGuideItem(guideId=guide.id, **s) for s in build_steps(works,strategy)]
    sess.bulk_save_objects(steps)
    sess.commit()
    print(f"[guide] Guide {guide.id} created for series {series_id} with {len(steps)} steps")
    sess.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series-id", required=True, type=int)
    ap.add_argument("--strategy", choices=["release","timeline"], default="release")
    args=ap.parse_args()
    generate(args.series_id,args.strategy)

if __name__ == "__main__":
    main()
