"""Use Gemini-Pro to fill missing Korean titles/descriptions."""
import os, time
from datetime import datetime
import google.generativeai as genai
from sqlalchemy import select, or_

from ..config import GEMINI_API_KEY
from ..db import SessionLocal
from ..models import Work

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """너는 엔터테인먼트 메타데이터 전문가야. 주어진 원어(영어) 정보를 바탕으로
한국어 제목과 줄거리를 작성해 줘. 줄거리는 **두 문단**, 각 2~3문장으로.
반드시 아래 **출력 형식**을 지켜.

<출력 형식>
제목: (한글 제목)
줄거리:
(한글 줄거리)"""

def _call_gemini(title_en:str, description_en:str|None) -> str:
    model = genai.GenerativeModel("gemini-pro")
    prompt = (
        SYSTEM_PROMPT +
        f"\n\n영어 제목: {title_en or '(없음)'}\n" +
        f"영어 줄거리: {description_en or '(없음)'}"
    )
    resp = model.generate_content(prompt, generation_config={"temperature":0.7})
    return resp.text.strip()

def _parse(text:str):
    parts = text.split("줄거리:")
    title_line = parts[0].split("제목:")[-1].strip()
    summary = parts[1].strip() if len(parts)>1 else ""
    return title_line, summary

def enrich(work:Work, delay:float=0.0):
    resp = _call_gemini(work.titleOriginal, work.description)
    title_kr, summary_kr = _parse(resp)
    if title_kr and not work.titleKr:
        work.titleKr = title_kr
    if summary_kr and not work.description:
        work.description = summary_kr
    work.updateDate = datetime.utcnow()
    time.sleep(delay)

def main(args):
    limit = args.limit or 200
    delay = args.delay or 0.0
    sess = SessionLocal()
    targets = sess.scalars(
        select(Work).where(
            or_(Work.titleKr.is_(None), Work.description.is_(None))
        ).limit(limit)
    ).all()
    print(f"[enrich] 대상 {len(targets)}건")
    for w in targets:
        try:
            enrich(w, delay)
            sess.commit()
            print(f"[enrich] ✅ Work {w.id}")
        except Exception as e:
            sess.rollback()
            print(f"[enrich] ❌ Work {w.id} → {e}")
    sess.close()
    print("[enrich] 작업 종료")
