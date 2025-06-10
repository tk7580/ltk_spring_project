package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWorkRating;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberWorkRatingRepository extends JpaRepository<MemberWorkRating, Long> {
    // 필요에 따라 사용자 정의 쿼리 메소드 추가 가능
}