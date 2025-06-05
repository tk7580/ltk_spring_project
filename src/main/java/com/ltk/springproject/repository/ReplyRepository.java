package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Reply;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ReplyRepository extends JpaRepository<Reply, Integer> {
    // 특정 게시글에 달린 댓글 목록 찾기 (부모 댓글이 없는 최상위 댓글들)
    List<Reply> findByArticleAndParentIsNull(Article article);
    List<Reply> findByArticleIdAndParentIsNull(Integer articleId);

    // 특정 회원이 작성한 댓글 목록 찾기
    List<Reply> findByMember(Member member);
    List<Reply> findByMemberId(Long memberId);

    // 특정 부모 댓글에 속한 자식 댓글(대댓글) 목록 찾기
    List<Reply> findByParent(Reply parent);
    List<Reply> findByParentId(Integer parentId);
}