package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Series;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional; // 필요에 따라 추가

public interface SeriesRepository extends JpaRepository<Series, Integer> {
    // 예시: 시리즈 한글 제목으로 검색 (부분 일치)
    // List<Series> findByTitleKrContaining(String keyword);

    // 예시: 시리즈 원작자로 검색
    // List<Series> findByAuthor(String author);
}