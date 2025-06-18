package com.ltk.springproject.repository;

import com.ltk.springproject.domain.WorkIdentifier;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface WorkIdentifierRepository extends JpaRepository<WorkIdentifier, Long> {
    // 출처 이름과 출처 ID로 식별자 정보를 찾음 (핵심 조회 메소드)
    Optional<WorkIdentifier> findBySourceNameAndSourceId(String sourceName, String sourceId);
}