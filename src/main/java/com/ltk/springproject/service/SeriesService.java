package com.ltk.springproject.service;

import com.ltk.springproject.domain.Series;
import com.ltk.springproject.repository.SeriesRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List; // [수정] List 임포트 추가

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class SeriesService {

    private final SeriesRepository seriesRepository;

    public Series findById(Long seriesId) {
        return seriesRepository.findById(seriesId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "시리즈를 찾을 수 없습니다."));
    }

    // [수정] 모든 시리즈를 조회하는 메소드 추가
    public List<Series> findAll() {
        return seriesRepository.findAll();
    }
}