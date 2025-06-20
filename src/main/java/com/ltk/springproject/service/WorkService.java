package com.ltk.springproject.service;

import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.WorkRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class WorkService {

    private final WorkRepository workRepository;

    public List<Work> findAllWorks() {
        return workRepository.findAll();
    }

    public Optional<Work> findWorkById(Long workId) {
        return workRepository.findById(workId);
    }

    // ===== 차트 페이지를 위한 메소드 추가 =====
    public List<Work> findWorksForChart(String type, String sortBy) {
        boolean isAllTypes = type == null || type.isEmpty() || type.equals("All");

        if ("rating".equalsIgnoreCase(sortBy)) {
            if (isAllTypes) {
                return workRepository.findAllByOrderByAverageRatingDesc();
            } else {
                return workRepository.findByTypeOrderByAverageRatingDesc(type);
            }
        } else { // 기본값은 최신순 (releaseDate)
            if (isAllTypes) {
                return workRepository.findAllByOrderByReleaseDateDesc();
            } else {
                return workRepository.findByTypeOrderByReleaseDateDesc(type);
            }
        }
    }
    // =====================================
}