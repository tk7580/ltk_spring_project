package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Work;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface WorkRepository extends JpaRepository<Work, Long> {

    List<Work> findBySeriesId(Long seriesId);

    // ===== 타입별, 최신순 정렬을 위한 쿼리 메소드 추가 =====
    List<Work> findByTypeOrderByReleaseDateDesc(String type);
    List<Work> findAllByOrderByReleaseDateDesc();

    // ===== 타입별, 평점순 정렬을 위한 JPQL 쿼리 추가 =====
    // 평점이 없는 작품도 포함시키기 위해 LEFT JOIN 사용
    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id WHERE w.type = :type GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findByTypeOrderByAverageRatingDesc(@Param("type") String type);

    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findAllByOrderByAverageRatingDesc();
}