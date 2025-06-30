#!/usr/bin/env python
"""
Unified entry-point for collectors / utilities.

예)
  python run.py collect --source anilist --pages 5 --delay 1.0
  python run.py collect --source tmdb    --type movie --pages 10
  python run.py fix-types  --limit 300
  python run.py enrich     --work-id 12345
"""
import argparse
import importlib
import sys

MODULE_MAP = {
    "anilist":    "anilist_collector",
    "tmdb":       "tmdb_collector",
    "series":     "series_collector",
    "reconcile":  "data_reconciler",
    "fix-types":  "type_fixer",
    "enrich":     "detail_enricher",
    "batch-reconcile": "series_batch_reconciler"
}


def main():
    p = argparse.ArgumentParser(description="파이프라인 실행기")
    sub = p.add_subparsers(dest="command", required=True)

    # collect 서브커맨드
    c1 = sub.add_parser("collect", help="데이터 수집 실행 (anilist, tmdb, series)")
    c1.add_argument("--source", choices=["anilist","tmdb","series"], required=True)
    c1.add_argument("--pages", type=int, default=None, help="페이지 수 (AniList/Series)")
    c1.add_argument("--batch", type=int, default=None, help="배치 크기 (TMDB)")
    c1.add_argument("--delay", type=float, default=0.5, help="각 요청 사이 대기 시간(초)")
    c1.add_argument("--type", type=str, default=None, help="TMDB collect시 type 지정(movie/tv)")

    # fix-types 서브커맨드
    c2 = sub.add_parser("fix-types", help="DB work 타입 보정 실행")
    c2.add_argument("--limit", type=int, default=None, help="최대 처리 개수")

    # reconcile 서브커맨드
    c3 = sub.add_parser("reconcile", help="데이터 재조정 실행")
    c3.add_argument("--work-id", type=int, required=False, help="단일 work id 지정")

    # enrich 서브커맨드
    c4 = sub.add_parser("enrich", help="LLM으로 메타데이터 보강")
    c4.add_argument("--limit", type=int, default=None)
    c4.add_argument("--delay", type=float, default=0.5)

    # batch-reconcile 서브커맨드
    c5 = sub.add_parser("batch-reconcile", help="시리즈 배치별 매핑")
    c5.add_argument("--delay", type=float, default=0.5)

    args = p.parse_args()

    # 어떤 모듈을 호출해야 할지 결정
    module_name = MODULE_MAP.get(args.command if args.command != "collect" else args.source)
    if not module_name:
        sys.exit(f"No module mapped for {args}")

    mod = importlib.import_module(module_name)
    # 각 스크립트는 main(args) 시그니처를 지켜야 합니다.
    mod.main(args)

if __name__ == "__main__":
    main()
