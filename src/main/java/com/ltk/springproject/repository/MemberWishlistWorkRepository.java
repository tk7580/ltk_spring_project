package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWishlistWork;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface MemberWishlistWorkRepository extends JpaRepository<MemberWishlistWork, Long> {
    // 특정 회원의 특정 작품에 대한 찜 기록 조회 (찜 취소 또는 중복 확인 시 사용)
    Optional<MemberWishlistWork> findByMemberIdAndWorkId(Long memberId, Integer workId);
}