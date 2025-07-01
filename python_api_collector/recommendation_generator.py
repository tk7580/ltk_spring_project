#!/usr/bin/env python3
# recommendation_generator.py

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

# LLM 엔드포인트 설정 (v1beta2 text-bison-001)
BASE_URL = (
    f"https://generativelanguage.googleapis.com"
    f"/v1beta2/projects/{GEMINI_PROJECT_ID}"
    f"/locations/us-central1/models/text-bison-001:generateMessage"
)

# ──────────────────────────────────────────────────────────────────────────────
def ask_llm(prompt: str) -> dict:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    payload = {
        "prompt": {"text": prompt},
        "modelParams": {"temperature": 0.3}
    }
    res = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
    res.raise_for_status()
    return res.json()

# ──────────────────────────────────────────────────────────────────────────────
def fetch_watched_titles(member_id: int) -> list:
    """DB에서 해당 멤버의 시청 완료된 작품 제목 리스트를 조회합니다."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT COALESCE(w.titleKr, w.titleOriginal) AS title
        FROM work w
        JOIN member_watched_work mw ON w.id = mw.work_id
        WHERE mw.member_id = %s
        """, (member_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r["title"] for r in rows]

# ──────────────────────────────────────────────────────────────────────────────
def main(member_id: int, output: str = None):
    watched = fetch_watched_titles(member_id)
    if not watched:
        print(f"멤버({member_id})의 시청 기록이 없습니다.")
        return

    # 프롬프트 작성
    prompt = (
        f"사용자가 다음 작품들을 시청했습니다: {', '.join(watched)}. "
        "이 사용자가 좋아할 만한 5개의 작품을 한국어 제목(koreanTitle), 영문 제목(englishTitle), "
        "간단 줄거리(synopsis)로 JSON 배열 형태로 반환해주세요. "
        "예시 포맷: [{'{'}\"koreanTitle\":\"...\",\"englishTitle\":\"...\",\"synopsis\":\"...\"{'}'}]")

    # LLM 호출
    raw = ask_llm(prompt)
    content = raw.get("candidates", [{}])[0].get("content", "")
    try:
        recommendations = json.loads(content)
    except json.JSONDecodeError:
        print("[LLM] JSON 파싱 실패, 원시 응답:\n", content)
        return

    # 결과 저장 또는 출력
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)
        print(f"추천 결과가 {output}에 저장되었습니다.")
    else:
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LLM 기반 추천 생성 스크립트")
    parser.add_argument("--member", type=int, required=True, help="멤버 ID")
    parser.add_argument("--output", type=str, default=None,
                        help="저장할 JSON 파일 경로 (미지정 시 콘솔 출력)")
    args = parser.parse_args()
    main(member_id=args.member, output=args.output)
