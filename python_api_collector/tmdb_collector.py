# tmdb_collector.py (다대다 타입 구조 대응 최종본)

import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv, find_dotenv
import time
import argparse

def find_work_by_external_id(cursor, source_name, source_id):
    """외부 ID로 우리 DB에 저장된 work의 고유 ID(PK)를 찾습니다."""
    query = "SELECT workId FROM work_identifier WHERE sourceName = %s AND sourceId = %s LIMIT 1"
    try:
        cursor.execute(query, (source_name, str(source_id)))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"  [오류] 외부 ID 조회 중 DB 에러: {e}")
        return None

def get_or_create_genre_ids(cursor, connection, genre_names):
    """장르 이름 목록을 받아 DB에 없으면 저장하고, 모든 장르의 ID 목록을 반환합니다."""
    genre_ids = []
    if not genre_names: return genre_ids
    select_query = "SELECT id FROM genre WHERE name = %s"
    insert_query = "INSERT INTO genre (name, regDate, updateDate) VALUES (%s, NOW(), NOW())"
    for name in genre_names:
        cursor.execute(select_query, (name,))
        result = cursor.fetchone()
        if result:
            genre_ids.append(result[0])
        else:
            cursor.execute(insert_query, (name,))
            genre_ids.append(cursor.lastrowid)
    connection.commit()
    return genre_ids

def link_genres_to_work(cursor, connection, work_id, genre_ids):
    """작품 ID와 장르 ID 목록을 받아 work_genre 테이블에 저장합니다."""
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
    """타입 이름 목록으로 work_type 테이블에서 ID 목록을 가져옵니다."""
    type_ids = []
    if not type_names: return type_ids
    format_strings = ','.join(['%s'] * len(type_names))
    query = f"SELECT id FROM work_type WHERE name IN ({format_strings})"
    cursor.execute(query, tuple(type_names))
    results = cursor.fetchall()
    for row in results:
        type_ids.append(row[0])
    return type_ids

def link_types_to_work(cursor, connection, work_id, type_ids):
    """작품 ID와 타입 ID 목록으로 work_type_mapping 테이블에 데이터를 저장합니다."""
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

def find_or_create_series(cursor, connection, item_data, media_type):
    """작품 데이터(영화/TV)를 받아, 적절한 시리즈를 찾거나 생성하고 seriesId를 반환합니다."""
    if media_type == 'tv':
        series_data = (item_data.get('titleKr'), item_data.get('titleOriginal'), item_data.get('description'), item_data.get('thumbnailUrl'), item_data.get('coverImageUrl'), item_data.get('author'), item_data.get('studios'), item_data.get('publisher'))
        insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, studios, publisher, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_query, series_data)
        return cursor.lastrowid

    elif media_type == 'movie':
        collection_info = item_data.get('collection')
        if collection_info and collection_info.get('name'):
            collection_name = collection_info['name']
            cursor.execute("SELECT id FROM series WHERE titleKr = %s OR titleOriginal = %s LIMIT 1", (collection_name, collection_name))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                series_data = (collection_name, collection_name, None, f"https://image.tmdb.org/t/p/w500{collection_info.get('poster_path')}" if collection_info.get('poster_path') else None, f"https://image.tmdb.org/t/p/w1280{collection_info.get('backdrop_path')}" if collection_info.get('backdrop_path') else None, item_data.get('author'), item_data.get('studios'), item_data.get('publisher'))
                insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, studios, publisher, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
                cursor.execute(insert_query, series_data)
                return cursor.lastrowid
        else:
            series_data = (item_data.get('titleKr'), item_data.get('titleOriginal'), item_data.get('description'), item_data.get('thumbnailUrl'), item_data.get('coverImageUrl'), item_data.get('author'), item_data.get('studios'), item_data.get('publisher'))
            insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, studios, publisher, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
            cursor.execute(insert_query, series_data)
            return cursor.lastrowid

    return None

def get_api_data(url):
    """주어진 URL로 API를 요청하고 JSON 결과를 반환합니다."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  [오류] API 요청 실패: {url} - {e}")
        return None

def get_trailer_key(media_type, tmdb_id, api_key):
    """작품의 YouTube 예고편 키를 가져옵니다."""
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos?api_key={api_key}"
    video_data = get_api_data(url)
    if not video_data or not video_data.get('results'): return None
    for video in video_data['results']:
        if video.get('site') == 'YouTube' and video.get('official') and video.get('type') == 'Trailer':
            return video.get('key')
    for video in video_data['results']:
        if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
            return video.get('key')
    return None

def get_credits_and_companies(media_type, tmdb_id, api_key):
    """감독/제작자, 제작사 정보를 가져옵니다."""
    credits_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits?api_key={api_key}"
    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR"

    credits_data = get_api_data(credits_url)
    detail_data = get_api_data(detail_url)

    creator, studios = None, None
    if media_type == 'movie' and credits_data:
        for member in credits_data.get('crew', []):
            if member.get('job') == 'Director':
                creator = member.get('name'); break
    elif media_type == 'tv' and detail_data and detail_data.get('created_by'):
        creator = ", ".join([p['name'] for p in detail_data['created_by']])
    if detail_data and detail_data.get('production_companies'):
        studios = ", ".join([c['name'] for c in detail_data['production_companies']])
    return creator, studios

def normalize_tmdb_data(item_detail, media_type, creator, studios, trailer_key):
    """API 응답을 우리 DB 스키마에 맞게 정규화된 딕셔너리로 변환합니다."""
    genres = [genre['name'] for genre in item_detail.get('genres', [])]

    types = []
    if media_type == 'movie':
        types.append('Movie')
    elif media_type == 'tv':
        types.append('TV Series')

    # TMDB 장르 ID '16'은 Animation 입니다.
    if 16 in [genre['id'] for genre in item_detail.get('genres', [])]:
        types.append('Animation')
        if '드라마' in genres:
            types.append('Drama')

    base_data = {
        'id': item_detail.get('id'), 'description': item_detail.get('overview'),
        'thumbnailUrl': f"https://image.tmdb.org/t/p/w500{item_detail.get('poster_path')}" if item_detail.get('poster_path') else None,
        'genres': genres, 'types': types,
        'author': creator, 'studios': studios,
        'collection': item_detail.get('belongs_to_collection'),
        'trailerUrl': f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None
    }
    if media_type == 'movie':
        base_data.update({'titleKr': item_detail.get('title'), 'titleOriginal': item_detail.get('original_title'), 'releaseDate': item_detail.get('release_date') or None, 'isCompleted': True, 'isOriginal': True, 'episodes': 1, 'duration': item_detail.get('runtime'), 'creators': creator})
    elif media_type == 'tv':
        base_data.update({'titleKr': item_detail.get('name'), 'titleOriginal': item_detail.get('original_name'), 'releaseDate': item_detail.get('first_air_date') or None, 'isCompleted': item_detail.get('status') == 'Ended', 'isOriginal': True, 'episodes': item_detail.get('number_of_episodes'), 'duration': item_detail.get('episode_run_time')[0] if item_detail.get('episode_run_time') else None, 'creators': creator})
    return base_data

def upsert_item(cursor, connection, item_summary, media_type, api_key):
    source_name = f"TMDB_{media_type.upper()}"
    tmdb_id = item_summary.get('id')
    if not tmdb_id: return None

    work_id = find_work_by_external_id(cursor, source_name, tmdb_id)

    # 업데이트 전, Animation 타입으로 이미 교정되었는지 확인
    if work_id:
        cursor.execute("SELECT wt.name FROM work_type_mapping wtm JOIN work_type wt ON wtm.typeId = wt.id WHERE wtm.workId = %s", (work_id,))
        existing_types = [row[0] for row in cursor.fetchall()]
        if 'Animation' in existing_types:
            print(f"  [SKIP] workId: {work_id} -> 이미 'Animation' 타입으로 교정된 작품이므로, TMDB 데이터로 덮어쓰지 않습니다.")
            return

    detail_data = get_api_data(f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR&append_to_response=credits,videos")
    if not detail_data: return None

    creator, studios = get_credits_and_companies(media_type, tmdb_id, api_key)
    trailer_key = get_trailer_key(media_type, tmdb_id, api_key)
    normalized_data = normalize_tmdb_data(detail_data, media_type, creator, studios, trailer_key)

    print("-" * 40)
    print(f"  >> '{normalized_data.get('titleKr')}' 처리 시작")

    if work_id:
        update_work_query = "UPDATE work SET titleKr=%s, titleOriginal=%s, releaseDate=%s, description=%s, thumbnailUrl=%s, trailerUrl=%s, isCompleted=%s, episodes=%s, duration=%s, creators=%s, studios=%s, updateDate=NOW() WHERE id=%s"
        cursor.execute(update_work_query, (normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate'), normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['trailerUrl'], normalized_data['isCompleted'], normalized_data['episodes'], normalized_data['duration'], normalized_data['creators'], normalized_data['studios'], work_id))
        print(f"  [업데이트] (workId: {work_id}) -> 정보 업데이트 완료")
        operation_type = "update"
    else:
        series_id = find_or_create_series(cursor, connection, normalized_data, media_type)
        insert_work_query = "INSERT INTO work (seriesId, regDate, updateDate, titleKr, titleOriginal, isOriginal, releaseDate, episodes, duration, creators, studios, isCompleted, description, thumbnailUrl, trailerUrl) VALUES (%s, NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_work_query, (series_id, normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data['isOriginal'], normalized_data.get('releaseDate'), normalized_data['episodes'], normalized_data['duration'], normalized_data['creators'], normalized_data['studios'], normalized_data['isCompleted'], normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['trailerUrl']))
        work_id = cursor.lastrowid
        cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())", (work_id, source_name, str(tmdb_id)))
        print(f"  [신규 저장] (workId: {work_id}) -> work, series, identifier 저장 완료")
        operation_type = "save"

    # 장르 및 타입 처리
    link_genres_to_work(cursor, connection, work_id, get_or_create_genre_ids(cursor, connection, normalized_data.get('genres', [])))
    print(f"    - 장르 정보 처리 완료")
    link_types_to_work(cursor, connection, work_id, get_type_ids_from_names(cursor, normalized_data.get('types', [])))
    print(f"    - 타입 정보 처리 완료: {normalized_data.get('types')}")

    connection.commit()
    return operation_type

def main():
    parser = argparse.ArgumentParser(description="TMDB에서 영화 및 TV 시리즈 정보를 수집합니다.")
    parser.add_argument('--type', type=str, choices=['movie', 'tv'], help="수집할 미디어 타입 (movie 또는 tv)")
    parser.add_argument('--endpoint', type=str, default='popular', choices=['popular', 'top_rated'], help="수집할 목록")
    parser.add_argument('--pages', type=int, default=5, help="각 목록에서 수집할 페이지 수")
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
        cursor = connection.cursor(buffered=True) # fetchone() 후 다른 execute를 위해 buffered=True
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