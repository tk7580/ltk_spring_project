package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Work;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface WorkRepository extends JpaRepository<Work, Long> {

    List<Work> findBySeriesId(Long seriesId);

    // ===== 차트 기능을 위한 쿼리 메소드들 추가 =====

    // DB에 저장된 모든 work의 type 종류를 중복 없이 조회 (동적 필터 버튼 생성용)
    @Query(value = "SELECT DISTINCT type FROM work ORDER BY type", nativeQuery = true)
    List<String> findDistinctTypes();

    // 특정 타입의 작품들을 최신순으로 정렬
    List<Work> findByTypeOrderByReleaseDateDesc(String type);

    // 모든 타입의 작품들을 최신순으로 정렬
    List<Work> findAllByOrderByReleaseDateDesc();

    // 특정 타입의 작품들을 평점순으로 정렬 (JPQL 사용)
    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id WHERE w.type = :type GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findByTypeOrderByAverageRatingDesc(@Param("type") String type);

    // 모든 타입의 작품들을 평점순으로 정렬 (JPQL 사용)
    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findAllByOrderByAverageRatingDesc();
}