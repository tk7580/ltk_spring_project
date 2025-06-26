# llm_enricher.py (JSON 통합 요청 방식으로 일관성 및 효율성 극대화)

import os
import time
import json
import argparse
import re
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error
import requests

# --- 환경 변수 및 API 설정 ---
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

def clean_html_tags(text):
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def call_gemini_api_for_json(prompt):
    if not GEMINI_API_KEY: return None
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    for i in range(3):
        try:
            response = model.generate_content(prompt)
            time.sleep(1.5) # API Rate Limit 준수
            # Gemini 응답에서 JSON 부분만 안정적으로 추출
            json_text = response.text.strip()
            match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if match:
                return json.loads(match.group())
            else:
                print(f"  [경고] Gemini가 유효한 JSON을 반환하지 못했습니다. (응답: {json_text}) 재시도... ({i+1}/3)")
                continue
        except json.JSONDecodeError as e:
            print(f"  [경고] JSON 파싱 오류: {e}. (응답: {response.text}) 재시도... ({i+1}/3)")
            continue
        except Exception as e:
            if "429" in str(e):
                delay = (i + 1) * 5
                print(f"  [경고] Gemini API 요청 횟수 제한. {delay}초 후 재시도... ({i+1}/3)")
                time.sleep(delay)
            else:
                print(f"  [오류] Gemini API 호출 중 오류 발생: {e}")
                return None
    return None

def update_work_in_db(cursor, work_id, fields_to_update):
    if not fields_to_update:
        return False
    update_clauses = [f"{key} = %s" for key in fields_to_update.keys()]
    params = list(fields_to_update.values())
    params.append(work_id)
    update_query = f"UPDATE work SET {', '.join(update_clauses)}, updateDate = NOW() WHERE id = %s"
    try:
        cursor.execute(update_query, tuple(params))
        return True
    except Error as e:
        print(f"  [오류] DB 업데이트 중 오류 발생: {e}")
        return False

# ★★★★★ 이 함수를 통째로 교체 ★★★★★
def get_unified_enrichment_data(work_info):
    """
    하나의 프롬프트로 제목, 줄거리, 썸네일을 한번에 JSON으로 요청하는 함수
    """
    title_to_search = work_info.get('titleOriginal') or work_info.get('titleKr')

    prompt = f"""
    당신은 한국 미디어 서비스의 데이터를 보강하는 전문가입니다.
    '{title_to_search}' 작품에 대한 아래 3가지 정보를 찾아 하나의 JSON 객체로 만들어주세요.

    [조사 기준]
    - 반드시 한국의 '공식' 스트리밍 서비스(넷플릭스, 라프텔, 왓챠 등)나 '공식' 출판사 사이트, 또는 나무위키의 정보를 최우선으로 참고해야 합니다.

    [요청 데이터]
    1.  "korean_title": 시즌 정보까지 포함한, 한국의 공식 명칭.
    2.  "poster_url": 위 사이트들에서 사용하는 고화질 포스터 이미지의 직접 주소(URL). 없으면 null.
    3.  "korean_plot": 위 사이트들의 공식 시놉시스를 바탕으로 한, 스포일러 없는 200자 내외의 한국어 줄거리. 없으면 null.

    [출력 형식]
    - 설명은 일절 금지하며, 아래와 같은 유효한 JSON 형식으로만 응답해주세요.
    {{
      "korean_title": "...",
      "poster_url": "...",
      "korean_plot": "..."
    }}
    """

    return call_gemini_api_for_json(prompt)

def main():
    parser = argparse.ArgumentParser(description="모든 작품을 대상으로 JSON 통합 요청을 통해 데이터를 일관성 있게 보강합니다.")
    parser.add_argument('--limit', type=int, default=500, help="한 번에 처리할 작품의 최대 개수")
    parser.add_argument('--offset', type=int, default=0, help="처리를 시작할 위치(offset)")
    args = parser.parse_args()

    print("=== JSON 통합 데이터 보강 스크립트 시작 ===")
    connection = get_db_connection()
    if not connection: return

    cursor = connection.cursor(dictionary=True)
    query = f"""
    SELECT w.id, w.titleKr, w.titleOriginal, w.description, w.thumbnailUrl
    FROM work w
    ORDER BY w.id ASC
    LIMIT {args.limit} OFFSET {args.offset}
    """
    cursor.execute(query)
    candidates = cursor.fetchall()

    if not candidates:
        print("해당 범위에 작품이 없습니다."); cursor.close(); connection.close(); return

    print(f"총 {len(candidates)}개의 작품에 대해 데이터 보강을 시도합니다. (시작 위치: {args.offset})")
    total_updated_count = 0
    try:
        for work in candidates:
            print(f"\n--- [ID: {work['id']}] '{work['titleKr']}' 처리 시작 ---")

            enriched_data = get_unified_enrichment_data(work)

            if not enriched_data:
                print("  -> 유효한 보강 정보를 얻지 못했습니다.")
                continue

            updates_needed = {}

            # 1. 제목 업데이트 확인
            new_title = enriched_data.get('korean_title')
            if new_title and work.get('titleKr') != new_title:
                updates_needed['titleKr'] = new_title

            # 2. 줄거리 업데이트 확인
            new_plot = enriched_data.get('korean_plot')
            if new_plot:
                cleaned_plot = clean_html_tags(new_plot)
                if work.get('description') != cleaned_plot:
                    updates_needed['description'] = cleaned_plot

            # 3. 썸네일 업데이트 확인
            new_thumbnail = enriched_data.get('poster_url')
            if new_thumbnail and work.get('thumbnailUrl') != new_thumbnail:
                updates_needed['thumbnailUrl'] = new_thumbnail

            if updates_needed:
                if update_work_in_db(cursor, work['id'], updates_needed):
                    print(f"  -> DB에 [{', '.join(updates_needed.keys())}] 정보 반영 완료.")
                    connection.commit()
                    total_updated_count += 1
            else:
                print("  -> 변경할 데이터 없음.")

        if total_updated_count > 0:
            print(f"\n총 {total_updated_count}건의 작품 정보가 수정/보강되었습니다.")
        else:
            print("\n새롭게 수정/보강된 정보가 없습니다.")

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