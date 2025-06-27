#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
series_collector.py
--------------------
AniList API를 이용해 Series(시리즈)와 그에 속한 Work(원작·애니·실사 등)를
한 번에 업서트(upsert)합니다.
"""

import argparse
import requests
import html
from data.models import Series, Work  # 실제 ORM 모델 경로로 수정하세요

ANILIST_API_URL = "https://graphql.anilist.co"

SERIES_QUERY = '''
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME) {
      id
      title {
        romaji
        native
        english
      }
      description(asHtml: false)
      relations {
        edges {
          relationType
          node {
            id
            title { romaji native english }
            description(asHtml: false)
          }
        }
      }
    }
  }
}
'''


def strip_html_tags(text: str) -> str:
    """
    간단히 HTML 태그(<br> 등) 제거하고 엔티티 디코딩
    """
    return html.unescape(text or "").replace('<br>', '\n')


def upsert_series_and_works(page: int, per_page: int):
    """
    AniList에서 page, perPage 만큼 데이터를 가져와
    Series.upsert_from_dict / Work.upsert_from_dict 로 저장합니다.
    """
    variables = {"page": page, "perPage": per_page}
    resp = requests.post(
        ANILIST_API_URL,
        json={"query": SERIES_QUERY, "variables": variables}
    )
    resp.raise_for_status()
    media_list = resp.json()["data"]["Page"]["media"]

    for m in media_list:
        # 1) Series 업서트
        series_data = {
            "externalIds": {"AniList": m["id"]},
            "titleOriginal": m["title"]["romaji"] or m["title"]["english"],
            "titleKr": m["title"]["native"],
            "description": strip_html_tags(m.get("description"))
        }
        series, created = Series.upsert_from_dict(series_data)

        # 2) relations로 묶인 Work들 업서트
        for edge in m.get("relations", {}).get("edges", []):
            node = edge["node"]
            work_data = {
                "seriesId": series.id,
                "externalIds": {"AniList": node["id"]},
                "titleOriginal": node["title"]["romaji"] or node["title"]["english"],
                "titleKr": node["title"]["native"],
                "types": [edge["relationType"]],
                "description": strip_html_tags(node.get("description"))
            }
            Work.upsert_from_dict(work_data)


def main():
    parser = argparse.ArgumentParser(
        description="Collect Series and related Works from AniList."
    )
    parser.add_argument(
        "--pages", type=int, default=3,
        help="Number of AniList pages to fetch"
    )
    parser.add_argument(
        "--per-page", type=int, default=50,
        help="Items per page"
    )
    args = parser.parse_args()

    for p in range(1, args.pages + 1):
        upsert_series_and_works(p, args.per_page)

    print("Series and Works collection completed.")


if __name__ == "__main__":
    main()
