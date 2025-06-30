package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Work;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface WorkRepository extends JpaRepository<Work, Long> {

    List<Work> findBySeriesId(Long seriesId);

    // [수정] work_type 테이블에서 모든 타입 이름을 가져오도록 변경
    @Query("SELECT wt.name FROM WorkType wt ORDER BY wt.id")
    List<String> findDistinctTypes();

    // [수정] work.type 대신 work_type_mapping을 JOIN하여 필터링
    @Query("SELECT w FROM Work w JOIN w.workTypeMappings wtm JOIN wtm.workType wt WHERE wt.name = :type ORDER BY w.releaseDate DESC")
    List<Work> findByTypeNameOrderByReleaseDateDesc(@Param("type") String type);

    // [수정] work.type 대신 work_type_mapping을 JOIN하여 필터링
    @Query("SELECT w FROM Work w JOIN w.workTypeMappings wtm JOIN wtm.workType wt WHERE wt.name = :type ORDER BY w.averageRating DESC, w.ratingCount DESC")
    List<Work> findByTypeNameOrderByAverageRatingDesc(@Param("type") String type);

    // [수정] work.type을 사용하던 복잡한 정렬 로직을 단순화
    @Query("SELECT w FROM Work w ORDER BY w.releaseDate DESC")
    List<Work> findAllByOrderByReleaseDateDesc();

    // [수정] work.type을 사용하던 복잡한 정렬 로직을 단순화
    @Query("SELECT w FROM Work w ORDER BY w.averageRating DESC, w.ratingCount DESC")
    List<Work> findAllByOrderByAverageRatingDesc();

    // 평점순으로 상위 N개 작품 조회 (기존과 유사)
    @Query("SELECT w FROM Work w ORDER BY w.averageRating DESC, w.ratingCount DESC")
    List<Work> findTopWorksByRating(Pageable pageable);


}