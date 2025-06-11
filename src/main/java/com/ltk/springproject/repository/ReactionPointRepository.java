package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.ReactionPoint;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface ReactionPointRepository extends JpaRepository<ReactionPoint, Long> { // Long으로 변경
    // 특정 회원이 남긴 반응 찾기
    List<ReactionPoint> findByMember(Member member);
    List<ReactionPoint> findByMemberId(Long memberId); // Long으로 변경

    // 특정 관련 타입과 ID로 반응 찾기 (예: 특정 게시글에 대한 모든 반응)
    List<ReactionPoint> findByRelTypeCodeAndRelId(String relTypeCode, Long relId); // Long으로 변경

    // 특정 회원이 특정 대상에 특정 타입의 반응을 했는지 확인
    Optional<ReactionPoint> findByMemberAndRelTypeCodeAndRelIdAndReactionType(Member member, String relTypeCode, Long relId, String reactionType); // Long으로 변경
    Optional<ReactionPoint> findByMemberIdAndRelTypeCodeAndRelIdAndReactionType(Long memberId, String relTypeCode, Long relId, String reactionType); // Long으로 변경
}