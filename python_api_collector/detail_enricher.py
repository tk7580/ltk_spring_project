#!/usr/bin/env python3
# detail_enricher.py

import os
import time
import json
import requests
from dotenv import load_dotenv
from db_utils import get_db_connection

# ──────────────────────────────────────────────────────────────────────────────
# 환경변수 로드 & 검증
load_dotenv()
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
GEMINI_PROJECT_ID = os.getenv("GEMINI_PROJECT_ID")
if not GEMINI_API_KEY or not GEMINI_PROJECT_ID:
    raise EnvironmentError("환경변수 GEMINI_API_KEY 또는 GEMINI_PROJECT_ID가 설정되지 않았습니다.")

# v1beta2 text-bison-001 모델 엔드포인트
BASE_URL = (
    f"https://generativelanguage.googleapis.com"
    f"/v1beta2/projects/{GEMINI_PROJECT_ID}"
    f"/locations/us-central1/models/text-bison-001:generateMessage"
)

# LLM 호출 템플릿
LLM_PROMPT_TEMPLATE = (
    "아래 원본 정보를 참고하여, JSON 객체로 한글 제목(koreanTitle)과 한글 줄거리(koreanSynopsis)을 작성하세요.\n"
    "원본 제목: {original_title}\n"
    "원본 줄거리: {original_synopsis}\n"
    "반환 JSON 예시: {\"koreanTitle\":\"...\",\"koreanSynopsis\":\"...\"}"
)

# ──────────────────────────────────────────────────────────────────────────────
def ask_llm(prompt: str, retries: int = 3, backoff: float = 1.0) -> dict:
    """
    LLM에 텍스트를 보내고 JSON 응답을 받습니다. 실패 시 재시도 로직 포함.
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    payload = {
        "prompt": {"text": prompt},
        "modelParams": {"temperature": 0.2}
    }
    for i in range(1, retries+1):
        try:
            res = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(f"[LLM] 시도 {i} 실패: {e}")
            if i < retries:
                time.sleep(backoff * i)
    print("[LLM] 모든 재시도 실패 — 빈 결과 리턴")
    return {}


def enrich_single(work: dict) -> bool:
    """
    단일 work 레코드를 LLM으로 보강합니다.
    """
    prompt = LLM_PROMPT_TEMPLATE.format(
        original_title=work.get("title_romaji") or work.get("title_english") or work.get("title_native", ""),
        original_synopsis=work.get("description") or ""
    )
    raw = ask_llm(prompt)
    # Gemini 응답에서 content 추출
    candidates = raw.get("candidates", [])
    content = candidates[0].get("content", "") if candidates else ""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print(f"[LLM] JSON 파싱 실패: work_id={work['id']}")
        return False

    # DB 업데이트
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE work SET
                        title_kr = COALESCE(%s, title_kr),
                        description_kr = COALESCE(%s, description_kr)
        WHERE id = %s
        """,
        (
            data.get("koreanTitle"),
            data.get("koreanSynopsis"),
            work["id"]
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[LLM] 보강 완료: work_id={work['id']}")
    return True


def main(limit: int = None, delay: float = 0.5):
    # DB에서 보강이 필요한 레코드 조회
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, title_romaji, title_english, title_native, description
        FROM work
        WHERE title_kr IS NULL OR description_kr IS NULL
        """ + (" LIMIT %s" if limit else ""),
        (limit,) if limit else ()
    )
    works = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"[LLM] 총 {len(works)}개 작품 보강 시작")
    for work in works:
        enrich_single(work)
        time.sleep(delay)
    print("[LLM] 모든 보강 작업 완료")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LLM으로 작품 메타데이터 한글 보강 스크립트")
    parser.add_argument("--limit", type=int, default=None, help="최대 보강할 작품 수")
    parser.add_argument("--delay", type=float, default=0.5, help="각 호출 간 대기 시간(초)")
    args = parser.parse_args()
    main(limit=args.limit, delay=args.delay)
