package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Series;
import com.ltk.springproject.domain.Work;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
// import java.time.LocalDate; // 필요시

public interface WorkRepository extends JpaRepository<Work, Long> { // Long으로 변경
    // 특정 시리즈에 속한 작품들 찾기
    List<Work> findBySeries(Series series);

    // 특정 시리즈 ID로 작품들 찾기
    List<Work> findBySeriesId(Long seriesId); // Long으로 변경

    // 작품 타입으로 작품들 찾기
    List<Work> findByType(String type);

    // 작품 한글 제목으로 검색 (부분 일치)
    // List<Work> findByTitleKrContaining(String keyword);

    // 특정 출시일 이후의 작품들 찾기
    // List<Work> findByReleaseDateAfter(LocalDate date);
}