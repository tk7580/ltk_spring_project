# type_fixer.py (LLM을 이용한 기존 데이터 타입 교정 스크립트)

import os
import time
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error

# --- 환경 변수 및 API 설정 ---
load_dotenv(find_dotenv())
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

# --- DB Helper Functions ---
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

def get_candidates_for_type_fix(cursor, limit=20):
    """ 'Animation' 타입이 아닌 작품 목록을 가져옵니다. """
    print(f"DB에서 'Animation'이 아닌 작품을 {limit}개 가져옵니다...")
    # titleKr, description이 비어있지 않은 것을 대상으로 함
    query = """
    SELECT id, titleKr, description, type FROM work 
    WHERE type != 'Animation' AND titleKr IS NOT NULL AND description IS NOT NULL
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def ask_gemini_for_type(work_data):
    """ Gemini에게 작품의 가장 적절한 타입을 물어봅니다. """
    if not GEMINI_API_KEY:
        print("오류: Gemini API 키가 설정되지 않았습니다.")
        return None

    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Gemini에게 전달할 프롬프트
    prompt = f"""
    당신은 미디어 분류 전문가입니다.
    아래 작품 정보(제목, 줄거리)를 보고, 이 작품의 가장 핵심적인 타입이 'Movie', 'TV', 'Animation' 중 무엇인지 판단해주세요.
    반드시 'Movie', 'TV', 'Animation' 셋 중 하나의 단어로만 답변해주세요.

    - 제목: {work_data['titleKr']}
    - 줄거리: {work_data['description'][:400]}

    가장 적합한 타입:
    """

    try:
        response = model.generate_content(prompt)
        # 답변에서 불필요한 문자나 공백을 제거하고 반환
        return response.text.strip().replace("'", "").replace('"', '')
    except Exception as e:
        print(f"Gemini API 호출 중 오류 발생: {e}")
        return None

def main():
    print("=== 기존 데이터 타입 교정 스크립트 시작 ===")
    connection = get_db_connection()
    if not connection: return

    cursor = connection.cursor(dictionary=True)

    # 1. 타입 교정이 필요한 후보 작품들을 가져옴
    candidates = get_candidates_for_type_fix(cursor, limit=20)

    if not candidates:
        print("타입을 교정할 후보 작품이 없습니다.")
        cursor.close()
        connection.close()
        return

    print(f"총 {len(candidates)}개의 작품에 대해 타입 교정을 시도합니다.")
    updated_count = 0

    try:
        # 2. 각 후보 작품에 대해 처리
        for work in candidates:
            print(f"\n--- [ID: {work['id']}] '{work['titleKr']}' (현재 타입: {work['type']}) 처리 중 ---")

            # 3. Gemini에게 올바른 타입 물어보기
            gemini_type = ask_gemini_for_type(work)
            print(f"  -> Gemini 판단: '{gemini_type}'")

            # 4. Gemini의 답변이 'Animation'이고, 현재 타입이 'Animation'이 아닐 경우 DB 업데이트
            if gemini_type == 'Animation' and work['type'] != 'Animation':
                update_query = "UPDATE work SET type = 'Animation', updateDate = NOW() WHERE id = %s"
                cursor.execute(update_query, (work['id'],))
                print(f"  [성공] ID '{work['id']}'의 타입을 'Animation'으로 변경했습니다.")
                updated_count += 1
            else:
                print("  [유지] 타입 변경 없음.")

            print("  (API 요청 제한을 위해 2초 대기...)")
            time.sleep(2)

        # 5. 모든 변경사항을 DB에 최종 저장
        if updated_count > 0:
            connection.commit()
            print(f"\n총 {updated_count}개의 작품 타입이 성공적으로 교정되었습니다.")
        else:
            print("\n타입이 변경된 작품이 없습니다.")

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