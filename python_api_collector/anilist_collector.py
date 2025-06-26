# anilist_collector.py (명령줄 인수 기능 추가)

import requests
import time
import os
import argparse # ★★★ argparse 라이브러리 임포트 ★★★
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv, find_dotenv

# data_reconciler.py 에서 최종 완성된 함수를 임포트
from data_reconciler import process_series_from_entry_point

# --- 환경 변수 로드 ---
load_dotenv(find_dotenv())
API_URL = 'https://graphql.anilist.co'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_DATABASE'), port=3306)
        return connection
    except Error as e:
        print(f"DB 연결 오류: {e}")
        return None

def get_popular_anime_list(page=1, per_page=50):
    """
    AniList에서 인기있는 애니메이션 목록을 가져옵니다.
    """
    print(f"\n>>>> AniList에서 인기 애니메이션 목록 조회 시도 (페이지: {page}, 개수: {per_page})")
    query = '''
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        media (type: ANIME, sort: POPULARITY_DESC, isAdult: false) {
          id
          title {
            english
            romaji
          }
        }
      }
    }
    '''
    variables = {'page': page, 'perPage': per_page}
    try:
        response = requests.post(API_URL, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()['data']['Page']['media']
    except Exception as e:
        print(f"애니메이션 목록을 가져오는 중 오류 발생: {e}")
        return []

def get_processed_anilist_ids(connection):
    """ 이미 처리된 AniList ID 목록을 DB에서 가져옵니다. """
    processed_ids = set()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT sourceId FROM work_identifier WHERE sourceName = 'ANILIST_ANIME'")
        results = cursor.fetchall()
        for row in results:
            processed_ids.add(int(row[0]))
        cursor.close()
    except Error as e:
        print(f"기처리 ID 목록 조회 중 오류 발생: {e}")
    return processed_ids


def main():
    # ★★★ [수정] 명령줄 인수 파서 설정 ★★★
    parser = argparse.ArgumentParser(description="AniList에서 인기 애니메이션 정보를 수집하고 데이터를 정제합니다.")
    parser.add_argument('--pages', type=int, default=1, help="수집할 페이지 수 (페이지당 50개)")
    args = parser.parse_args()

    connection = get_db_connection()
    if not connection: return

    processed_ids = get_processed_anilist_ids(connection)
    print(f"현재까지 DB에 등록된 AniList 작품 수: {len(processed_ids)}개")
    connection.close()

    # ★★★ [수정] 하드코딩된 변수 대신 args.pages 사용 ★★★
    for page_num in range(1, args.pages + 1):
        anime_list = get_popular_anime_list(page=page_num, per_page=50)
        if not anime_list:
            print(f"{page_num} 페이지에서 더 이상 가져올 목록이 없습니다. 작업을 중단합니다.")
            break

        print(f"\n총 {len(anime_list)}개의 애니메이션에 대한 데이터 정제 및 보강 작업을 시작합니다.")

        for anime in anime_list:
            anilist_id = anime['id']
            title = anime['title']['english'] or anime['title']['romaji']

            if anilist_id in processed_ids:
                print(f"\n[SKIP] '{title}' (AniList ID: {anilist_id})는 이미 처리된 작품입니다.")
                continue

            process_series_from_entry_point(anilist_id)

            print("다음 작업을 위해 2초 대기...")
            time.sleep(2)

    print("\n모든 작업이 완료되었습니다.")


if __name__ == '__main__':
    main()