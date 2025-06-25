# data_reconciler.py (재사용 가능한 모듈로 리팩토링된 최종본)

import os
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# --- 환경 변수 및 API 설정 (스크립트 로드 시 1회 실행) ---
load_dotenv()
API_URL = 'https://graphql.anilist.co'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Helper Functions ---
def get_db_connection():
    # ... (이전과 동일)
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

def fetch_anime_by_id(anime_id):
    # ... (이전과 동일)
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        id
        title { romaji english native }
        format
        episodes
        duration
        studios(isMain: true) { nodes { name } }
        description(asHtml: false)
        startDate { year }
        status
      }
    }
    '''
    variables = {'id': anime_id}
    response = requests.post(API_URL, json={'query': query, 'variables': variables})
    response.raise_for_status()
    return response.json()['data']['Media']

def find_candidates_in_db(connection, titles):
    # ... (이전과 동일)
    candidates = []
    cursor = connection.cursor(dictionary=True)
    search_terms = [f"%{title}%" for title in titles if title]
    if not search_terms:
        return []
    query_conditions_list = ["(titleKr LIKE %s OR titleOriginal LIKE %s)"] * len(search_terms)
    query_conditions = " OR ".join(query_conditions_list)
    query = f"SELECT id, titleKr, titleOriginal, type, releaseDate FROM work WHERE {query_conditions}"
    params = [term for term in search_terms for _ in (0, 1)]
    cursor.execute(query, params)
    for row in cursor.fetchall():
        candidates.append(row)
    cursor.close()
    return candidates

def ask_gemini_for_judgment(anilist_data, db_candidate):
    # ... (이전과 동일)
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
    response = model.generate_content(prompt)
    return response.text.strip()

# ==========================================================
#           ★★★ 핵심 로직을 담은 메인 함수 ★★★
# ==========================================================
def reconcile_and_update_work(anilist_id):
    """
    AniList ID 하나를 받아, 데이터 정제 및 DB 업데이트까지의 전 과정을 처리하는 함수.
    """
    print(f"\n{'='*20} [ AniList ID: {anilist_id} ] 처리 시작 {'='*20}")

    if not GEMINI_API_KEY:
        print("오류: .env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")
        return

    connection = get_db_connection()
    if not connection:
        return

    cursor = connection.cursor()

    try:
        # 1. AniList 정보 조회
        anilist_data = fetch_anime_by_id(anilist_id)
        print(f"✅ AniList 정보 로드 완료: {anilist_data['title']['english']}")

        # 2. DB에서 후보 검색
        all_titles_from_anilist = [
            anilist_data['title']['english'],
            anilist_data['title']['romaji'],
            anilist_data['title']['native']
        ]
        candidates = find_candidates_in_db(connection, all_titles_from_anilist)
        print(f"✅ 로컬 DB에서 {len(candidates)}개의 후보 작품 검색 완료")

        # 3. Gemini 판단 및 DB 처리
        if not candidates:
            print("-> DB에 일치 후보 없음. 신규 작품으로 처리합니다. (향후 구현)")
            # TODO: 신규 작품으로 DB에 INSERT하는 로직 추가
        else:
            # 여기서는 첫 번째 후보만 처리 (간략화를 위해)
            candidate = candidates[0]
            work_id = candidate['id']
            print(f"-> 후보 '{candidate['titleKr']}' (workId: {work_id}) 와 비교 시작")

            judgment = ask_gemini_for_judgment(anilist_data, candidate)
            print(f"--- Gemini의 최종 판단: {judgment} ---")

            if judgment == 'SAME':
                print(f"-> 동일 작품으로 판단. workId '{work_id}'의 데이터를 보강합니다.")

                # AniList 데이터로 work 테이블 업데이트 (데이터 보강)
                update_query = """
                UPDATE work SET
                    type = %s,
                    description = %s,
                    episodes = %s,
                    duration = %s,
                    studios = %s,
                    isCompleted = %s,
                    updateDate = NOW()
                WHERE id = %s
                """
                studios_str = ", ".join(node['name'] for node in anilist_data.get('studios', {}).get('nodes', []))
                is_completed = 1 if anilist_data.get('status') == 'FINISHED' else 0

                params = (
                    'Animation',
                    anilist_data.get('description'),
                    anilist_data.get('episodes'),
                    anilist_data.get('duration'),
                    studios_str,
                    is_completed,
                    work_id
                )
                cursor.execute(update_query, params)

                # work_identifier에 AniList ID 기록
                insert_identifier_query = """
                INSERT INTO work_identifier (workId, sourceName, sourceId, regDate, updateDate)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON DUPLICATE KEY UPDATE updateDate = NOW()
                """
                cursor.execute(insert_identifier_query, (work_id, 'ANILIST_ANIME', str(anilist_id)))

                connection.commit()
                print("-> DB 데이터 보강 및 업데이트 성공!")

            else: # DIFFERENT 또는 UNCERTAIN
                print("-> 다른 작품 또는 판단 불확실. DB 변경 없음.")

    except Exception as e:
        print(f"오류 발생: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("DB 연결이 종료되었습니다.")
    print(f"{'='*25} [ 처리 완료 ] {'='*25}")

# --- 이 파일을 직접 실행했을 때 테스트용으로 사용할 코드 ---
if __name__ == "__main__":
    # 이 파일 자체를 테스트하기 위해 특정 ID로 함수를 호출
    test_id = 16498 # 진격의 거인
    reconcile_and_update_work(test_id)