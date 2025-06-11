import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import time

def save_work_to_db(cursor, connection, movie_data):
    """
    하나의 영화 데이터를 받아서 series와 work 테이블에 저장하는 함수
    """
    try:
        # 1. Series 테이블에 먼저 데이터를 저장하거나, 이미 있는지 확인합니다.
        # 이 예제에서는 각 영화를 고유한 시리즈로 간주하고 매번 새로 생성합니다.
        # TODO: 실제로는 같은 시리즈(예: '해리포터')는 한번만 저장하도록 로직 개선이 필요합니다.
        series_data = (
            movie_data.get('title'),
            movie_data.get('original_title'),
            movie_data.get('overview'),
            f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None
        )
        insert_series_query = """
        INSERT INTO series (titleKr, titleOriginal, description, thumbnailUrl, regDate, updateDate)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(insert_series_query, series_data)
        # 방금 생성된 series의 id를 가져옵니다.
        series_id = cursor.lastrowid
        print(f"  [1/2] '{series_data[0]}' -> series 테이블 저장 완료 (seriesId: {series_id})")

        # 2. Work 테이블에 저장합니다.
        work_data = (
            series_id, # 위에서 생성된 series의 id를 사용합니다.
            movie_data.get('title'),
            movie_data.get('original_title'),
            'Movie', # API가 영화이므로 'Movie'로 고정합니다.
            movie_data.get('release_date') or None, # 날짜 정보가 없으면 NULL로 저장합니다.
            movie_data.get('overview'),
            f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None
        )
        # work 테이블의 thumbnailUrl 컬럼도 함께 INSERT 합니다.
        insert_work_query = """
        INSERT INTO work (
            seriesId, titleKr, titleOriginal, type, releaseDate,
            description, thumbnailUrl, regDate, updateDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(insert_work_query, work_data)
        work_id = cursor.lastrowid
        print(f"  [2/2] '{work_data[1]}' -> work 테이블 저장 완료 (workId: {work_id})")

        # 모든 작업이 성공했을 때만 최종적으로 DB에 반영합니다.
        connection.commit()
        print("-" * 40)
        return True

    except Error as e:
        # 중간에 오류가 발생하면 모든 변경사항을 되돌립니다.
        print(f"  [실패] 저장 중 오류 발생: {e}")
        connection.rollback()
        print("-" * 40)
        return False

def main():
    """
    메인 실행 함수
    """
    # .env 파일에서 환경 변수를 로드합니다.
    load_dotenv()

    # TMDB API 키를 로드합니다.
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("에러: TMDB API 키를 .env 파일에 설정해주세요.")
        return

    # DB 접속 정보를 로드합니다.
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_database = os.getenv('DB_DATABASE')
    db_port = 3306

    if not all([db_host, db_user, db_password, db_database]):
        print("에러: DB 접속 정보를 .env 파일에 모두 설정해주세요.")
        return

    # 1. TMDB에서 인기 영화 목록을 가져옵니다.
    page_to_fetch = 1 # 1페이지의 인기 영화 목록을 가져옵니다.
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ko-KR&page={page_to_fetch}"
    print(f"API 요청 URL: {url}\n")

    try:
        response = requests.get(url)
        response.raise_for_status() # 요청 실패 시 에러 발생
        data = response.json()
        movies = data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 에러 발생: {e}")
        return
    except json.JSONDecodeError:
        print("API 응답 파싱 실패. 응답 내용:", response.text)
        return

    if not movies:
        print("API에서 가져올 영화 목록이 없습니다.")
        return

    print(f"총 {len(movies)}개의 영화 데이터를 가져왔습니다. 데이터베이스 저장을 시작합니다...")

    # 2. 데이터베이스에 연결합니다.
    connection = None
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_database
        )
        cursor = connection.cursor()
        print("데이터베이스에 성공적으로 연결되었습니다.\n")

        # 3. 각 영화를 순회하며 DB에 저장합니다.
        saved_count = 0
        print(f"총 {len(movies)}개의 영화 데이터 저장을 시도합니다.")
        print("=" * 40)

        for movie in movies:
            # 중복 저장 방지 로직은 현재 생략되어 있습니다.
            if save_work_to_db(cursor, connection, movie):
                saved_count += 1

            # API 서버에 부담을 주지 않기 위해 약간의 딜레이를 둡니다.
            time.sleep(0.1)

        print(f"\n총 {saved_count}개의 새로운 작품 정보가 저장되었습니다.")

    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")
    finally:
        # 모든 작업이 끝나면 DB 연결을 안전하게 종료합니다.
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

# 이 스크립트가 직접 실행될 때만 main() 함수를 호출합니다.
if __name__ == "__main__":
    main()