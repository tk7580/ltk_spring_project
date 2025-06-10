import os
import requests
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

def main():
    # .env 파일에서 환경 변수 로드
    load_dotenv()

    # TMDB API 키 로드
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("에러: TMDB API 키를 .env 파일에 설정해주세요.")
        return

    # DB 접속 정보 로드
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_database = os.getenv('DB_DATABASE')
    db_port = 3306 # MySQL 기본 포트. 필요시 .env 파일에 추가하여 관리 가능

    if not all([db_host, db_user, db_password, db_database]):
        print("에러: DB 접속 정보를 .env 파일에 모두 설정해주세요.")
        return

    # 1. API에서 데이터 가져오기 (이 부분은 이전과 동일)
    query = "인터스텔라"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&language=ko-KR"
    print(f"API 요청 URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 에러 발생: {e}")
        return
    except json.JSONDecodeError:
        print("API 응답 파싱 실패. 응답 내용:", response.text)
        return

    if not data.get('results'):
        print(f"'{query}'에 대한 검색 결과가 없습니다.")
        return

    first_movie = data['results'][0]
    print("\n--- API에서 가져온 영화 정보 ---")
    print(f"제목: {first_movie.get('title')}")

    # 2. 데이터베이스에 연결 및 데이터 저장
    connection = None # connection 변수를 try 블록 전에 초기화
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port, # 포트 번호 명시적으로 전달
            user=db_user,
            password=db_password,
            database=db_database
        )

        if connection.is_connected():
            print("\n데이터베이스에 성공적으로 연결되었습니다.")
            cursor = connection.cursor()

            series_id_for_work = 1 # 임시로 1번 시리즈에 속한다고 가정

            work_data = (
                series_id_for_work,
                first_movie.get('title'),
                first_movie.get('original_title'),
                'Movie',
                first_movie.get('release_date') or None,
                first_movie.get('overview'),
                f"https://image.tmdb.org/t/p/w500{first_movie.get('poster_path')}" if first_movie.get('poster_path') else None
            )

            insert_query_simple = """
            INSERT INTO work (
                seriesId, titleKr, titleOriginal, type, releaseDate,
                description, thumbnailUrl, regDate, updateDate
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """

            cursor.execute(insert_query_simple, work_data)
            connection.commit()

            print(f"\n성공: '{work_data[1]}' 작품 정보가 work 테이블에 저장되었습니다.")
            print(f"저장된 레코드의 ID: {cursor.lastrowid}")

    except Error as e:
        print(f"데이터베이스 작업 중 에러 발생: {e}")

    finally:
        # DB 연결 종료 (connection 변수가 생성되었는지 확인 후 닫음)
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()