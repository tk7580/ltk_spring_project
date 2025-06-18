import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import time

def find_work_by_external_id(cursor, source_name, source_id):
    """
    외부 ID로 work_identifier 테이블에서 기존 작품의 workId(PK)를 조회하는 함수
    :param cursor: DB 커서 객체
    :param source_name: 데이터 출처 (예: 'TMDB_MOVIE')
    :param source_id: 해당 출처에서의 고유 ID
    :return: 우리 DB의 work.id (존재하지 않으면 None)
    """
    query = "SELECT workId FROM work_identifier WHERE sourceName = %s AND sourceId = %s LIMIT 1"
    try:
        # source_id는 문자열일 수 있으므로 str()로 변환하여 안전하게 처리
        cursor.execute(query, (source_name, str(source_id)))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"  [오류] 외부 ID로 작품 조회 중 DB 에러 발생: {e}")
        return None

def update_work_in_db(cursor, connection, work_id, movie_data):
    """
    기존에 있던 작품 정보를 최신 정보로 업데이트하는 함수
    """
    try:
        # 시리즈 정보는 복잡하므로 일단 업데이트에서 제외하고, 작품 정보만 업데이트
        work_data = (
            movie_data.get('title'),
            movie_data.get('original_title'),
            movie_data.get('release_date') or None,
            movie_data.get('overview'),
            f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None,
            work_id # WHERE 절에 들어갈 ID
        )
        update_work_query = """
        UPDATE work SET
            titleKr = %s,
            titleOriginal = %s,
            releaseDate = %s,
            description = %s,
            thumbnailUrl = %s,
            updateDate = NOW()
        WHERE id = %s
        """
        cursor.execute(update_work_query, work_data)
        connection.commit()
        print(f"  [업데이트] '{movie_data.get('title')}' (workId: {work_id}) -> 정보 업데이트 완료")
        print("-" * 40)
        return True
    except Error as e:
        print(f"  [실패] 업데이트 중 오류 발생: {e}")
        connection.rollback()
        print("-" * 40)
        return False

def save_new_work(cursor, connection, movie_data):
    """
    새로운 영화 데이터를 series, work, work_identifier 테이블에 저장하는 함수
    """
    try:
        # 1. Series 테이블 저장
        # TODO: 향후 TMDB의 'belongs_to_collection' 정보를 활용하여 시리즈를 그룹화하는 로직 개선 필요
        series_data = (
            movie_data.get('title'),
            movie_data.get('original_title'),
            movie_data.get('overview'),
            f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None
        )
        insert_series_query = "INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, regDate, updateDate) VALUES (%s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_series_query, series_data)
        series_id = cursor.lastrowid
        print(f"  [1/3] '{series_data[0]}' -> series 저장 완료 (seriesId: {series_id})")

        # 2. Work 테이블 저장
        work_data = (
            series_id,
            movie_data.get('title'),
            movie_data.get('original_title'),
            'Movie',
            movie_data.get('release_date') or None,
            movie_data.get('overview'),
            f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None
        )
        insert_work_query = "INSERT INTO work (seriesId, titleKr, titleOriginal, type, releaseDate, description, thumbnailUrl, regDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_work_query, work_data)
        work_id = cursor.lastrowid
        print(f"  [2/3] '{work_data[1]}' -> work 저장 완료 (workId: {work_id})")

        # 3. Work Identifier 테이블에 매핑 정보 저장
        identifier_data = (work_id, 'TMDB_MOVIE', str(movie_data.get('id')))
        insert_identifier_query = "INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate) VALUES (%s, %s, %s, NOW(), NOW())"
        cursor.execute(insert_identifier_query, identifier_data)
        print(f"  [3/3] workId {work_id}와 TMDB ID {identifier_data[2]} 매핑 정보 저장 완료")

        connection.commit()
        print("-" * 40)
        return True

    except Error as e:
        print(f"  [실패] 신규 저장 중 오류 발생: {e}")
        connection.rollback()
        print("-" * 40)
        return False

def main():
    # .env 파일에서 환경 변수 로드
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_database = os.getenv('DB_DATABASE')

    if not api_key or not all([db_host, db_user, db_password, db_database]):
        print("에러: .env 파일에 TMDB_API_KEY와 DB 접속 정보(HOST, USER, PASSWORD, DATABASE)를 모두 설정해주세요.")
        return

    # TMDB API 요청
    page_to_fetch = 1
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ko-KR&page={page_to_fetch}"
    print(f"API 요청 URL: {url}\n")
    try:
        response = requests.get(url)
        response.raise_for_status()
        movies = response.json().get('results', [])
    except Exception as e:
        print(f"API 요청/파싱 오류: {e}")
        return

    if not movies:
        print("API에서 가져올 영화 목록이 없습니다.")
        return

    print(f"총 {len(movies)}개의 영화 데이터를 가져왔습니다. 데이터베이스 처리를 시작합니다...")

    connection = None
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect( host=db_host, user=db_user, password=db_password, database=db_database, port=3306 )
        cursor = connection.cursor()
        print("데이터베이스에 성공적으로 연결되었습니다.\n")

        saved_count = 0
        updated_count = 0

        print(f"총 {len(movies)}개의 영화 데이터 처리를 시도합니다.")
        print("=" * 40)

        # 각 영화 데이터를 순회하며 처리
        for movie in movies:
            tmdb_id = movie.get('id')
            if not tmdb_id:
                print("  [경고] TMDB ID가 없는 데이터가 있어 건너뜁니다.")
                continue

            # TMDB ID를 기준으로 우리 DB에 작품이 이미 있는지 확인
            existing_work_id = find_work_by_external_id(cursor, 'TMDB_MOVIE', tmdb_id)

            if existing_work_id:
                # 이미 존재하면 업데이트
                if update_work_in_db(cursor, connection, existing_work_id, movie):
                    updated_count += 1
            else:
                # 존재하지 않으면 새로 저장
                if save_new_work(cursor, connection, movie):
                    saved_count += 1

            time.sleep(0.1) # API 서버 부하 방지를 위한 딜레이

        print(f"\n처리 완료: 신규 저장 {saved_count}건, 정보 업데이트 {updated_count}건")

    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")
    finally:
        # 연결 종료
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()