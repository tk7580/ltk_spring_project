package com.ltk.springproject.service;

import com.ltk.springproject.domain.Series;
import com.ltk.springproject.repository.SeriesRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class SeriesService {

    private final SeriesRepository seriesRepository;

    public Series findById(Long seriesId) {
        return seriesRepository.findById(seriesId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "시리즈를 찾을 수 없습니다."));
    }
}