# anilist_collector.py (대량 데이터 수집 및 주석 추가 최종본)
# ===================================================================
# 이 스크립트는 AniList에서 인기 애니메이션 목록을 가져와서,
# 각 애니메이션에 대한 데이터 정제/보강/신규추가 작업을 수행합니다.
#
# 데이터 수집 양을 조절하려면, 아래 main() 함수 내의
# TOTAL_PAGES_TO_FETCH 값을 수정하시면 됩니다. (26번째 줄 근처)
# ===================================================================

import requests
import time
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv, find_dotenv

# data_reconciler.py 에서 최종 완성된 함수를 임포트
from data_reconciler import process_series_from_entry_point

# --- 환경 변수 로드 ---
load_dotenv(find_dotenv())
API_URL = 'https://graphql.anilist.co'

def get_popular_anime_list(page=1, per_page=50):
    """
    AniList에서 인기있는 애니메이션 목록을 가져옵니다.
    (per_page는 최대 50까지 가능)
    """
    print(f"\n>>>> AniList에서 인기 애니메이션 목록 조회 시도 (페이지: {page}, 개수: {per_page})")
    query = '''
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        pageInfo {
          hasNextPage
        }
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

def get_processed_anilist_ids():
    """ 이미 처리된 AniList ID 목록을 DB에서 가져옵니다. """
    processed_ids = set()
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_DATABASE'), port=3306)
        cursor = connection.cursor()
        cursor.execute("SELECT sourceId FROM work_identifier WHERE sourceName = 'ANILIST_ANIME'")
        results = cursor.fetchall()
        for row in results:
            processed_ids.add(int(row[0]))
        cursor.close()
    except Error as e:
        print(f"기처리 ID 목록 조회 중 오류 발생: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
    return processed_ids


def main():
    # ==========================================================
    # ★★★ 데이터 수집 양을 조절하려면 아래 값을 수정하세요 ★★★
    # (페이지당 50개씩 데이터를 가져옵니다)
    TOTAL_PAGES_TO_FETCH = 3
    # ==========================================================

    # 1. 이미 DB에 등록된 AniList ID들을 가져와서, 중복 처리를 방지
    processed_ids = get_processed_anilist_ids()
    print(f"현재까지 DB에 등록된 AniList 작품 수: {len(processed_ids)}개")

    # 2. 지정된 페이지 수만큼 반복하여 처리
    for page_num in range(1, 21):
        anime_list = get_popular_anime_list(page=page_num, per_page=50)
        if not anime_list:
            print(f"{page_num} 페이지에서 더 이상 가져올 목록이 없습니다. 작업을 중단합니다.")
            break

        print(f"\n총 {len(anime_list)}개의 애니메이션에 대한 데이터 정제 및 보강 작업을 시작합니다.")

        # 3. 목록을 순회하며, 아직 처리되지 않은 작품에 대해서만 정제/보강 함수를 호출
        for anime in anime_list:
            anilist_id = anime['id']
            title = anime['title']['english'] or anime['title']['romaji']

            if anilist_id in processed_ids:
                print(f"\n[SKIP] '{title}' (AniList ID: {anilist_id})는 이미 처리된 작품입니다.")
                continue

            # data_reconciler.py에 있는 핵심 함수를 호출
            process_series_from_entry_point(anilist_id)

            # AniList API에 대한 예의를 지키고, 차단을 피하기 위해 잠시 대기
            print("다음 작업을 위해 2초 대기...")
            time.sleep(2)

    print("\n모든 작업이 완료되었습니다.")


if __name__ == '__main__':
    main()