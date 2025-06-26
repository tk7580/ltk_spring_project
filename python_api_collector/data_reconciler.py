# data_reconciler.py (429 오류 및 KeyError 모두 수정한 최종본)

import os
import requests
import json
import time
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error

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

def get_type_ids_from_names(cursor, type_names):
    type_ids = []
    if not type_names: return type_ids
    format_strings = ','.join(['%s'] * len(type_names))
    query = f"SELECT id FROM work_type WHERE name IN ({format_strings})"
    cursor.execute(query, tuple(type_names))
    results = cursor.fetchall()
    for row in results:
        type_ids.append(row['id'])
    return type_ids

def link_types_to_work(cursor, connection, work_id, type_ids):
    if not type_ids: return
    delete_query = "DELETE FROM work_type_mapping WHERE workId = %s"
    insert_query = "INSERT INTO work_type_mapping (workId, typeId, regDate) VALUES (%s, %s, NOW())"
    try:
        cursor.execute(delete_query, (work_id,))
        data_to_insert = [(work_id, type_id) for type_id in type_ids]
        cursor.executemany(insert_query, data_to_insert)
        connection.commit()
    except Error as e:
        print(f"  [오류] 작품-타입 연결 중 DB 에러: {e}")
        connection.rollback()

def determine_types_from_anilist(anilist_data):
    types = {'Animation'}
    anilist_format = anilist_data.get('format')
    if anilist_format == 'MOVIE':
        types.add('Movie')
    return list(types)

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
            # ★★★ [수정] 각 시즌 처리 전에도 짧은 딜레이 추가하여 429 오류 방지 ★★★
            time.sleep(1)

            work_id_in_db = find_work_id_by_anilist_id(cursor, anilist_id)
            details = get_full_details_from_anilist(anilist_id)
            title_kr = details['title']['english'] or details['title']['romaji']
            print(f"\n--- '{title_kr}' (AniList ID: {anilist_id}) 처리 ---")

            type_names = determine_types_from_anilist(details)
            type_ids = get_type_ids_from_names(cursor, type_names)

            if work_id_in_db:
                print(f"  [UPDATE]: DB에 workId '{work_id_in_db}'(으)로 존재. 정보 보강 실행.")
                update_query = "UPDATE work SET seriesId = %s, description = %s, episodes = %s, duration = %s, studios = %s, isCompleted = %s, updateDate = NOW(), titleKr = %s, titleOriginal = %s, releaseDate = %s, thumbnailUrl = %s, trailerUrl = %s WHERE id = %s"
                start_date_str = f"{details['startDate']['year']}-{(details['startDate']['month'] or 1):02d}-{(details['startDate']['day'] or 1):02d}"
                studios_str = ", ".join(node['name'] for node in details.get('studios', {}).get('nodes', []))
                trailer_url = f"https://www.youtube.com/watch?v={details['trailer']['id']}" if details.get('trailer') and details['trailer']['site'] == 'youtube' else None
                params = (series_id, details.get('description'), details.get('episodes'), details.get('duration'), studios_str, 1 if details.get('status') == 'FINISHED' else 0, title_kr, details['title']['native'], start_date_str, details.get('coverImage', {}).get('extraLarge'), trailer_url, work_id_in_db)
                cursor.execute(update_query, params)
                link_types_to_work(cursor, connection, work_id_in_db, type_ids)
                print(f"  -> 기존 work(id:{work_id_in_db}) 정보/타입 업데이트 완료: {type_names}")
            else:
                print(f"  [INSERT]: DB에 없는 작품. 신규 추가 실행.")
                start_date_str = f"{details['startDate']['year']}-{(details['startDate']['month'] or 1):02d}-{(details['startDate']['day'] or 1):02d}"
                studios_str = ", ".join(node['name'] for node in details.get('studios', {}).get('nodes', []))
                trailer_url = f"https://www.youtube.com/watch?v={details['trailer']['id']}" if details.get('trailer') and details['trailer']['site'] == 'youtube' else None
                insert_query = "INSERT INTO work (seriesId, regDate, updateDate, titleKr, titleOriginal, releaseDate, episodes, duration, studios, description, thumbnailUrl, trailerUrl, isCompleted) VALUES (%s, NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                params = (series_id, title_kr, details['title']['native'], start_date_str, details.get('episodes'), details.get('duration'), studios_str, details.get('description'), details.get('coverImage', {}).get('extraLarge'), trailer_url, 1 if details.get('status') == 'FINISHED' else 0)
                cursor.execute(insert_query, params)
                new_work_id = cursor.lastrowid
                cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, 'ANILIST_ANIME', %s, NOW(), NOW())", (new_work_id, str(anilist_id)))
                link_types_to_work(cursor, connection, new_work_id, type_ids)
                print(f"  -> 신규 work 추가 완료 (새 workId: {new_work_id}), 타입: {type_names}")

        connection.commit()
    except Exception as e:
        print(f"오류 발생: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print(f"\n{'='*25} [ 처리 완료 ] {'='*25}")


if __name__ == "__main__":
    process_series_from_entry_point(21459)