package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWishlistWork;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberWishlistWorkRepository extends JpaRepository<MemberWishlistWork, Long> {
    // 필요에 따라 사용자 정의 쿼리 메소드 추가 가능
    // 예: Optional<MemberWishlistWork> findByMemberIdAndWorkId(Long memberId, Integer workId);
}