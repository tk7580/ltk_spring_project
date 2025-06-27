package com.ltk.springproject.repository;

import com.ltk.springproject.domain.ReactionPoint;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ReactionPointRepository extends JpaRepository<ReactionPoint, Long> {

    /**
     * 특정 사용자가 특정 대상(게시글 또는 댓글)에 반응을 남겼는지 찾기 위해 사용합니다.
     * 이 메서드가 ReactionService의 핵심 로직에서 사용됩니다.
     * @param memberId 사용자 ID
     * @param relTypeCode 대상 타입 ('article' 또는 'reply')
     * @param relId 대상 ID
     * @return ReactionPoint 객체를 담은 Optional
     */
    Optional<ReactionPoint> findByMemberIdAndRelTypeCodeAndRelId(Long memberId, String relTypeCode, Long relId);
}