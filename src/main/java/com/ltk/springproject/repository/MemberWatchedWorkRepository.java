package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWatchedWork;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberWatchedWorkRepository extends JpaRepository<MemberWatchedWork, Long> { // Long으로 변경
    // 특정 회원이 특정 작품을 봤는지 확인 (평가 전 확인용)
    boolean existsByMemberIdAndWorkId(Long memberId, Long workId); // Long으로 변경
}