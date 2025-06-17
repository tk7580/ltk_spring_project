package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWatchedWork;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List; // List 임포트 추가

public interface MemberWatchedWorkRepository extends JpaRepository<MemberWatchedWork, Long> {

    // ===== 이 줄이 누락되었습니다. 추가합니다. =====
    // 특정 회원이 특정 작품을 봤는지 확인 (평가 전 확인용 등)
    boolean existsByMemberIdAndWorkId(Long memberId, Long workId);
    // =======================================

    // 특정 회원의 감상 완료 목록 조회
    List<MemberWatchedWork> findByMemberId(Long memberId);
}