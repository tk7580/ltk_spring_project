# ---------- db_utils.py ----------
#!/usr/bin/env python
"""
공통 DB 커넥션 & 커서 헬퍼
────────────────────────
• .env 로부터 DB 접속 정보 로드
• use_pure=True  →  mysql-connector C-extension 오류(3.13) 우회
"""
import os
import contextlib
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # .env 로드
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", "*****" if os.getenv("DB_PASSWORD") else None)
print("DB_NAME:", os.getenv("DB_NAME"))

def get_connection():
    """
    환경변수로부터 DB 연결을 생성합니다.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),  # ex) ltk-spring_project
        use_pure=True,
    )

@contextlib.contextmanager
def cursor(dictionary=True, buffered=True):
    """
    get_connection으로 생성한 커넥션을 사용해 커서를 yield하며 처리 후 자동 커밋/종료합니다.
    """
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=dictionary, buffered=buffered)
        yield cur
        conn.commit()
    finally:
        cur.close()
        conn.close()


# 호환성 alias
get_db_connection = get_connection
