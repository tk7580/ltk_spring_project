"""
공통 설정 로더

- .env  (프로젝트 루트) 를 우선 읽고,
- 환경변수(OS) 값이 있으면 그것을 최종값으로 사용한다.
"""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv   # pip install python-dotenv

# ─────────────────────────────────────────────────────────────
# 1. .env 로드 (.env가 없으면 건너뜀)
# ─────────────────────────────────────────────────────────────
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ─────────────────────────────────────────────────────────────
# 2. DB 환경변수 → SQLAlchemy URL 생성
# ─────────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME     = os.getenv("DB_NAME", "ltk_spring_project")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_URL      = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# ─────────────────────────────────────────────────────────────
# 3. 외부 API 키
# ─────────────────────────────────────────────────────────────
TMDB_API_KEY   : str | None = os.getenv("TMDB_API_KEY")
GEMINI_API_KEY : str | None = os.getenv("GEMINI_API_KEY")

# 필요하다면 다른 키(OpenAI 등)도 같은 방식으로 추가
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

__all__ = [
    "DB_URL",
    "TMDB_API_KEY",
    "GEMINI_API_KEY",
]
