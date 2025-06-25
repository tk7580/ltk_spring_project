# anilist_collector.py

import requests
import json

# AniList GraphQL API 엔드포인트 URL
API_URL = 'https://graphql.anilist.co'

def fetch_anime_by_id(anime_id):
    """
    AniList ID로 특정 애니메이션의 정보를 가져옵니다.
    """
    # GraphQL 쿼리 정의:
    # 필요한 정보들(id, 제목, 타입, 포맷, 에피소드 수 등)을 명시합니다.
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        id
        title {
          romaji
          english
          native
        }
        type
        format
        status
        description(asHtml: false)
        startDate {
          year
          month
          day
        }
        episodes
        duration
        genres
        averageScore
        studios(isMain: true) {
          nodes {
            name
          }
        }
      }
    }
    '''

    # 쿼리에 전달할 변수 (애니메이션 ID)
    variables = {
        'id': anime_id
    }

    print(f"AniList에서 ID '{anime_id}' 작품 정보 조회 중...")

    try:
        # API에 POST 요청 전송
        response = requests.post(API_URL, json={'query': query, 'variables': variables})

        # 요청 성공 여부 확인
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류가 발생했습니다: {e}")
        return None
    except json.JSONDecodeError:
        print(f"API 응답을 JSON으로 파싱하는 데 실패했습니다.")
        return None


if __name__ == '__main__':
    # 테스트를 위해 유명 애니메이션 '카우보이 비밥' (AniList ID: 1)의 정보를 가져옵니다.
    test_anime_id = 1
    anime_data = fetch_anime_by_id(test_anime_id)

    if anime_data:
        print("\n--- AniList API 응답 결과 ---")
        # indent=2 옵션으로 JSON을 예쁘게 출력
        print(json.dumps(anime_data, indent=2, ensure_ascii=False))
        print("---------------------------\n")
        print("AniList API 연동 테스트 성공!")