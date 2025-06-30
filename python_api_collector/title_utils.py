#!/usr/bin/env python
"""
다국어 타이틀 중 ‘가장 보기 좋은 한글/원제’를 골라 주는 유틸
"""
import re
KO = re.compile(r"[가-힣]")

def pick_best_title(*candidates):
    # 1) 완전 한글
    for t in candidates:
        if t and KO.search(t) and t.isalpha() is False:
            return t.strip()
    # 2) 한글·영문 혼합
    for t in candidates:
        if t and KO.search(t):
            return t.strip()
    # 3) 영문
    for t in candidates:
        if t:
            return t.strip()
    return candidates[0] if candidates else ""
