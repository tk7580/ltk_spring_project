package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ArticleRepository extends JpaRepository<Article, Long> {
    // 특정 회원이 작성한 게시글 목록 찾기
    List<Article> findByMember(Member member);
    List<Article> findByMemberId(Long memberId);

    // [삭제] 아래 두 메소드가 오류의 원인이므로 삭제합니다.
    // List<Article> findByWork(Work work);
    // List<Article> findByWorkId(Long workId);

    // 제목으로 게시글 검색 (부분 일치)
    List<Article> findByTitleContaining(String keyword);

    // Board ID로 게시글을 찾아 최신순으로 정렬 (ID 역순)
    List<Article> findByBoardIdOrderByIdDesc(Long boardId);
}