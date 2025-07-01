"""Unified CLI entry for pipeline sub-modules."""
import importlib
import argparse
import sys

def _dispatch(path:str, arg_ns):
    try:
        mod = importlib.import_module(f"python_api_pipeline.{path}")
        if hasattr(mod, "main"):
            mod.main(arg_ns)
        else:
            print(f"[run] module '{path}' has no main()")
    except Exception as e:
        import traceback
        print(f"[run] 모듈 '{path}' 로드 실패: {e}")
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="collect/enrich/...")
    parser.add_argument("--source")
    parser.add_argument("--type")
    parser.add_argument("--pages", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--delay", type=float)
    args = parser.parse_args()

    cmd_map = {
        "collect": {
            "anilist": "collectors.anilist",
            "tmdb": "collectors.tmdb",
            "series": "collectors.series",
        },
        "enrich": {
            "llm": "enrich.llm"
        },
        "fix-types": {
            "": "reconcile.type_fixer"
        },
        "batch-reconcile": {
            "": "reconcile.series_batch"
        }
    }

    if args.command not in cmd_map:
        print("Unknown command")
        sys.exit(1)

    sub = args.source or ""
    path = cmd_map[args.command].get(sub)
    if not path:
        print("Unknown source/type")
        sys.exit(1)

    _dispatch(path, args)

if __name__ == "__main__":
    main()
