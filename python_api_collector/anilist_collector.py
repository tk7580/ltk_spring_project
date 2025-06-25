# anilist_collector.py (여러 작품을 순차적으로 처리하는 감독 스크립트)

import requests
import json
import time
from data_reconciler import reconcile_and_update_work # 우리가 만든 모듈에서 함수 임포트

# AniList GraphQL API 엔드포인트 URL
API_URL = 'https://graphql.anilist.co'

def get_popular_anime_list(page=1, per_page=5):
    """
    AniList에서 인기있는 애니메이션 목록을 가져옵니다.
    (한 번에 너무 많지 않게 per_page로 개수 조절)
    """
    print(f"AniList에서 인기 애니메이션 목록 조회 시작 (페이지: {page}, 개수: {per_page})")

    query = '''
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
        }
        media (type: ANIME, sort: POPULARITY_DESC) {
          id
          title {
            english
            romaji
          }
        }
      }
    }
    '''
    variables = {
        'page': page,
        'perPage': per_page
    }

    try:
        response = requests.post(API_URL, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()['data']['Page']['media']
    except Exception as e:
        print(f"애니메이션 목록을 가져오는 중 오류 발생: {e}")
        return []

def main():
    # 처리할 애니메이션 목록을 가져옴 (테스트를 위해 5개만)
    anime_list = get_popular_anime_list(page=1, per_page=5)

    if not anime_list:
        print("처리할 애니메이션 목록이 없습니다.")
        return

    print(f"\n총 {len(anime_list)}개의 애니메이션에 대한 데이터 정제 및 보강 작업을 시작합니다.")

    # 목록을 순회하며 각 ID에 대해 정제/보강 함수를 호출
    for anime in anime_list:
        anilist_id = anime['id']

        # data_reconciler.py에 있는 핵심 함수를 호출
        reconcile_and_update_work(anilist_id)

        # AniList API에 대한 예의를 지키고, 차단을 피하기 위해 잠시 대기
        print("다음 작업을 위해 2초 대기...")
        time.sleep(2)

    print("\n모든 작업이 완료되었습니다.")


if __name__ == '__main__':
    main()