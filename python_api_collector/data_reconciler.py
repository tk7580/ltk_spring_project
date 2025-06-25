# data_reconciler.py (파일 경로 문제 해결 최종본)

import os
import requests
import json
import time
from dotenv import load_dotenv, find_dotenv # find_dotenv 임포트 추가
import mysql.connector
from mysql.connector import Error

# --- 환경 변수 및 API 설정 ---
# 현재 위치부터 상위 폴더로 올라가며 .env 파일을 찾아 로드
load_dotenv(find_dotenv())

API_URL = 'https://graphql.anilist.co'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

# --- DB Helper Functions ---
def get_db_connection():
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_DATABASE')

    # --- 디버깅을 위한 print문 (이제 정상적으로 값이 출력될 것입니다) ---
    print("\n--- .env 파일에서 읽어온 DB 접속 정보 ---")
    print(f"DB_HOST: {host}")
    print(f"DB_USER: {user}")
    print(f"DB_PASSWORD: {'설정됨' if password else '!!! 설정 안됨 !!!'}")
    print(f"DB_DATABASE: {database}")
    print("------------------------------------\n")

    try:
        connection = mysql.connector.connect(
            host=host, user=user,
            password=password, database=database, port=3306)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"DB 연결 오류 (host: {host}): {e}")
        return None

def find_or_create_series_in_db(cursor, title):
    search_term = f"%{title}%"
    cursor.execute("SELECT id FROM series WHERE titleKr LIKE %s OR titleOriginal LIKE %s LIMIT 1", (search_term, search_term))
    result = cursor.fetchone()
    if result:
        print(f"-> 기존 시리즈 '{title}'(을)를 DB에서 찾았습니다. (seriesId: {result['id']})")
        return result['id']
    else:
        print(f"-> DB에 없는 새로운 시리즈 '{title}'. 신규 생성합니다.")
        cursor.execute("INSERT INTO series (regDate, updateDate, titleKr) VALUES (NOW(), NOW(), %s)", (title,))
        new_series_id = cursor.lastrowid
        print(f"   - 신규 시리즈 생성 완료. (seriesId: {new_series_id})")
        return new_series_id

def find_work_id_by_anilist_id(cursor, anilist_id):
    cursor.execute("SELECT workId FROM work_identifier WHERE sourceName = 'ANILIST_ANIME' AND sourceId = %s", (str(anilist_id),))
    result = cursor.fetchone()
    return result['workId'] if result else None

def get_full_details_from_anilist(anilist_id):
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        id
        title { romaji english native }
        format
        status
        description(asHtml: false)
        startDate { year month day }
        episodes
        duration
        genres
        studios(isMain: true) { nodes { name } }
        coverImage { extraLarge }
        trailer { id site }
      }
    }
    '''
    variables = {'id': anilist_id}
    print(f"   (AniList에서 ID '{anilist_id}'의 상세 정보 조회...)")
    response = requests.post(API_URL, json={'query': query, 'variables': variables})
    response.raise_for_status()
    return response.json()['data']['Media']

def fetch_anime_with_relations(anime_id):
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        id
        title { romaji english native }
        relations { edges { relationType(version: 2) node { id } } }
      }
    }
    '''
    variables = {'id': anime_id}
    response = requests.post(API_URL, json={'query': query, 'variables': variables})
    response.raise_for_status()
    return response.json()['data']['Media']


# --- Main Processing Function ---
def process_series_from_entry_point(entry_anilist_id):
    print(f"\n{'='*20} [ 시리즈 처리 시작 (시작 ID: {entry_anilist_id}) ] {'='*20}")
    connection = get_db_connection()
    if not connection: return
    cursor = connection.cursor(dictionary=True)

    try:
        main_work_data = fetch_anime_with_relations(entry_anilist_id)
        works_to_process_ids = [main_work_data['id']]
        for edge in main_work_data.get('relations', {}).get('edges', []):
            if edge.get('relationType') == 'SEQUEL':
                works_to_process_ids.append(edge['node']['id'])
        print(f"✅ 총 {len(works_to_process_ids)}개 작품(시즌) 처리 대상 확정: {works_to_process_ids}")

        series_id = find_or_create_series_in_db(cursor, main_work_data['title']['english'] or main_work_data['title']['romaji'])
        connection.commit()

        for anilist_id in works_to_process_ids:
            work_id_in_db = find_work_id_by_anilist_id(cursor, anilist_id)
            details = get_full_details_from_anilist(anilist_id)
            title_kr = details['title']['english'] or details['title']['romaji']
            print(f"\n--- '{title_kr}' (AniList ID: {anilist_id}) 처리 ---")

            if work_id_in_db:
                print(f"  [UPDATE]: DB에 workId '{work_id_in_db}'(으)로 존재. 정보 보강 실행.")
                update_query = """
                UPDATE work SET
                    seriesId = %s, type = %s, description = %s, episodes = %s,
                    duration = %s, studios = %s, isCompleted = %s, updateDate = NOW(),
                    titleKr = %s, titleOriginal = %s, releaseDate = %s, thumbnailUrl = %s, trailerUrl = %s
                WHERE id = %s
                """
                studios_str = ", ".join(node['name'] for node in details.get('studios', {}).get('nodes', []))
                is_completed = 1 if details.get('status') == 'FINISHED' else 0
                start_date_str = f"{details['startDate']['year']}-{(details['startDate']['month'] or 1):02d}-{(details['startDate']['day'] or 1):02d}"
                trailer_url = f"https://www.youtube.com/watch?v={details['trailer']['id']}" if details.get('trailer') and details['trailer']['site'] == 'youtube' else None
                params = (
                    series_id, 'Animation', details.get('description'), details.get('episodes'),
                    details.get('duration'), studios_str, is_completed, title_kr, details['title']['native'],
                    start_date_str, details.get('coverImage', {}).get('extraLarge'), trailer_url,
                    work_id_in_db
                )
                cursor.execute(update_query, params)
                print(f"  -> 기존 work(id:{work_id_in_db}) 정보 업데이트 완료 (새 seriesId: {series_id} 연결)")
            else:
                print(f"  [INSERT]: DB에 없는 작품. 신규 추가 실행.")
                start_date_str = f"{details['startDate']['year']}-{(details['startDate']['month'] or 1):02d}-{(details['startDate']['day'] or 1):02d}"
                studios_str = ", ".join(node['name'] for node in details.get('studios', {}).get('nodes', []))
                trailer_url = f"https://www.youtube.com/watch?v={details['trailer']['id']}" if details.get('trailer') and details['trailer']['site'] == 'youtube' else None
                insert_query = """
                INSERT INTO work (seriesId, regDate, updateDate, titleKr, titleOriginal, type, releaseDate, episodes, duration, studios, description, thumbnailUrl, trailerUrl, isCompleted)
                VALUES (%s, NOW(), NOW(), %s, %s, 'Animation', %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    series_id, title_kr, details['title']['native'], start_date_str, details.get('episodes'),
                    details.get('duration'), studios_str, details.get('description'),
                    details.get('coverImage', {}).get('extraLarge'), trailer_url, 1 if details.get('status') == 'FINISHED' else 0
                )
                cursor.execute(insert_query, params)
                new_work_id = cursor.lastrowid
                cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, 'ANILIST_ANIME', %s, NOW(), NOW())", (new_work_id, str(anilist_id)))
                print(f"  -> 신규 work 추가 완료 (새 workId: {new_work_id})")

        connection.commit()
    except Exception as e:
        print(f"오류 발생: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nDB 연결이 종료되었습니다.")

if __name__ == "__main__":
    test_id = 21459 # 나의 히어로 아카데미아 1기
    process_series_from_entry_point(test_id)