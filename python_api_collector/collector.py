import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import time

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
    """작품 ID와 장르 ID 목록을 받아 work_genre 테이블에 저장합니다."""
    delete_query = "DELETE FROM work_genre WHERE workId = %s"
    insert_query = "INSERT INTO work_genre (workId, genreId, regDate) VALUES (%s, %s, NOW()) ON DUPLICATE KEY UPDATE workId=workId"
    try:
        cursor.execute(delete_query, (work_id,))
        for genre_id in genre_ids:
            cursor.execute(insert_query, (work_id, genre_id))
        connection.commit()
    except Error as e:
        print(f"  [오류] 작품-장르 연결 중 DB 에러: {e}")
        connection.rollback()

def find_or_create_series(cursor, connection, item_data, media_type):
    """작품 데이터(영화/TV)를 받아, 적절한 시리즈를 찾거나 생성하고 seriesId를 반환합니다."""
    if media_type == 'tv':
        series_data = (item_data.get('titleKr'), item_data.get('titleOriginal'), item_data.get('description'), item_data.get('thumbnailUrl'), item_data.get('coverImageUrl'), item_data.get('author'))
        insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_query, series_data)
        return cursor.lastrowid

    elif media_type == 'movie':
        collection_info = item_data.get('collection')
        if collection_info and collection_info.get('name'):
            collection_name = collection_info['name']
            cursor.execute("SELECT id FROM series WHERE titleKr = %s LIMIT 1", (collection_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                collection_poster = f"https://image.tmdb.org/t/p/w500{collection_info.get('poster_path')}" if collection_info.get('poster_path') else None
                collection_backdrop = f"https://image.tmdb.org/t/p/w1280{collection_info.get('backdrop_path')}" if collection_info.get('backdrop_path') else None
                series_data = (collection_name, collection_name, None, collection_poster, collection_backdrop, None)
                insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
                cursor.execute(insert_query, series_data)
                return cursor.lastrowid
        else:
            series_data = (item_data.get('titleKr'), item_data.get('titleOriginal'), item_data.get('description'), item_data.get('thumbnailUrl'), item_data.get('coverImageUrl'), item_data.get('author'))
            insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
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
    if not video_data or not video_data.get('results'):
        return None

    for video in video_data['results']:
        # 공식(Official) 예고편(Trailer)을 우선적으로 찾습니다. 없으면 아무 예고편이나 가져옵니다.
        if video.get('site') == 'YouTube' and video.get('official') and video.get('type') == 'Trailer':
            return video.get('key')
    for video in video_data['results']:
        if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
            return video.get('key')
    return None

def get_creator_info(media_type, tmdb_id, api_key):
    """영화 감독 또는 TV 제작자 정보를 가져옵니다."""
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits?api_key={api_key}"
    credits_data = get_api_data(url)
    if not credits_data:
        return None

    if media_type == 'movie':
        for member in credits_data.get('crew', []):
            if member.get('job') == 'Director':
                return member.get('name')
    elif media_type == 'tv':
        creators = credits_data.get('created_by', [])
        if creators:
            return ", ".join([creator['name'] for creator in creators])
    return None

def normalize_item_data(item_detail, media_type, creator_name, trailer_key):
    """Movie와 TV API의 다른 필드명을 공통 형식으로 정규화합니다."""
    base_data = {
        'id': item_detail.get('id'),
        'description': item_detail.get('overview'),
        'thumbnailUrl': f"https://image.tmdb.org/t/p/w500{item_detail.get('poster_path')}" if item_detail.get('poster_path') else None,
        'coverImageUrl': f"https://image.tmdb.org/t/p/w1280{item_detail.get('backdrop_path')}" if item_detail.get('backdrop_path') else None,
        'genres': [genre['name'] for genre in item_detail.get('genres', [])],
        'author': creator_name,
        'collection': item_detail.get('belongs_to_collection'),
        'trailerUrl': f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None
    }
    if media_type == 'movie':
        base_data.update({'titleKr': item_detail.get('title'), 'titleOriginal': item_detail.get('original_title'), 'releaseDate': item_detail.get('release_date'), 'type': 'Movie', 'isCompleted': True})
    elif media_type == 'tv':
        base_data.update({'titleKr': item_detail.get('name'), 'titleOriginal': item_detail.get('original_name'), 'releaseDate': item_detail.get('first_air_date'), 'type': 'TV', 'isCompleted': item_detail.get('status') == 'Ended'})
    return base_data

def process_item(cursor, connection, item_summary, media_type, api_key):
    """하나의 아이템(영화/TV)을 가져와 DB에 저장 또는 업데이트합니다."""
    source_name = f"TMDB_{media_type.upper()}"
    tmdb_id = item_summary.get('id')
    if not tmdb_id:
        print("  [경고] TMDB ID가 없는 데이터는 건너뜁니다.")
        return None, None

    existing_work_id = find_work_by_external_id(cursor, source_name, tmdb_id)

    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR"
    detail_data = get_api_data(detail_url)
    if not detail_data:
        return None, None

    creator_name = get_creator_info(media_type, tmdb_id, api_key)
    trailer_key = get_trailer_key(media_type, tmdb_id, api_key)
    normalized_data = normalize_item_data(detail_data, media_type, creator_name, trailer_key)

    print("-" * 40)

    work_id = None
    operation_type = None

    if existing_work_id:
        work_id = existing_work_id
        cursor.execute("UPDATE work SET titleKr=%s, titleOriginal=%s, releaseDate=%s, description=%s, thumbnailUrl=%s, isCompleted=%s, trailerUrl=%s, updateDate=NOW() WHERE id=%s",
                       (normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['isCompleted'], normalized_data['trailerUrl'], work_id))
        cursor.execute("SELECT seriesId FROM work WHERE id = %s", (work_id,))
        series_id = cursor.fetchone()[0]
        cursor.execute("UPDATE series SET author=%s, coverImageUrl=%s, updateDate=NOW() WHERE id=%s",
                       (normalized_data['author'], normalized_data['coverImageUrl'], series_id))
        print(f"  [업데이트] '{normalized_data.get('titleKr')}' (workId: {work_id}) -> 정보 업데이트 완료")
        operation_type = "update"
    else:
        series_id = find_or_create_series(cursor, connection, normalized_data, media_type)
        print(f"  [시리즈 처리] '{normalized_data['titleKr']}' -> seriesId: {series_id}에 소속")

        cursor.execute("INSERT INTO work (seriesId, titleKr, titleOriginal, type, releaseDate, description, thumbnailUrl, trailerUrl, isCompleted, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
                       (series_id, normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data['type'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['trailerUrl'], normalized_data['isCompleted']))
        work_id = cursor.lastrowid
        print(f"  [신규 저장] '{normalized_data['titleKr']}' -> work 저장 완료 (workId: {work_id})")

        cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())",
                       (work_id, source_name, str(tmdb_id)))
        print(f"  [매핑] workId {work_id}와 {source_name} ID {tmdb_id} 매핑 완료")
        operation_type = "save"

    genre_names = normalized_data.get('genres', [])
    if genre_names:
        genre_ids = get_or_create_genre_ids(cursor, connection, genre_names)
        link_genres_to_work(cursor, connection, work_id, genre_ids)
        print(f"    - 장르 정보 {len(genre_ids)}건 처리 완료")

    connection.commit()
    return operation_type, work_id

def main():
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_database = os.getenv('DB_DATABASE')

    if not all([api_key, db_host, db_user, db_password, db_database]):
        print("에러: .env 파일에 필요한 모든 정보(API키, DB접속정보)를 설정해주세요.")
        return

    connection = None
    try:
        connection = mysql.connector.connect( host=db_host, user=db_user, password=db_password, database=db_database, port=3306 )
        cursor = connection.cursor()
        print("데이터베이스에 성공적으로 연결되었습니다.")

        endpoints_to_fetch = ['popular', 'top_rated']
        pages_to_fetch = 3
        total_saved = 0
        total_updated = 0

        for media_type in ['movie', 'tv']:
            for endpoint in endpoints_to_fetch:
                for page in range(1, pages_to_fetch + 1):
                    list_url = f"https://api.themoviedb.org/3/{media_type}/{endpoint}?api_key={api_key}&language=ko-KR&page={page}"
                    print(f"\n===== '{media_type.upper()}' / '{endpoint}' 데이터 처리 시작 (페이지: {page}) =====")

                    list_data = get_api_data(list_url)
                    if not list_data or not list_data.get('results'):
                        print(f"  [정보] 목록을 가져올 수 없습니다. 다음으로 넘어갑니다.")
                        continue

                    print(f"  > {len(list_data['results'])}개 항목 처리 시작...")
                    for item_summary in list_data['results']:
                        result_type, _ = process_item(cursor, connection, item_summary, media_type, api_key)
                        if result_type == "save":
                            total_saved += 1
                        elif result_type == "update":
                            total_updated += 1
                        time.sleep(0.2)

        print(f"\n\n===== 전체 처리 완료 =====")
        print(f"신규 저장: {total_saved}건")
        print(f"정보 업데이트: {total_updated}건")

    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()