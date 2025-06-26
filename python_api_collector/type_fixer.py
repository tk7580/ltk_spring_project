# type_fixer.py (명령줄 인수 기능 추가)

import os
import time
import json
import argparse # ★★★ argparse 라이브러리 임포트 ★★★
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

def get_candidates_for_drama_fix(cursor, limit):
    print(f"DB에서 'Drama' 타입이 아닌 작품을 {limit}개 가져옵니다...")
    query = """
    SELECT w.id, w.titleKr, w.description FROM work w
    LEFT JOIN work_type_mapping wtm ON w.id = wtm.workId
    LEFT JOIN work_type wt ON wtm.typeId = wt.id AND wt.name = 'Drama'
    WHERE wt.id IS NULL
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def ask_gemini_is_drama(work_data):
    if not GEMINI_API_KEY:
        print("오류: Gemini API 키가 설정되지 않았습니다.")
        return None
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    당신은 미디어 분류 전문가입니다. 작품의 줄거리를 보고, 이 작품이 '아케인'이나 '왕좌의 게임'처럼 인물들의 관계와 서사가 중심이 되는 본격 '드라마'에 가까운지 판단해주세요.
    단순 액션, 모험, 코미디가 주가 되는 작품은 '드라마'가 아닙니다.
    반드시 'Drama' 또는 'Non-Drama' 둘 중 하나로만 답변해주세요.

    - 제목: {work_data['titleKr']}
    - 줄거리: {work_data['description'][:500]}

    판단:
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API 호출 중 오류 발생: {e}")
        return None

def main():
    # ★★★ [수정] 명령줄 인수 파서 설정 ★★★
    parser = argparse.ArgumentParser(description="LLM을 이용해 작품에 'Drama' 타입을 지능적으로 부여합니다.")
    parser.add_argument('--limit', type=int, default=20, help="한 번에 처리할 작품의 최대 개수")
    args = parser.parse_args()

    print("=== 'Drama' 타입 교정 스크립트 시작 ===")
    connection = get_db_connection()
    if not connection: return

    cursor = connection.cursor(dictionary=True)

    # ★★★ [수정] 하드코딩된 변수 대신 args.limit 사용 ★★★
    candidates = get_candidates_for_drama_fix(cursor, limit=args.limit)

    if not candidates:
        print("타입을 교정할 후보 작품이 없습니다.")
        cursor.close()
        connection.close()
        return

    print(f"총 {len(candidates)}개의 작품에 대해 'Drama' 타입 추가 여부를 검토합니다.")

    cursor.execute("SELECT id FROM work_type WHERE name = 'Drama'")
    result = cursor.fetchone()
    if not result:
        print("오류: work_type 테이블에 'Drama' 타입이 없습니다.")
        return
    drama_type_id = result['id']

    updated_count = 0
    try:
        for work in candidates:
            print(f"\n--- [ID: {work['id']}] '{work['titleKr']}' 처리 중 ---")
            judgment = ask_gemini_is_drama(work)
            print(f"  -> Gemini 판단: '{judgment}'")

            if judgment == 'Drama':
                insert_query = "INSERT IGNORE INTO work_type_mapping (workId, typeId, regDate) VALUES (%s, %s, NOW())"
                cursor.execute(insert_query, (work['id'], drama_type_id))
                if cursor.rowcount > 0:
                    print(f"  [성공] ID '{work['id']}'에 'Drama' 타입을 추가했습니다.")
                    updated_count += 1
                else:
                    print("  [유지] 이미 'Drama' 타입이 있거나 추가에 실패했습니다.")
            else:
                print("  [유지] 타입 변경 없음.")

            print("  (API 요청 제한을 위해 2초 대기...)")
            time.sleep(2)

        if updated_count > 0:
            connection.commit()
            print(f"\n총 {updated_count}개의 작품에 'Drama' 타입이 성공적으로 추가되었습니다.")
        else:
            print("\n'Drama' 타입으로 변경된 작품이 없습니다.")

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