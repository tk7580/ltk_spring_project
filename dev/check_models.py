"""
모델 ↔ 실제 DB 테이블/컬럼 불일치를 사전에 찾아내는 유틸.
$ python dev/check_models.py
"""

from __future__ import annotations

import sys
from sqlalchemy import inspect
from python_api_pipeline.db import Base, engine

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

def main() -> None:
    insp   = inspect(engine)
    errors = []

    for cls in Base.__subclasses__():
        table_name   = cls.__table__.name
        mapper_cols  = {prop.key for prop in inspect(cls).attrs}
        table_cols   = set(insp.get_columns(table_name, resolve_fks=False))
        diff_mapper  = mapper_cols - table_cols
        diff_table   = table_cols  - mapper_cols

        if diff_mapper or diff_table:
            errors.append(
                f"[{table_name}] mapper-only {sorted(diff_mapper)} | "
                f"table-only {sorted(diff_table)}"
            )

    if errors:
        print(f"{RED}❌  mismatch detected!{RESET}")
        for err in errors:
            print("   •", err)
        sys.exit(1)
    else:
        print(f"{GREEN}✅  all models & tables are consistent.{RESET}")

if __name__ == "__main__":
    main()
