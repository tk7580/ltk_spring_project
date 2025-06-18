package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWatchedWork;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional; // Optional 임포트가 필요할 수 있습니다.

public interface MemberWatchedWorkRepository extends JpaRepository<MemberWatchedWork, Long> {

    // 특정 회원이 특정 작품을 봤는지 확인
    boolean existsByMemberIdAndWorkId(Long memberId, Long workId);

    // ===== 이 메소드를 새로 추가합니다. =====
    // 특정 회원의 특정 작품에 대한 감상 기록 조회 (시청 취소 시 객체를 찾아 삭제하기 위해 필요)
    Optional<MemberWatchedWork> findByMemberIdAndWorkId(Long memberId, Long workId);
    // ===================================

    // 특정 회원의 감상 완료 목록 조회
    List<MemberWatchedWork> findByMemberId(Long memberId);
}