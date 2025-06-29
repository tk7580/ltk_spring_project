# tmdb_collector.py (KeyError 수정 최종본)

import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv, find_dotenv
import time
import argparse

def find_work_by_external_id(cursor, source_name, source_id):
    query = "SELECT workId FROM work_identifier WHERE sourceName = %s AND sourceId = %s LIMIT 1"
    cursor.execute(query, (source_name, str(source_id)))
    result = cursor.fetchone()
    return result['workId'] if result else None

def get_or_create_genre_ids(cursor, connection, genre_names):
    genre_ids = []
    if not genre_names: return genre_ids
    select_query = "SELECT id FROM genre WHERE name = %s"
    insert_query = "INSERT INTO genre (name, regDate, updateDate) VALUES (%s, NOW(), NOW())"
    for name in genre_names:
        cursor.execute(select_query, (name,))
        result = cursor.fetchone()
        if result:
            genre_ids.append(result['id'])
        else:
            cursor.execute(insert_query, (name,))
            genre_ids.append(cursor.lastrowid)
    connection.commit()
    return genre_ids

def link_genres_to_work(cursor, connection, work_id, genre_ids):
    if not genre_ids: return
    delete_query = "DELETE FROM work_genre WHERE workId = %s"
    insert_query = "INSERT INTO work_genre (workId, genreId, regDate) VALUES (%s, %s, NOW())"
    try:
        cursor.execute(delete_query, (work_id,))
        data_to_insert = [(work_id, genre_id) for genre_id in genre_ids]
        cursor.executemany(insert_query, data_to_insert)
        connection.commit()
    except Error as e:
        print(f"  [오류] 작품-장르 연결 중 DB 에러: {e}")
        connection.rollback()

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

def find_or_create_series(cursor, connection, item_data):
    title_kr = item_data.get('titleKr')
    title_original = item_data.get('titleOriginal')

    collection_info = item_data.get('collection')
    if collection_info and collection_info.get('name'):
        series_title = collection_info['name']
        cursor.execute("SELECT id FROM series WHERE titleKr = %s OR titleOriginal = %s LIMIT 1", (series_title, series_title))
        result = cursor.fetchone()
        if result:
            return result['id']

        poster_path = f"https://image.tmdb.org/t/p/w500{collection_info.get('poster_path')}" if collection_info.get('poster_path') else None
        series_data = (series_title, series_title, None, poster_path, None, None, None, None)
        insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, studios, publisher, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_query, series_data)
        return cursor.lastrowid

    series_data = (title_kr, title_original, item_data.get('description'), item_data.get('thumbnailUrl'), None, None, item_data.get('studios'), None)
    insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, studios, publisher, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
    cursor.execute(insert_query, series_data)
    return cursor.lastrowid

def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  [오류] API 요청 실패: {url} - {e}")
        return None

def normalize_tmdb_data(item_detail, media_type):
    genres = [genre['name'] for genre in item_detail.get('genres', [])]
    types = []
    is_animation = 16 in [g['id'] for g in item_detail.get('genres', [])]

    if media_type == 'movie':
        types.append('Movie')
        if is_animation:
            types.append('Animation')
        else:
            types.append('Live-Action')
    elif media_type == 'tv':
        if is_animation:
            types.append('Animation')
        else:
            types.append('Live-Action')

    trailer_key = None
    if 'videos' in item_detail and item_detail['videos']['results']:
        for video in item_detail['videos']['results']:
            if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                trailer_key = video.get('key')
                if video.get('official'):
                    break

    trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None

    base_data = {
        'id': item_detail.get('id'), 'description': item_detail.get('overview'),
        'thumbnailUrl': f"https://image.tmdb.org/t/p/w500{item_detail.get('poster_path')}" if item_detail.get('poster_path') else None,
        'genres': genres, 'types': types,
        'collection': item_detail.get('belongs_to_collection'),
        'studios': ", ".join([c['name'] for c in item_detail.get('production_companies', [])]),
        'trailerUrl': trailer_url
    }

    if media_type == 'movie':
        creators = ", ".join([p['name'] for p in item_detail.get('credits', {}).get('crew', []) if p.get('job') == 'Director'])
        base_data.update({'titleKr': item_detail.get('title'), 'titleOriginal': item_detail.get('original_title'), 'releaseDate': item_detail.get('release_date') or None, 'episodes': 1, 'duration': item_detail.get('runtime'), 'creators': creators})
    elif media_type == 'tv':
        creators = ", ".join([p['name'] for p in item_detail.get('created_by', [])])
        base_data.update({'titleKr': item_detail.get('name'), 'titleOriginal': item_detail.get('original_name'), 'releaseDate': item_detail.get('first_air_date') or None, 'isCompleted': item_detail.get('status') == 'Ended', 'episodes': item_detail.get('number_of_episodes'), 'duration': item_detail.get('episode_run_time')[0] if item_detail.get('episode_run_time') else None, 'creators': creators})
    return base_data

def upsert_item(cursor, connection, item_summary, media_type, api_key):
    if media_type == 'tv' and 16 in item_summary.get('genre_ids', []):
        print(f"  [SKIP] '{item_summary.get('name')}' -> 애니메이션 TV 시리즈이므로 anilist_collector에서 처리합니다.")
        return

    source_name = f"TMDB_{media_type.upper()}"
    tmdb_id = item_summary.get('id')
    if not tmdb_id: return None

    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR&append_to_response=videos,credits"
    detail_data = get_api_data(detail_url)
    if not detail_data: return None

    normalized_data = normalize_tmdb_data(detail_data, media_type)

    print("-" * 40)
    print(f"  >> '{normalized_data.get('titleKr')}' 처리 시작")

    work_id = find_work_by_external_id(cursor, source_name, tmdb_id)

    if work_id:
        update_query = "UPDATE work SET titleKr=%s, titleOriginal=%s, releaseDate=%s, description=%s, thumbnailUrl=%s, studios=%s, creators=%s, episodes=%s, duration=%s, isCompleted=%s, trailerUrl=%s, updateDate=NOW() WHERE id=%s"
        params = (
            normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate'),
            normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['studios'],
            normalized_data.get('creators'), normalized_data.get('episodes'), normalized_data.get('duration'),
            normalized_data.get('isCompleted'), normalized_data.get('trailerUrl'),
            work_id
        )
        cursor.execute(update_query, params)
        print(f"  [업데이트] (workId: {work_id}) -> 정보 업데이트 완료")
    else:
        series_id = find_or_create_series(cursor, connection, normalized_data)
        insert_query = "INSERT INTO work (seriesId, regDate, updateDate, titleKr, titleOriginal, releaseDate, description, thumbnailUrl, studios, creators, episodes, duration, isCompleted, trailerUrl) VALUES (%s, NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (
            series_id, normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate'),
            normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['studios'],
            normalized_data.get('creators'), normalized_data.get('episodes'), normalized_data.get('duration'),
            normalized_data.get('isCompleted'), normalized_data.get('trailerUrl')
        )
        cursor.execute(insert_query, params)
        work_id = cursor.lastrowid
        cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())", (work_id, source_name, str(tmdb_id)))
        print(f"  [신규 저장] (workId: {work_id}) -> work, series, identifier 저장 완료")

    link_genres_to_work(cursor, connection, work_id, get_or_create_genre_ids(cursor, connection, normalized_data.get('genres', [])))
    link_types_to_work(cursor, connection, work_id, get_type_ids_from_names(cursor, normalized_data.get('types', [])))
    print(f"    - 타입 및 장르 정보 처리 완료: {normalized_data.get('types')}")

    connection.commit()

def main():
    parser = argparse.ArgumentParser(description="TMDB에서 영화 및 TV 시리즈 정보를 수집합니다.")
    parser.add_argument('--pages', type=int, default=1, help="각 목록에서 수집할 페이지 수 (페이지당 20개)")
    parser.add_argument('--type', type=str, choices=['movie', 'tv'], help="수집할 미디어 타입 (movie 또는 tv)")
    parser.add_argument('--endpoint', type=str, default='popular', choices=['popular', 'top_rated'], help="수집할 목록 (popular 또는 top_rated)")
    args = parser.parse_args()

    load_dotenv(find_dotenv())
    api_key = os.getenv('TMDB_API_KEY')
    db_host = os.getenv('DB_HOST'); db_user = os.getenv('DB_USER'); db_password = os.getenv('DB_PASSWORD'); db_database = os.getenv('DB_DATABASE')

    if not all([api_key, db_host, db_user, db_password, db_database]):
        print("에러: .env 파일에 필요한 모든 정보(API키, DB접속정보)를 설정해주세요.")
        return

    connection = None
    try:
        connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_database, port=3306)
        cursor = connection.cursor(dictionary=True, buffered=True)
        print("데이터베이스에 성공적으로 연결되었습니다.")

        media_types_to_process = [args.type] if args.type else ['movie', 'tv']

        for media_type in media_types_to_process:
            for page in range(1, args.pages + 1):
                list_url = f"https://api.themoviedb.org/3/{media_type}/{args.endpoint}?api_key={api_key}&language=ko-KR&page={page}"
                print(f"\n===== '{media_type.upper()}' / '{args.endpoint}' 데이터 처리 시작 (페이지: {page}) =====")
                list_data = get_api_data(list_url)
                if not list_data or not list_data.get('results'):
                    print("  [정보] 목록을 가져올 수 없습니다. 다음으로 넘어갑니다.")
                    continue

                print(f"  > {len(list_data['results'])}개 항목 처리 시작...")
                for item_summary in list_data['results']:
                    upsert_item(cursor, connection, item_summary, media_type, api_key)
                    time.sleep(0.5)

    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()