package com.ltk.springproject.repository;

import com.ltk.springproject.domain.MemberWatchedWork;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberWatchedWorkRepository extends JpaRepository<MemberWatchedWork, Long> {
    // 필요에 따라 사용자 정의 쿼리 메소드 추가 가능
}