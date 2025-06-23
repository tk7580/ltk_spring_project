package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Work;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface WorkRepository extends JpaRepository<Work, Long> {

    List<Work> findBySeriesId(Long seriesId);

    List<Work> findByType(String type);

    @Query(value = "SELECT DISTINCT type FROM work ORDER BY type", nativeQuery = true)
    List<String> findDistinctTypes();

    List<Work> findByTypeOrderByReleaseDateDesc(String type);

    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id WHERE w.type = :type GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findByTypeOrderByAverageRatingDesc(@Param("type") String type);

    /**
     * 모든 타입의 작품들을 커스텀 순서(Movie > TV > 기타)로 정렬한 뒤, 최신순으로 정렬합니다.
     */
    @Query("SELECT w FROM Work w ORDER BY CASE WHEN w.type = 'Movie' THEN 1 WHEN w.type = 'TV' THEN 2 ELSE 3 END, w.releaseDate DESC")
    List<Work> findAllByOrderByReleaseDateDescCustom();

    /**
     * 모든 타입의 작품들을 커스텀 순서(Movie > TV > 기타)로 정렬한 뒤, 평점순으로 정렬합니다.
     */
    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id GROUP BY w.id ORDER BY CASE WHEN w.type = 'Movie' THEN 1 WHEN w.type = 'TV' THEN 2 ELSE 3 END, AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findAllByOrderByAverageRatingDescCustom();
}