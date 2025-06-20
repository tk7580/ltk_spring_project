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

    /**
     * 인기 차트 페이지를 위한 작품 목록을 조회하고 정렬합니다.
     * @param type 작품 타입 ("Movie", "TV", 또는 "All")
     * @param sortBy 정렬 기준 ("rating" 또는 "newest")
     * @return 정렬된 작품 엔티티 리스트
     */
    public List<Work> findWorksForChart(String type, String sortBy) {
        boolean isAllTypes = type == null || type.isEmpty() || "All".equalsIgnoreCase(type);

        if ("rating".equalsIgnoreCase(sortBy)) {
            return isAllTypes ? workRepository.findAllByOrderByAverageRatingDesc() : workRepository.findByTypeOrderByAverageRatingDesc(type);
        } else { // 기본값은 최신순 (newest)
            return isAllTypes ? workRepository.findAllByOrderByReleaseDateDesc() : workRepository.findByTypeOrderByReleaseDateDesc(type);
        }
    }

    /**
     * DB에 있는 모든 작품의 type을 중복 없이 조회합니다. (동적 필터 버튼 생성용)
     * @return 작품 타입 문자열 리스트
     */
    public List<String> findAllWorkTypes() {
        return workRepository.findDistinctTypes();
    }
}