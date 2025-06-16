package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWishlistWork;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface MemberWishlistWorkRepository extends JpaRepository<MemberWishlistWork, Long> {
    // 특정 회원의 특정 작품에 대한 찜 기록 조회
    Optional<MemberWishlistWork> findByMemberIdAndWorkId(Long memberId, Long workId);

    // 특정 회원의 모든 찜 목록 조회
    List<MemberWishlistWork> findByMemberId(Long memberId);
}