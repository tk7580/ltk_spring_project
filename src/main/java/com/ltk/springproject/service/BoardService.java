package com.ltk.springproject.service;

import com.ltk.springproject.domain.Board;
import com.ltk.springproject.domain.Series;
import com.ltk.springproject.repository.BoardRepository;
import com.ltk.springproject.repository.SeriesRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
@RequiredArgsConstructor
public class BoardService {

    private final BoardRepository boardRepository;
    private final SeriesRepository seriesRepository;

    // 시리즈 ID로 게시판을 찾거나, 없으면 새로 생성하는 메서드
    public Board getBoardBySeriesId(Long seriesId) {
        return boardRepository.findBySeriesId(seriesId)
                .orElseGet(() -> createBoardForSeries(seriesId));
    }

    // 특정 시리즈에 대한 게시판을 생성하는 내부 메서드
    private Board createBoardForSeries(Long seriesId) {
        Series series = seriesRepository.findById(seriesId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 시리즈입니다."));

        Board board = Board.builder()
                .series(series)
                .name(series.getTitleKr() + " 게시판")
                .code("series_" + series.getId())
                .build();

        return boardRepository.save(board);
    }
}