package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Work;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface WorkRepository extends JpaRepository<Work, Long> {

    List<Work> findBySeriesId(Long seriesId);

    @Query(value = "SELECT DISTINCT type FROM work ORDER BY type", nativeQuery = true)
    List<String> findDistinctTypes();

    List<Work> findByTypeOrderByReleaseDateDesc(String type);

    List<Work> findAllByOrderByReleaseDateDesc();

    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id WHERE w.type = :type GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findByTypeOrderByAverageRatingDesc(@Param("type") String type);

    @Query("SELECT w FROM Work w LEFT JOIN MemberWorkRating r ON w.id = r.work.id GROUP BY w.id ORDER BY AVG(r.score) DESC, COUNT(r.score) DESC")
    List<Work> findAllByOrderByAverageRatingDesc();
}