"""
프로젝트 전역에서 공통으로 사용하는 SQLAlchemy Base / Session 설정.
Naming Convention 을 지정해 FK·UK 이름, snake/camel 혼용 문제를 예방한다.
"""

from __future__ import annotations

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

# ────────────────────────────────────────────────────────────────
# 1. 환경 변수 / 설정
# ────────────────────────────────────────────────────────────────
# 환경변수나 config.py 등에 선언되어 있는 DB 접속 URL 사용
try:
    from .config import DB_URL        # e.g. "mysql+pymysql://user:pw@host:3306/ltk_spring_project"
except ImportError:                   # 테스트용 SQLite fallback
    DB_URL = os.getenv("DB_URL", "sqlite+pysqlite:///./dev.sqlite3")

# ────────────────────────────────────────────────────────────────
# 2. Naming Convention  (snake_case 자동 통일)
# ────────────────────────────────────────────────────────────────
NAMING_CONVENTION: dict[str, str] = {
    "ix":  "ix_%(column_0_label)s",
    "uq":  "uq_%(table_name)s_%(column_0_name)s",
    "ck":  "ck_%(table_name)s_%(constraint_name)s",
    "fk":  "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk":  "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base     = declarative_base(metadata=metadata)

# ────────────────────────────────────────────────────────────────
# 3. Engine / Session
# ────────────────────────────────────────────────────────────────
_engine_options = {
    "echo": False,            # 쿼리 로그 출력 여부
    "future": True,           # 2.0 스타일 API
    "pool_pre_ping": True,    # 연결 검사
}
engine = create_engine(DB_URL, **_engine_options)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

# ────────────────────────────────────────────────────────────────
# 4. FastAPI 의존성 등에서 쓸 수 있는 get_db 헬퍼
# ────────────────────────────────────────────────────────────────
def get_db():
    """`with` 대신 FastAPI Depends 용으로 쓸 수 있는 제너레이터."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
