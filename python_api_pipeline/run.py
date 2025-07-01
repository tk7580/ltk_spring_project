# python_api_pipeline/run.py
"""
Unified entry-point for collectors / utilities.

예)
  python -m python_api_pipeline.run collect --source anilist --pages 5
  python -m python_api_pipeline.run fix-types  --limit 300
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

# ─────────────────────────────────────────────
# 0. 프로젝트 루트를 PYTHONPATH에 자동 추가
# ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ─────────────────────────────────────────────
# 1. 서브커맨드 ↔ 모듈 매핑
# ─────────────────────────────────────────────
MODULE_MAP = {
    # collect
    "anilist":         "collectors.anilist",
    "tmdb":            "collectors.tmdb",
    "series":          "collectors.series",
    # reconcile / fix
    "fix-types":       "reconcile.type_fixer",
    "batch-reconcile": "reconcile.batch_reconciler",   # ← ‘batch’ → ‘batch_reconciler’
    # LLM
    "enrich":          "enrich.llm",
}

# ─────────────────────────────────────────────
def _dispatch_module(mod, args):
    """
    전달된 모듈에서 main / collect / run / class Collector
    중 하나를 찾아 실행
    """
    for name in ("main", "collect", "run"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn(args)

    # 클래스 Collector 도 허용
    Collector = getattr(mod, "Collector", None)
    if Collector:
        return Collector().run(args)

    raise AttributeError(
        f"'{mod.__name__}' 모듈에 실행 가능한 "
        "엔트리포인트(main/collect/run/Collector)가 없습니다."
    )


def main() -> None:
    p = argparse.ArgumentParser(description="LTK 파이프라인 실행기")
    sub = p.add_subparsers(dest="command", required=True)

    # ── collect ──────────────────────────────
    c1 = sub.add_parser("collect", help="데이터 수집 (anilist/tmdb/series)")
    c1.add_argument("--source", choices=["anilist", "tmdb", "series"], required=True)
    c1.add_argument("--pages", type=int)
    c1.add_argument("--batch", type=int)
    c1.add_argument("--delay", type=float, default=0.5)
    c1.add_argument("--type",  type=str)

    # ── fix-types ────────────────────────────
    c2 = sub.add_parser("fix-types", help="Live-Action → Drama 매핑")
    c2.add_argument("--limit", type=int)

    # ── reconcile ───────────────────────────
    c3 = sub.add_parser("batch-reconcile", help="시리즈-워크 매핑 재조정")
    c3.add_argument("--delay", type=float, default=0.5)

    # ── LLM enrich ──────────────────────────
    c4 = sub.add_parser("enrich", help="Gemini로 한글 메타데이터 보강")
    c4.add_argument("--limit", type=int)
    c4.add_argument("--delay", type=float, default=0.0)

    args = p.parse_args()

    # collect 일 때는 source 로 모듈 결정
    key = args.source if args.command == "collect" else args.command
    mod_path = MODULE_MAP.get(key)
    if not mod_path:
        sys.exit(f"[run] MODULE_MAP 에 '{key}' 가 없음")

    mod = importlib.import_module(f"python_api_pipeline.{mod_path}")
    _dispatch_module(mod, args)


if __name__ == "__main__":
    main()
