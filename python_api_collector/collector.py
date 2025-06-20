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
    # 기존 연결은 모두 삭제 후 새로 추가하여 최신 상태를 유지합니다.
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
            return creators[0].get('name')
    return None

def normalize_item_data(item, media_type, creator_name):
    """Movie와 TV API의 다른 필드명을 공통 형식으로 정규화합니다."""
    base_data = {
        'id': item.get('id'),
        'description': item.get('overview'),
        'thumbnailUrl': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
        'coverImageUrl': f"https://image.tmdb.org/t/p/w1280{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
        'genres': [genre['name'] for genre in item.get('genres', [])],
        'author': creator_name
    }
    if media_type == 'movie':
        base_data.update({
            'titleKr': item.get('title'),
            'titleOriginal': item.get('original_title'),
            'releaseDate': item.get('release_date'),
            'type': 'Movie',
            'isCompleted': True # 영화는 항상 '완결'로 간주
        })
    elif media_type == 'tv':
        base_data.update({
            'titleKr': item.get('name'),
            'titleOriginal': item.get('original_name'),
            'releaseDate': item.get('first_air_date'),
            'type': 'TV',
            'isCompleted': item.get('status') == 'Ended'
        })
    return base_data

# ===== Main DB Operation Functions =====

def process_item(cursor, connection, item, media_type, api_key):
    """하나의 아이템(영화/TV)을 가져와 DB에 저장 또는 업데이트합니다."""
    source_name = f"TMDB_{media_type.upper()}"
    tmdb_id = item.get('id')
    if not tmdb_id:
        print("  [경고] TMDB ID가 없는 데이터는 건너뜁니다.")
        return None, None

    # 상세 정보 API를 호출하여 장르, 커버 이미지 등 추가 정보 획득
    detail_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={api_key}&language=ko-KR"
    detail_data = get_api_data(detail_url)
    if not detail_data:
        return None, None

    creator_name = get_creator_info(media_type, tmdb_id, api_key)
    normalized_data = normalize_item_data(detail_data, media_type, creator_name)

    existing_work_id = find_work_by_external_id(cursor, source_name, tmdb_id)

    print("-" * 40)

    if existing_work_id:
        # 업데이트 로직 (work, series 테이블)
        cursor.execute("UPDATE work SET titleKr=%s, titleOriginal=%s, releaseDate=%s, description=%s, thumbnailUrl=%s, isCompleted=%s, updateDate=NOW() WHERE id=%s",
                       (normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['isCompleted'], existing_work_id))
        cursor.execute("SELECT seriesId FROM work WHERE id = %s", (existing_work_id,))
        series_id = cursor.fetchone()[0]
        cursor.execute("UPDATE series SET author=%s, coverImageUrl=%s, updateDate=NOW() WHERE id=%s",
                       (normalized_data['author'], normalized_data['coverImageUrl'], series_id))
        print(f"  [업데이트] '{normalized_data.get('titleKr')}' (workId: {existing_work_id}) -> 정보 업데이트 완료")
        work_id = existing_work_id
    else:
        # 신규 저장 로직 (series, work, work_identifier 테이블)
        cursor.execute("INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, coverImageUrl, author, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())",
                       (normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['coverImageUrl'], normalized_data['author']))
        series_id = cursor.lastrowid
        print(f"  [신규 저장 1/3] '{normalized_data['titleKr']}' -> series 저장 완료")

        cursor.execute("INSERT INTO work (seriesId, titleKr, titleOriginal, type, releaseDate, description, thumbnailUrl, isCompleted, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
                       (series_id, normalized_data['titleKr'], normalized_data['titleOriginal'], normalized_data['type'], normalized_data.get('releaseDate') or None, normalized_data['description'], normalized_data['thumbnailUrl'], normalized_data['isCompleted']))
        work_id = cursor.lastrowid
        print(f"  [신규 저장 2/3] '{normalized_data['titleKr']}' -> work 저장 완료 (workId: {work_id})")

        cursor.execute("INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())",
                       (work_id, source_name, str(tmdb_id)))
        print(f"  [신규 저장 3/3] workId {work_id}와 {source_name} ID {tmdb_id} 매핑 완료")

    # 장르 처리 로직
    genre_names = normalized_data.get('genres', [])
    if genre_names:
        genre_ids = get_or_create_genre_ids(cursor, connection, genre_names)
        link_genres_to_work(cursor, connection, work_id, genre_ids)
        print(f"    - '{normalized_data.get('titleKr')}' -> 장르 정보 {len(genre_ids)}건 처리 완료")

    connection.commit()
    return "update" if existing_work_id else "save"

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
        connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_database, port=3306)
        cursor = connection.cursor()
        print("데이터베이스에 성공적으로 연결되었습니다.")

        media_types_to_process = ['movie', 'tv']
        total_saved = 0
        total_updated = 0

        for media_type in media_types_to_process:
            page = 1 # 각 타입별로 1페이지씩만 가져옵니다.
            list_url = f"https://api.themoviedb.org/3/{media_type}/popular?api_key={api_key}&language=ko-KR&page={page}"

            print(f"\n===== '{media_type.upper()}' 데이터 처리 시작 (페이지: {page}) =====")
            popular_list = get_api_data(list_url)

            if not popular_list or not popular_list.get('results'):
                print(f"  [정보] '{media_type.upper()}' 타입의 인기 목록을 가져올 수 없습니다.")
                continue

            for item_summary in popular_list['results']:
                result_type, _ = process_item(cursor, connection, item_summary, media_type, api_key)
                if result_type == "save":
                    total_saved += 1
                elif result_type == "update":
                    total_updated += 1
                time.sleep(0.2) # 상세 정보 및 크레딧 API 호출로 인한 부하 방지 딜레이

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