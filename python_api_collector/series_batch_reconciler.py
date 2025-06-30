#!/usr/bin/env python
"""
series_batch_reconciler.py
──────────────────────────
모든 work 를 훑어 제목 기반으로 시리즈를 자동 정리/병합한다.

사용법
------
python series_batch_reconciler.py   # 전체
python series_batch_reconciler.py --limit 500   # 상위 500개만
"""

import re, argparse, unicodedata
from collections import defaultdict
from db_utils import cursor

# 시즌·파트 표기를 빼기 위한 정규식
SEASON_RX = re.compile(
    r"\s*([Ss]eason|[0-9]+기|[Pp]art|[편권]|[第]?\d+[話話話]?|\d+st|\d+nd|\d+rd|\d+th)\s*$"
)

def normalize(title: str) -> str:
    """‘귀멸의 칼날 1기’ → ‘귀멸의 칼날’ 같이 시리즈 공통부 추출"""
    t = unicodedata.normalize("NFKC", title)
    t = SEASON_RX.sub("", t)        # 시즌/파트 숫자 제거
    return t.strip()

def fetch_works(limit: int | None = None):
    with cursor() as cur:
        sql = "SELECT id, seriesId, titleKr, titleOriginal FROM work"
        if limit:
            sql += " LIMIT %s"
            cur.execute(sql, (limit,))
        else:
            cur.execute(sql)
        return cur.fetchall()

def ensure_series(name_kr: str, name_orig: str | None):
    with cursor() as cur:
        cur.execute("SELECT id FROM series WHERE titleKr=%s", (name_kr,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute("""
            INSERT INTO series(regDate, updateDate, titleKr, titleOriginal)
            VALUES (NOW(), NOW(), %s, %s)
        """, (name_kr, name_orig))
        sid = cur.lastrowid
        # 게시판 1:1 생성
        cur.execute("""
            INSERT INTO board(regDate, updateDate, seriesId, name, code)
            VALUES (NOW(), NOW(), %s, %s, %s)
        """, (sid, f"{name_kr} 게시판", f"series_{sid}"))
        return sid

def reconcile(limit: int | None):
    works = fetch_works(limit)
    groups: defaultdict[str, list[dict]] = defaultdict(list)

    for w in works:
        key = normalize(w["titleKr"] or w["titleOriginal"])
        groups[key].append(w)

    moved, created = 0, 0
    for key, ws in groups.items():
        # 시리즈 대표: 이미 시리즈 있는 work 중 첫 번째, 없으면 새로
        repr_work = next((w for w in ws if w["seriesId"]), ws[0])
        repr_series_id = repr_work["seriesId"]
        if not repr_series_id:
            repr_series_id = ensure_series(
                key, repr_work["titleOriginal"] or repr_work["titleKr"]
            )
            created += 1

        # 다른 work 들을 동일 시리즈로 이동
        for w in ws:
            if w["seriesId"] != repr_series_id:
                with cursor() as cur:
                    cur.execute(
                        "UPDATE work SET seriesId=%s WHERE id=%s",
                        (repr_series_id, w["id"]),
                    )
                moved += 1

    print(f"✅  series created {created} · works moved {moved}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="작품 N개만 테스트")
    args = ap.parse_args()

    reconcile(args.limit)

if __name__ == "__main__":
    main()
