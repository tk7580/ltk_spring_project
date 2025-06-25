# data_reconciler.py (전체 수정본)

import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# --- 환경 변수 및 API 설정 ---
load_dotenv()
API_URL = 'https://graphql.anilist.co'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- 데이터베이스 연결 함수 (누락되었던 함수) ---
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE'),
            port=3306
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"DB 연결 오류: {e}")
        return None

# --- AniList 데이터 조회 함수 ---
def fetch_anime_by_id(anime_id):
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        id
        title { romaji english native }
        format
        episodes
        startDate { year }
      }
    }
    '''
    variables = {'id': anime_id}
    response = requests.post(API_URL, json={'query': query, 'variables': variables})
    response.raise_for_status()
    return response.json()['data']['Media']

# --- 로컬 DB에서 후보 검색 함수 (개선된 버전) ---
def find_candidates_in_db(connection, titles):
    candidates = []
    cursor = connection.cursor(dictionary=True)
    search_terms = [f"%{title}%" for title in titles if title]
    if not search_terms:
        return []

    # 각 제목에 대해 OR 조건으로 쿼리를 동적으로 생성
    # titleKr과 titleOriginal 두 컬럼에 대해 검색
    query_conditions_list = ["(titleKr LIKE %s OR titleOriginal LIKE %s)"] * len(search_terms)
    query_conditions = " OR ".join(query_conditions_list)
    query = f"SELECT id, titleKr, titleOriginal, type, releaseDate FROM work WHERE {query_conditions}"

    # 파라미터 리스트 생성 (예: [t1, t1, t2, t2])
    params = [term for term in search_terms for _ in (0, 1)]

    cursor.execute(query, params)

    for row in cursor.fetchall():
        candidates.append(row)
    cursor.close()
    return candidates

# --- Gemini에게 동일 작품 여부 판단 요청 함수 ---
def ask_gemini_for_judgment(anilist_data, db_candidate):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    당신은 작품 데이터베이스 관리 전문가입니다.
    아래 두 작품이 동일한 작품인지 판단해주세요. 제목이 비슷하더라도 시즌이 다르거나, 리메이크, 스핀오프인 경우는 다른 작품입니다.
    반드시 'SAME', 'DIFFERENT', 'UNCERTAIN' 셋 중 하나로만 답변해주세요.

    [작품 1: AniList 정보]
    - 제목(영문): {anilist_data['title']['english']}
    - 제목(로마지): {anilist_data['title']['romaji']}
    - 제목(원어): {anilist_data['title']['native']}
    - 포맷: {anilist_data['format']}
    - 방영 시작 연도: {anilist_data['startDate']['year']}

    [작품 2: 기존 DB 정보]
    - 제목(한글): {db_candidate['titleKr']}
    - 제목(원제): {db_candidate['titleOriginal']}
    - 타입: {db_candidate['type']}
    - 출시일: {db_candidate['releaseDate']}

    판단 결과:
    """
    print("\n--- Gemini에게 판단 요청 ---")
    # print(prompt) # 프롬프트가 너무 길어지므로 일단 주석 처리
    response = model.generate_content(prompt)
    return response.text.strip()


def main():
    if not GEMINI_API_KEY:
        print("오류: .env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")
        return

    test_anilist_id = 16498
    connection = get_db_connection()
    if not connection:
        return

    try:
        anilist_data = fetch_anime_by_id(test_anilist_id)
        print(f"✅ AniList 정보 로드 완료: {anilist_data['title']['english']}")

        all_titles_from_anilist = [
            anilist_data['title']['english'],
            anilist_data['title']['romaji'],
            anilist_data['title']['native'] # 원어 제목도 검색에 추가
        ]
        candidates = find_candidates_in_db(connection, all_titles_from_anilist)
        print(f"✅ 로컬 DB에서 {len(candidates)}개의 후보 작품 검색 완료")

        if not candidates:
            print("\n결과: DB에 비슷한 작품이 없어, 신규 데이터로 처리해야 합니다.")
            return

        for candidate in candidates:
            print(f"\n===== 후보 '{candidate['titleKr']}' (workId: {candidate['id']}) 와 비교 시작 =====")
            judgment = ask_gemini_for_judgment(anilist_data, candidate)
            print("\n--- Gemini의 최종 판단 ---")
            print(f"'{anilist_data['title']['english']}' vs '{candidate['titleKr']}' => {judgment}")
            print("==========================================================")

    finally:
        if connection.is_connected():
            connection.close()
            print("\nDB 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()