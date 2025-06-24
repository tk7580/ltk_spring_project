import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import time

# --- DB Helper Functions ---

def find_work_by_external_id(cursor, source_name, source_id):
    query = "SELECT workId FROM work_identifier WHERE sourceName = %s AND sourceId = %s LIMIT 1"
    try:
        cursor.execute(query, (source_name, str(source_id)))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"  [오류] 외부 ID 조회 중 DB 에러: {e}")
        return None

def get_or_create_genre_ids(cursor, connection, genre_names):
    genre_ids = []
    select_query = "SELECT id FROM genre WHERE name = %s"
    insert_query = "INSERT INTO genre (name, regDate, updateDate) VALUES (%s, NOW(), NOW())"
    for name in genre_names:
        cursor.execute(select_query, (name,))
        result = cursor.fetchone()
        if result:
            genre_ids.append(result[0])
        else:
            cursor.execute(insert_query, (name,))
            genre_id = cursor.lastrowid
            genre_ids.append(genre_id)
            print(f"    - 신규 장르 '{name}' -> genre 테이블 저장 (genreId: {genre_id})")
    connection.commit()
    return genre_ids

def link_genres_to_work(cursor, connection, work_id, genre_ids):
    delete_query = "DELETE FROM work_genre WHERE workId = %s"
    insert_query = "INSERT INTO work_genre (workId, genreId, regDate) VALUES (%s, %s, NOW()) ON DUPLICATE KEY UPDATE workId=workId"
    try:
        cursor.execute(delete_query, (work_id,))
        if genre_ids:
            data_to_insert = [(work_id, genre_id) for genre_id in genre_ids]
            cursor.executemany(insert_query, data_to_insert)
        connection.commit()
    except Error as e:
        print(f"  [오류] 작품-장르 연결 중 DB 에러: {e}")
        connection.rollback()

def find_or_create_series(cursor, connection, item_data):
    collection_info = item_data.get('collection')
    if collection_info and collection_info.get('name'):
        collection_name = collection_info['name']
        cursor.execute("SELECT id FROM series WHERE titleKr = %s LIMIT 1", (collection_name,))
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

# --- TMDB API Helper Functions ---

def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  [오류] API 요청 실패: {url} - {e}")
        return None

def get_trailer_key(media_type, tmdb_id, api_key):
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
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits?api_key={api_key}"
    credits_data = get_api_data(url)
    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}"
    detail_data = get_api_data(detail_url)

    creator = None
    studios = None

    if media_type == 'movie':
        if credits_data:
            for member in credits_data.get('crew', []):
                if member.get('job') == 'Director':
                    creator = member.get('name')
                    break
    elif media_type == 'tv':
        if detail_data and detail_data.get('created_by'):
            creator = ", ".join([p['name'] for p in detail_data['created_by']])

    if detail_data and detail_data.get('production_companies'):
        studios = ", ".join([c['name'] for c in detail_data['production_companies']])

    return creator, studios

def normalize_tmdb_data(item_detail, media_type, creator, studios, trailer_key):
    base_data = {
        'id': item_detail.get('id'),
        'description': item_detail.get('overview'),
        'thumbnailUrl': f"https://image.tmdb.org/t/p/w500{item_detail.get('poster_path')}" if item_detail.get('poster_path') else None,
        'coverImageUrl': f"https://image.tmdb.org/t/p/w1280{item_detail.get('backdrop_path')}" if item_detail.get('backdrop_path') else None,
        'genres': [genre['name'] for genre in item_detail.get('genres', [])],
        'author': creator, # 영화감독 또는 TV 제작자
        'studios': studios,
        'collection': item_detail.get('belongs_to_collection'),
        'trailerUrl': f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None
    }
    if media_type == 'movie':
        base_data.update({'titleKr': item_detail.get('title'), 'titleOriginal': item_detail.get('original_title'), 'releaseDate': item_detail.get('release_date'), 'type': 'Movie', 'isCompleted': True, 'episodes': 1, 'duration': item_detail.get('runtime')})
    elif media_type == 'tv':
        base_data.update({'titleKr': item_detail.get('name'), 'titleOriginal': item_detail.get('original_name'), 'releaseDate': item_detail.get('first_air_date'), 'type': 'TV', 'isCompleted': item_detail.get('status') == 'Ended', 'episodes': item_detail.get('number_of_episodes'), 'duration': item_detail.get('episode_run_time')[0] if item_detail.get('episode_run_time') else None})
    return base_data

# ===== Main DB Upsert Function =====

def upsert_item(cursor, connection, item_summary, media_type, api_key):
    source_name = f"TMDB_{media_type.upper()}"
    tmdb_id = item_summary.get('id')
    if not tmdb_id: return None

    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR"
    detail_data = get_api_data(detail_url)
    if not detail_data: return None

    creator, studios = get_credits_and_companies(media_type, tmdb_id, api_key)
    trailer_key = get_trailer_key(media_type, tmdb_id, api_key)
    normalized_data = normalize_tmdb_data(detail_data, media_type, creator, studios, trailer_key)

    print("-" * 40)

    work_id = find_work_by_external_id(cursor, source_name, tmdb_id)

    if work_id:
        # UPDATE
        update_work_query = "UPDATE work SET titleKr=%s, titleOriginal=%s, releaseDate=%s, description=%s, thumbnailUrl=%s, trailerUrl=%s, isCompleted=%s, episodes=%s, duration=%s, creators=%s, studios=%s, updateDate=NOW() WHERE id=%s"
        cursor.execute(update_work_query, (normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['trailerUrl'], normalized_data['isCompleted'], normalized_data['episodes'], normalized_data['duration'], normalized_data['author'], normalized_data['studios'], work_id))
        print(f"  [업데이트] '{normalized_data.get('titleKr')}' (workId: {work_id}) -> 정보 업데이트 완료")
        operation_type = "update"
    else:
        # INSERT
        series_id = find_or_create_series(cursor, connection, normalized_data)

        insert_work_query = "INSERT INTO work (seriesId, titleKr, titleOriginal, type, releaseDate, description, thumbnailUrl, trailerUrl, isCompleted, episodes, duration, creators, studios, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_work_query, (series_id, normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data['type'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['trailerUrl'], normalized_data['isCompleted'], normalized_data['episodes'], normalized_data['duration'], normalized_data['author'], normalized_data['studios']))
        work_id = cursor.lastrowid

        cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())", (work_id, source_name, str(tmdb_id)))
        print(f"  [신규 저장] '{normalized_data.get('titleKr')}' -> work, series, identifier 저장 완료")
        operation_type = "save"

    genre_names = normalized_data.get('genres', [])
    if genre_names:
        genre_ids = get_or_create_genre_ids(cursor, connection, genre_names)
        link_genres_to_work(cursor, connection, work_id, genre_ids)
        print(f"    - 장르 정보 {len(genre_ids)}건 처리 완료")

    connection.commit()
    return operation_type

def main():
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')
    db_host = os.getenv('DB_HOST'); db_user = os.getenv('DB_USER'); db_password = os.getenv('DB_PASSWORD'); db_database = os.getenv('DB_DATABASE')

    connection = None
    try:
        connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_database, port=3306)
        cursor = connection.cursor()
        print("데이터베이스에 성공적으로 연결되었습니다.")

        endpoints_to_fetch = ['popular', 'top_rated']
        pages_to_fetch = 3
        total_saved = 0; total_updated = 0

        for media_type in ['movie', 'tv']:
            for endpoint in endpoints_to_fetch:
                for page in range(1, pages_to_fetch + 1):
                    list_url = f"https://api.themoviedb.org/3/{media_type}/{endpoint}?api_key={api_key}&language=ko-KR&page={page}"
                    print(f"\n===== '{media_type.upper()}' / '{endpoint}' 데이터 처리 시작 (페이지: {page}) =====")

                    list_data = get_api_data(list_url)
                    if not list_data or not list_data.get('results'): continue

                    for item_summary in list_data['results']:
                        result_type = upsert_item(cursor, connection, item_summary, media_type, api_key)
                        if result_type == "save": total_saved += 1
                        elif result_type == "update": total_updated += 1
                        time.sleep(0.1)

        print(f"\n\n===== 전체 처리 완료 ====="); print(f"신규 저장: {total_saved}건"); print(f"정보 업데이트: {total_updated}건")
    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close(); connection.close(); print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()