#!/usr/bin/env python
"""
Unified entry-point for collectors / utilities.

예)
  python run.py collect --source anilist --pages 5 --delay 1.0
  python run.py collect --source tmdb    --type movie --pages 10
  python run.py fix-types  --limit 300
  python run.py enrich     --work-id 12345
"""
import argparse, importlib, sys

MODULE_MAP = {
    "anilist":    "anilist_collector",
    "tmdb":       "tmdb_collector",
    "series":     "series_collector",
    "reconcile":  "data_reconciler",
    "fix-types":  "type_fixer",
    "enrich":     "llm_enricher",
}

def main():
    p = argparse.ArgumentParser(prog="run.py")
    sub = p.add_subparsers(dest="command", required=True)

    # ----- collect ----------------------------------------------------------
    collect = sub.add_parser("collect")
    collect.add_argument("--source", choices=["anilist", "tmdb"], required=True)
    collect.add_argument("--type",   choices=["movie", "tv"], help="tmdb only")
    collect.add_argument("--pages",  type=int, default=1)
    collect.add_argument("--delay",  type=float, default=0.5)

    # ----- fix-types --------------------------------------------------------
    sub.add_parser("fix-types").add_argument("--limit", type=int, default=500)

    # ----- enrich -----------------------------------------------------------
    sub.add_parser("enrich").add_argument("--work-id", type=int, required=True)

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
