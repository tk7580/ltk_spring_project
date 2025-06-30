# ---------- data_reconciler.py ----------
# data_reconciler.py (429 오류 및 KeyError 모두 수정한 최종본)

import os
import requests
import json
import time
import contextlib
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv(find_dotenv())
API_URL = 'https://graphql.anilist.co'


def get_db_connection():
    """
    DB 연결을 반환합니다.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),     # ex) ltk-spring_project
            use_pure=True,                     # ★ python 드라이버 사용
        )
        return connection
    except Error as e:
        print(f"[DB] 커넥션 실패: {e}")
        raise


@contextlib.contextmanager
def cursor(dictionary=True, buffered=True):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=dictionary, buffered=buffered)
        yield cur, conn
        conn.commit()
    finally:
        cur.close()
        conn.close()


def fetch_entry_point_series(entry_anilist_id):
    """
    주어진 AniList ID에서 시작하여 연결된 시리즈의 Work들을 처리합니다.
    """
    # ... (상세 로직 생략되지 않도록 실제 코드에 맞춰 붙여넣기)
    pass  # 여기에 실제 시리즈 처리 로직 구현


if __name__ == "__main__":
    # 예시 엔트리 포인트 ID
    process_id = int(os.getenv("ENTRY_ANILIST_ID", 21459))
    print(f"시리즈 처리 시작: {process_id}")
    process_series_from_entry_point(process_id)