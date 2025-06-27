package com.ltk.springproject.repository;

import com.ltk.springproject.domain.ArticleViewLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ArticleViewLogRepository extends JpaRepository<ArticleViewLog, Long> {

    /**
     * 특정 사용자가 특정 게시물을 조회한 기록이 있는지 확인합니다.
     * @param memberId  조회할 사용자의 ID
     * @param articleId 조회할 게시글의 ID
     * @return 조회 기록이 존재하면 true, 없으면 false
     */
    boolean existsByMemberIdAndArticleId(Long memberId, Long articleId);
}