import os
import time
import json
import argparse
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv(find_dotenv())
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_DATABASE'), port=3306)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"DB 연결 오류: {e}")
        return None

def get_works_to_enrich(cursor, limit):
    """ 한글 제목/썸네일/줄거리가 부실한 작품 목록을 가져옵니다. """
    print(f"DB에서 보강이 필요한 작품을 {limit}개 가져옵니다...")
    query = """
    SELECT id, titleKr, titleOriginal, description, thumbnailUrl FROM work 
    WHERE 
        thumbnailUrl IS NULL 
        OR (titleKr = titleOriginal AND titleOriginal IS NOT NULL)
        OR description IS NULL
        OR description = ''
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def ask_gemini_for_enrichment(title):
    """ Gemini에게 작품의 한국어 제목, 포스터, 줄거리를 물어봅니다. """
    if not GEMINI_API_KEY:
        print("오류: Gemini API 키가 설정되지 않았습니다.")
        return None

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    당신은 미디어 정보 검색 전문가입니다.
    작품의 원제 또는 영문 제목이 '{title}' 입니다.
    이 작품의 정보 3가지를 찾아서, 반드시 아래와 같은 JSON 형식으로만 답변해주세요.

    1.  "korean_title": 이 작품의 한국어 정식 제목. 한국어 제목이 없다면 null 값을 반환해주세요.
    2.  "poster_url": 이 작품을 대표하는 고화질 세로 포스터 이미지의 URL. 없다면 null 값을 반환해주세요.
    3.  "korean_description": 이 작품의 공식 소개글 또는 스포일러가 없는 한국어 줄거리 요약. 없다면 null 값을 반환해주세요.

    JSON 데이터:
    """

    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_str)
    except Exception as e:
        print(f"  [오류] Gemini API 호출 또는 JSON 파싱 중 오류 발생: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="LLM을 이용해 작품의 누락된 정보(한글 제목, 썸네일 등)를 보강합니다.")
    parser.add_argument('--limit', type=int, default=10, help="한 번에 처리할 작품의 최대 개수")
    args = parser.parse_args()

    print("=== LLM 데이터 보강 스크립트 시작 ===")
    connection = get_db_connection()
    if not connection: return

    cursor = connection.cursor(dictionary=True)

    candidates = get_works_to_enrich(cursor, limit=args.limit)

    if not candidates:
        print("데이터 보강이 필요한 작품이 없습니다.")
        cursor.close()
        connection.close()
        return

    print(f"총 {len(candidates)}개의 작품에 대해 데이터 보강을 시도합니다.")
    updated_count = 0

    try:
        for work in candidates:
            work_id = work['id']
            title_to_search = work['titleOriginal'] or work['titleKr']

            print(f"\n--- [ID: {work_id}] '{title_to_search}' 처리 중 ---")

            enriched_data = ask_gemini_for_enrichment(title_to_search)

            if enriched_data:
                update_fields = []
                update_params = []

                new_title = enriched_data.get('korean_title')
                if new_title and work['titleKr'] != new_title:
                    update_fields.append("titleKr = %s")
                    update_params.append(new_title)
                    print(f"   - 한글 제목 보강: '{new_title}'")

                new_thumbnail = enriched_data.get('poster_url')
                if new_thumbnail and work['thumbnailUrl'] != new_thumbnail:
                    update_fields.append("thumbnailUrl = %s")
                    update_params.append(new_thumbnail)
                    print(f"   - 썸네일 보강: URL 발견")

                new_description = enriched_data.get('korean_description')
                if new_description and (not work['description'] or work['description'] != new_description):
                    update_fields.append("description = %s")
                    update_params.append(new_description)
                    print(f"   - 줄거리 보강: 내용 발견")

                if update_fields:
                    update_query = f"UPDATE work SET {', '.join(update_fields)}, updateDate = NOW() WHERE id = %s"
                    update_params.append(work_id)
                    cursor.execute(update_query, tuple(update_params))
                    print(f"  [성공] ID '{work['id']}'의 정보를 업데이트했습니다.")
                    updated_count += 1
                else:
                    print("  [유지] 기존 정보가 최신이거나, Gemini가 유효한 정보를 제공하지 않았습니다.")
            else:
                print("  [실패] Gemini로부터 유효한 정보를 얻지 못했습니다.")

            print("  (API 요청 제한을 위해 2초 대기...)")
            time.sleep(2)

        if updated_count > 0:
            connection.commit()
            print(f"\n총 {updated_count}개의 작품 정보가 성공적으로 보강되었습니다.")
        else:
            print("\n정보가 변경된 작품이 없습니다.")

    except Exception as e:
        print(f"작업 중 오류 발생: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n=== 스크립트 종료 ===")

if __name__ == "__main__":
    main()