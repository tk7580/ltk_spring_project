#!/usr/bin/env python
"""
detail_enricher.py
──────────────────
1) work 중 titleKr·description·thumbnailUrl 이 빈 행을 조회
2) (1차) TMDB /search/movie or /search/tv 로 검색 → 한국어 데이터 가져오기
3) (2차) 실패 시 LLM(Gemini) + google 검색으로 한글 제목·줄거리 추출
4) UPDATE work … SET titleKr=…, description=…, thumbnailUrl=… WHERE id=…
"""

import os, argparse, requests, time, json, re
from db_utils import cursor
from title_utils import pick_best_title
from llm_enricher import query_llm  # <— 기존 LLM util 그대로 사용

TMDB_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

HEADERS = {"Accept-Language": "ko-KR"}

def search_tmdb(name, year=None, tv=False):
    typ = "tv" if tv else "movie"
    url = f"https://api.themoviedb.org/3/search/{typ}"
    params = {"api_key": TMDB_KEY, "query": name, "include_adult": "false", "language": "ko-KR"}
    if year and not tv:
        params["year"] = year
    r = requests.get(url, params=params, timeout=10, headers=HEADERS)
    r.raise_for_status()
    results = r.json()["results"]
    return results[0] if results else None

def tmdb_details(item, tv=False):
    typ = "tv" if tv else "movie"
    url = f"https://api.themoviedb.org/3/{typ}/{item['id']}"
    r = requests.get(url, params={"api_key": TMDB_KEY, "language":"ko-KR"}, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_incomplete(limit):
    with cursor() as cur:
        cur.execute("""
            SELECT id, titleKr, titleOriginal, releaseDate
            FROM work
            WHERE (titleKr IS NULL OR titleKr='')
               OR (description IS NULL OR description='')
               OR (thumbnailUrl IS NULL OR thumbnailUrl='')
            LIMIT %s
        """, (limit,))
        return cur.fetchall()

def enrich_from_tmdb(w):
    name = w["titleOriginal"] or w["titleKr"]
    year = w["releaseDate"].year if w["releaseDate"] else None
    for tv in (False, True):   # 먼저 movie, 그다음 tv
        hit = search_tmdb(name, year, tv)
        if hit:
            det = tmdb_details(hit, tv)
            return {
                "titleKr": det.get("title") or det.get("name"),
                "description": det.get("overview"),
                "thumbnailUrl": TMDB_IMG + det["poster_path"] if det.get("poster_path") else None
            }
    return None

KW_RX = re.compile(r"[가-힣]+")

def enrich_from_llm(w):
    query = f"{w['titleOriginal'] or w['titleKr']} 애니메이션 줄거리 한글 제목"
    answer = query_llm(query, max_tokens=512)
    # 아주 단순 파싱 예시
    title_match = KW_RX.search(answer.split("\n",1)[0])
    title_kr = title_match.group(0) if title_match else None
    description = answer.strip()
    return {"titleKr": title_kr, "description": description, "thumbnailUrl": None}

def update_work(wid, data):
    sets, vals = [], []
    for col in ("titleKr","description","thumbnailUrl"):
        if data.get(col):
            sets.append(f"{col}=%s")
            vals.append(data[col])
    if not sets:
        return False
    vals.append(wid)
    with cursor() as cur:
        cur.execute(f"UPDATE work SET {', '.join(sets)}, updateDate=NOW() WHERE id=%s", vals)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=100, help="최대 처리 행")
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()

    works = fetch_incomplete(args.limit)
    for w in works:
        wid = w["id"]
        data = enrich_from_tmdb(w)
        if not data:
            data = enrich_from_llm(w)
        if update_work(wid, data):
            print(f"[✓] work {wid} 업데이트")
        else:
            print(f"[–] work {wid} 건너뜀")
        time.sleep(args.delay)

if __name__ == "__main__":
    main()
