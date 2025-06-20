import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import time

# ===== DB Helper Functions =====

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

# ===== 신규 시리즈/컬렉션 처리 함수 =====
def find_or_create_series(cursor, connection, item_data, media_type):
    """
    작품 데이터(영화/TV)를 받아, 적절한 시리즈를 찾거나 생성하고 seriesId를 반환합니다.
    """
    # TV 시리즈의 경우, TV 쇼 자체가 시리즈입니다.
    if media_type == 'tv':
        series_data = (item_data.get('titleKr'), item_data.get('titleOriginal'), item_data.get('description'), item_data.get('thumbnailUrl'), item_data.get('coverImageUrl'), item_data.get('author'))
        insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_query, series_data)
        return cursor.lastrowid

    # 영화의 경우, '컬렉션' 정보가 있는지 확인합니다.
    elif media_type == 'movie':
        collection_info = item_data.get('collection')
        if collection_info and collection_info.get('name'):
            # 컬렉션 정보가 있으면, 컬렉션 이름으로 기존 시리즈를 검색합니다.
            collection_name = collection_info['name']
            cursor.execute("SELECT id FROM series WHERE titleKr = %s LIMIT 1", (collection_name,))
            result = cursor.fetchone()
            if result:
                # 기존에 같은 이름의 시리즈가 있으면 해당 ID를 반환합니다.
                return result[0]
            else:
                # 없으면 컬렉션 정보로 새로운 시리즈를 생성합니다.
                collection_poster = f"https://image.tmdb.org/t/p/w500{collection_info.get('poster_path')}" if collection_info.get('poster_path') else None
                collection_backdrop = f"https://image.tmdb.org/t/p/w1280{collection_info.get('backdrop_path')}" if collection_info.get('backdrop_path') else None
                series_data = (collection_name, collection_name, None, collection_poster, collection_backdrop, None)
                insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
                cursor.execute(insert_query, series_data)
                return cursor.lastrowid
        else:
            # 컬렉션 정보가 없는 독립 영화는, 영화 자체 정보를 시리즈로 생성합니다. (기존 방식)
            series_data = (item_data.get('titleKr'), item_data.get('titleOriginal'), item_data.get('description'), item_data.get('thumbnailUrl'), item_data.get('coverImageUrl'), item_data.get('author'))
            insert_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())"
            cursor.execute(insert_query, series_data)
            return cursor.lastrowid

    return None

# ===== TMDB API Helper Functions =====

def get_api_data(url):
    """주어진 URL로 API를 요청하고 JSON 결과를 반환합니다."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  [오류] API 요청 실패: {e}")
    except json.JSONDecodeError:
        print(f"  [오류] API 응답 파싱 실패. 응답 내용: {response.text}")
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
            return ", ".join([creator['name'] for creator in creators]) # 여러 제작자 저장
    return None

def normalize_item_data(item_detail, media_type, creator_name):
    """Movie와 TV API의 다른 필드명을 공통 형식으로 정규화합니다."""
    base_data = {
        'id': item_detail.get('id'),
        'description': item_detail.get('overview'),
        'thumbnailUrl': f"https://image.tmdb.org/t/p/w500{item_detail.get('poster_path')}" if item_detail.get('poster_path') else None,
        'coverImageUrl': f"https://image.tmdb.org/t/p/w1280{item_detail.get('backdrop_path')}" if item_detail.get('backdrop_path') else None,
        'genres': [genre['name'] for genre in item_detail.get('genres', [])],
        'author': creator_name,
        'collection': item_detail.get('belongs_to_collection') # 영화 컬렉션 정보 추가
    }
    if media_type == 'movie':
        base_data.update({'titleKr': item_detail.get('title'), 'titleOriginal': item_detail.get('original_title'), 'releaseDate': item_detail.get('release_date'), 'type': 'Movie', 'isCompleted': True})
    elif media_type == 'tv':
        base_data.update({'titleKr': item_detail.get('name'), 'titleOriginal': item_detail.get('original_name'), 'releaseDate': item_detail.get('first_air_date'), 'type': 'TV', 'isCompleted': item_detail.get('status') == 'Ended'})
    return base_data

# ===== Main DB Operation Functions =====

def process_item(cursor, connection, item_summary, media_type, api_key):
    """하나의 아이템(영화/TV)을 가져와 DB에 저장 또는 업데이트합니다."""
    source_name = f"TMDB_{media_type.upper()}"
    tmdb_id = item_summary.get('id')
    if not tmdb_id:
        print("  [경고] TMDB ID가 없는 데이터는 건너뜁니다.")
        return None, None

    existing_work_id = find_work_by_external_id(cursor, source_name, tmdb_id)

    # 상세 정보 API를 호출하여 장르 등 추가 정보 획득
    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR"
    detail_data = get_api_data(detail_url)
    if not detail_data:
        return None, None

    creator_name = get_creator_info(media_type, tmdb_id, api_key)
    normalized_data = normalize_item_data(detail_data, media_type, creator_name)

    print("-" * 40)

    work_id_for_genre = None
    operation_type = None

    if existing_work_id:
        # 업데이트 로직
        cursor.execute("UPDATE work SET titleKr=%s, titleOriginal=%s, releaseDate=%s, description=%s, thumbnailUrl=%s, isCompleted=%s, updateDate=NOW() WHERE id=%s",
                       (normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['isCompleted'], existing_work_id))
        cursor.execute("SELECT seriesId FROM work WHERE id = %s", (existing_work_id,))
        series_id = cursor.fetchone()[0]
        cursor.execute("UPDATE series SET author=%s, coverImageUrl=%s, updateDate=NOW() WHERE id=%s",
                       (normalized_data['author'], normalized_data['coverImageUrl'], series_id))
        print(f"  [업데이트] '{normalized_data.get('titleKr')}' (workId: {existing_work_id}) -> 정보 업데이트 완료")
        work_id_for_genre = existing_work_id
        operation_type = "update"
    else:
        # 신규 저장 로직
        series_id = find_or_create_series(cursor, connection, normalized_data, media_type)
        print(f"  [시리즈 처리] '{normalized_data['titleKr']}' -> seriesId: {series_id}에 소속")

        cursor.execute("INSERT INTO work (seriesId, titleKr, titleOriginal, type, releaseDate, description, thumbnailUrl, isCompleted, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
                       (series_id, normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data['type'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['isCompleted']))
        work_id_for_genre = cursor.lastrowid
        print(f"  [신규 저장] '{normalized_data['titleKr']}' -> work 저장 완료 (workId: {work_id_for_genre})")

        cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())",
                       (work_id_for_genre, source_name, str(tmdb_id)))
        print(f"  [매핑] workId {work_id_for_genre}와 {source_name} ID {tmdb_id} 매핑 완료")
        operation_type = "save"

    genre_names = normalized_data.get('genres', [])
    if genre_names:
        genre_ids = get_or_create_genre_ids(cursor, connection, genre_names)
        link_genres_to_work(cursor, connection, work_id_for_genre, genre_ids)
        print(f"    - 장르 정보 {len(genre_ids)}건 처리 완료")

    connection.commit()
    return operation_type, work_id_for_genre

def main():
    # .env 파일 및 DB 연결 설정 (이전과 동일)
    load_dotenv(); api_key = os.getenv('TMDB_API_KEY'); db_host = os.getenv('DB_HOST'); db_user = os.getenv('DB_USER'); db_password = os.getenv('DB_PASSWORD'); db_database = os.getenv('DB_DATABASE')
    if not all([api_key, db_host, db_user, db_password, db_database]): print("에러: .env 파일에 필요한 모든 정보(API키, DB접속정보)를 설정해주세요."); return
    connection = None
    try:
        connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_database, port=3306); cursor = connection.cursor(); print("데이터베이스에 성공적으로 연결되었습니다.")

        media_types_to_process = ['movie', 'tv']
        total_saved = 0; total_updated = 0

        for media_type in media_types_to_process:
            page = 1
            list_url = f"https://api.themoviedb.org/3/{media_type}/popular?api_key={api_key}&language=ko-KR&page={page}"
            print(f"\n===== '{media_type.upper()}' 데이터 처리 시작 (페이지: {page}) =====")
            popular_list = get_api_data(list_url)
            if not popular_list or not popular_list.get('results'): print(f"  [정보] '{media_type.upper()}' 타입의 인기 목록을 가져올 수 없습니다."); continue

            for item_summary in popular_list['results']:
                result_type, _ = process_item(cursor, connection, item_summary, media_type, api_key)
                if result_type == "save": total_saved += 1
                elif result_type == "update": total_updated += 1
                time.sleep(0.2)

        print(f"\n\n===== 전체 처리 완료 ====="); print(f"신규 저장: {total_saved}건"); print(f"정보 업데이트: {total_updated}건")
    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")
    finally:
        if connection and connection.is_connected(): cursor.close(); connection.close(); print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()