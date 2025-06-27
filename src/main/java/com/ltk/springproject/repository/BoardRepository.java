package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Board;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface BoardRepository extends JpaRepository<Board, Long> {
    // 게시판 코드로 게시판 찾기
    Optional<Board> findByCode(String code);

    // 게시판 이름으로 게시판 찾기
    Optional<Board> findByName(String name);

    // [수정] Series ID로 Board를 조회하는 메소드 추가
    Optional<Board> findBySeriesId(Long seriesId);
}