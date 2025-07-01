# python_api_pipeline/enrich/llm.py
"""
Use **Google Gemini Pro** to fill in missing Korean titles / descriptions.

Requirements
------------
pip install google-generativeai~=0.4
.env (또는 환경변수)에 GEMINI_API_KEY=...
"""

from __future__ import annotations

import time
from datetime import datetime
from argparse import Namespace

import google.generativeai as genai
from sqlalchemy import select, or_

from ..config import GEMINI_API_KEY          # .env 로부터
from ..db      import SessionLocal
from ..models  import Work


# ────────────────────────────────────────────────────
# 0. Gemini 초기화
# ────────────────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)


# ────────────────────────────────────────────────────
# 1. 프롬프트 템플릿
# ────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
너는 엔터테인먼트 메타데이터 전문가야. 주어진 원어(영어) 정보를 바탕으로
한국어 제목과 줄거리를 작성해 줘. 줄거리는 **두 문단**, 각 2~3문장으로.
반드시 아래 **출력 형식**을 지켜.

<출력 형식>
제목: (한글 제목)
줄거리:
(한글 줄거리)
"""


def _call_gemini(title_en: str, description_en: str | None) -> str:
    """Gemini-Pro 호출 후 응답 텍스트 반환"""
    model  = genai.GenerativeModel("gemini-pro")
    prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + f"영어 제목: {title_en or '(없음)'}\n"
            + f"영어 줄거리: {description_en or '(없음)'}"
    )
    resp = model.generate_content(
        prompt,
        generation_config={"temperature": 0.7},
    )
    return resp.text.strip()


def _parse_response(text: str) -> tuple[str, str]:
    """`제목:` / `줄거리:` 라벨 기준 파싱"""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title_kr, summary_kr = "", ""
    for ln in lines:
        low = ln.lower()
        if low.startswith("제목"):
            title_kr = ln.split(":", 1)[1].strip()
        elif low.startswith("줄거리"):
            summary_kr = ln.split(":", 1)[1].strip()
        else:
            summary_kr += ("\n" if summary_kr else "") + ln
    return title_kr, summary_kr


def enrich_work(work: Work, delay: float = 0.0) -> None:
    """단일 Work 레코드 보강"""
    try:
        resp_text = _call_gemini(work.title_original, work.description)
        title_kr, summary_kr = _parse_response(resp_text)

        if title_kr and not work.title_kr:
            work.title_kr = title_kr
        if summary_kr and not work.description:
            work.description = summary_kr
        work.update_date = datetime.utcnow()

    except Exception as e:
        # 트랜잭션 롤백은 상위에서 수행
        raise RuntimeError(f"Gemini 실패 (Work {work.id}): {e}") from e
    finally:
        time.sleep(delay)  # rate-limit 완화용


# ────────────────────────────────────────────────────
# 2. CLI 엔트리포인트
# ────────────────────────────────────────────────────
def main(args: Namespace) -> None:
    """$ python -m python_api_pipeline.run enrich ..."""
    limit = args.limit or 200
    delay = args.delay or 0.0

    if not GEMINI_API_KEY:
        print("[enrich] GEMINI_API_KEY 가 설정되어 있지 않습니다 — 종료")
        return

    sess = SessionLocal()

    # 제목 또는 줄거리가 NULL **또는 빈 문자열**인 작품
    stmt = (
        select(Work)
        .where(
            or_(
                Work.title_kr.is_(None),
                Work.title_kr == "",
                Work.description.is_(None),
                Work.description == "",
                )
        )
        .limit(limit)
    )

    works = sess.scalars(stmt).all()
    print(f"[enrich] 대상 {len(works)}건")

    for w in works:
        try:
            enrich_work(w, delay=delay)
            sess.commit()
            print(f"[enrich] ✅  Work {w.id} 완료")
        except Exception as err:
            sess.rollback()
            print(f"[enrich] ❌  Work {w.id} 실패 → {err}")

    sess.close()
    print("[enrich] 작업 종료")
