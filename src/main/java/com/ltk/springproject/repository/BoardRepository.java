package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Board;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface BoardRepository extends JpaRepository<Board, Integer> {
    // 게시판 코드로 게시판 찾기
    Optional<Board> findByCode(String code);

    // 게시판 이름으로 게시판 찾기
    Optional<Board> findByName(String name);
}