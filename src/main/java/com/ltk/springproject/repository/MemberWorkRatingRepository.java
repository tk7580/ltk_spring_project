package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWorkRating;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface MemberWorkRatingRepository extends JpaRepository<MemberWorkRating, Long> {
    // 특정 회원의 특정 작품에 대한 평가 기록 조회 (평가 수정 시 사용)
    Optional<MemberWorkRating> findByMemberIdAndWorkId(Long memberId, Integer workId);
}