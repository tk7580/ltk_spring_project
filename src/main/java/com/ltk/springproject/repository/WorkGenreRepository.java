package com.ltk.springproject.repository;

import com.ltk.springproject.domain.WorkGenre;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkGenreRepository extends JpaRepository<WorkGenre, Long> {
    // 기본 CRUD 외에 특별한 메소드는 пока 필요 없음
}