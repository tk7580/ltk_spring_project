"""SQLAlchemy engine / session setup."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Expect DATABASE_URL env; fallback to local MySQL.
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/ltk_spring_project")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, future=True)
