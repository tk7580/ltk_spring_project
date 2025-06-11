package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Series;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ArticleRepository extends JpaRepository<Article, Long> { // Long으로 변경
    // 특정 회원이 작성한 게시글 목록 찾기
    List<Article> findByMember(Member member);
    List<Article> findByMemberId(Long memberId); // Long으로 변경

    // 특정 시리즈(게시판 역할)에 속한 게시글 목록 찾기
    List<Article> findBySeries(Series series);
    List<Article> findBySeriesId(Long seriesId); // Long으로 변경

    // 제목으로 게시글 검색 (부분 일치)
    List<Article> findByTitleContaining(String keyword);

    // 내용으로 게시글 검색 (부분 일치)
    // List<Article> findByBodyContaining(String keyword);
}