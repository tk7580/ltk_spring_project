# type_fixer.py (Live-Action 작품만 대상으로 수정된 최종본)

import os
import time
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

def get_candidates_for_drama_fix(cursor, limit):
    """ 'Live-Action'이면서 아직 'Drama'가 아닌 작품 목록을 가져옵니다. """
    print(f"DB에서 'Live-Action'이면서 'Drama' 타입이 아닌 작품을 {limit}개 가져옵니다...")
    # ★★★ [수정] 'Live-Action' 타입이 있는 작품만 가져오도록 SQL 변경 ★★★
    query = """
    SELECT w.id, w.titleKr, w.description FROM work w
    -- 이 작품이 Live-Action 타입인지 확인
    JOIN work_type_mapping wtm_live ON w.id = wtm_live.workId
    JOIN work_type wt_live ON wtm_live.typeId = wt_live.id AND wt_live.name = 'Live-Action'
    -- 이 작품에 Drama 타입이 없는지 확인
    LEFT JOIN work_type_mapping wtm_drama ON w.id = wtm_drama.workId AND wtm_drama.typeId = (SELECT id FROM work_type WHERE name = 'Drama')
    WHERE wtm_drama.workId IS NULL
    AND w.description IS NOT NULL AND w.description != ''
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
    for i in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                delay = (i + 1) * 2
                print(f"  [경고] Gemini API 요청 횟수 제한 도달. {delay}초 후 재시도합니다... ({i + 1}/3)")
                time.sleep(delay)
            else:
                print(f"  [오류] Gemini API 호출 중 다른 오류 발생: {e}")
                return None

    print("  [실패] 여러 번의 재시도 후에도 작업에 실패했습니다.")
    return None

def main():
    parser = argparse.ArgumentParser(description="LLM을 이용해 'Live-Action' 작품에 'Drama' 타입을 지능적으로 부여합니다.")
    parser.add_argument('--limit', type=int, default=20, help="한 번에 처리할 작품의 최대 개수")
    args = parser.parse_args()

    print("=== 'Drama' 타입 교정 스크립트 시작 ===")
    connection = get_db_connection()
    if not connection: return

    cursor = connection.cursor(dictionary=True)
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
        cursor.close()
        connection.close()
        return
    drama_type_id = result['id']

    updated_count = 0
    try:
        for work in candidates:
            print(f"\n--- [ID: {work['id']}] '{work['titleKr']}' 처리 중 ---")
            judgment = ask_gemini_is_drama(work)

            if judgment == 'Drama':
                print(f"  -> Gemini 판단: 'Drama' -> 타입 추가")
                insert_query = "INSERT IGNORE INTO work_type_mapping (workId, typeId, regDate) VALUES (%s, %s, NOW())"
                cursor.execute(insert_query, (work['id'], drama_type_id))
                if cursor.rowcount > 0:
                    updated_count += 1
            elif judgment:
                print(f"  -> Gemini 판단: '{judgment}' -> 타입 변경 없음")
            else:
                print("  [실패] Gemini로부터 유효한 정보를 얻지 못했습니다.")

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