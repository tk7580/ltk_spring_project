#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_enricher.py
---------------
LLM에게 국내 공식 한글 제목과 한국어 줄거리를 요청하여
Work 엔티티의 titleKr, descriptionKr 필드를 보강(enrich)합니다.
"""

import argparse
from llm_client import ask_llm    # LLM 호출 유틸
from data.models import Work       # 실제 ORM 모델 경로로 수정하세요

LLM_PROMPT_TEMPLATE = (
    "Given the English title '{original_title}', find the official Korean title "
    "and synopsis as released in South Korea "
    "(e.g. on Crunchyroll Korea, Netflix KR, Naver). "
    "Return JSON with keys: koreanTitle, koreanSynopsis."
)


def enrich_with_korean_metadata(work):
    """
    단일 Work 객체에 대해 LLM을 호출해 한글 제목/줄거리를 채웁니다.
    """
    prompt = LLM_PROMPT_TEMPLATE.format(original_title=work.titleOriginal)
    response = ask_llm(prompt)
    # LLM 응답이 JSON 형태라고 가정
    korean_info = response.json()

    # 기존 값이 없거나 null인 경우에만 덮어쓰기
    work.titleKr = korean_info.get("koreanTitle") or work.titleKr
    work.descriptionKr = korean_info.get("koreanSynopsis") or work.descriptionKr
    work.save()
    print(f"Enriched Work id={work.id} with Korean metadata.")


def main():
    parser = argparse.ArgumentParser(
        description="Enrich Works with official Korean metadata via LLM."
    )
    parser.add_argument(
        "--limit", type=int, default=500,
        help="Max number of Works to enrich"
    )
    args = parser.parse_args()

    # 보강이 필요한 Work들을 fetch 하는 클래스메소드
    works = Work.fetch_pending_korean_enrichment(limit=args.limit)

    for w in works:
        try:
            enrich_with_korean_metadata(w)
        except Exception as e:
            print(f"Failed to enrich work id={w.id}: {e}")

    print("LLM enrichment completed.")


if __name__ == "__main__":
    main()