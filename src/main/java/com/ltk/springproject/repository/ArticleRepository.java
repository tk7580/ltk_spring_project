package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Work; // Series 대신 Work를 임포트
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ArticleRepository extends JpaRepository<Article, Long> {
    // 특정 회원이 작성한 게시글 목록 찾기
    List<Article> findByMember(Member member);
    List<Article> findByMemberId(Long memberId);

    // ★★★ [수정] 특정 작품(Work)에 속한 게시글 목록을 찾도록 변경 ★★★
    List<Article> findByWork(Work work);
    List<Article> findByWorkId(Long workId);

    // 제목으로 게시글 검색 (부분 일치)
    List<Article> findByTitleContaining(String keyword);
}