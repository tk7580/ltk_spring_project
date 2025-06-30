#!/usr/bin/env python
"""
공통 DB 커넥션 & 커서 헬퍼
────────────────────────
• .env 로부터 DB 접속 정보 로드
• use_pure=True  →  mysql-connector C-extension 오류(3.13) 우회
"""
import os, contextlib, mysql.connector
from dotenv import load_dotenv

load_dotenv()  # .env 로드

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME"),     # ex) ltk-spring_project
        use_pure=True,                     # ★ python 드라이버 사용
    )

@contextlib.contextmanager
def cursor(dictionary=True, buffered=True):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=dictionary, buffered=buffered)
        yield cur
        conn.commit()
    finally:
        cur.close()
        conn.close()
