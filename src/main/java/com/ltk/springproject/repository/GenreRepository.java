package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Genre;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface GenreRepository extends JpaRepository<Genre, Long> {
    // 장르 이름으로 장르를 찾는 메소드 (중복 확인 시 사용)
    Optional<Genre> findByName(String name);
}