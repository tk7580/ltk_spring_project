package com.ltk.springproject.service;

import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.WorkRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class WorkService {

    private final WorkRepository workRepository;

    public Optional<Work> findWorkById(Long workId) {
        return workRepository.findById(workId);
    }

    public List<Work> findWorksByCriteria(String type, String sortBy) {
        boolean isAllTypes = type == null || type.isEmpty() || "All".equalsIgnoreCase(type);

        if ("rating".equalsIgnoreCase(sortBy)) {
            // [수정] Repository의 변경된 메소드 이름(findByTypeName...)을 호출합니다.
            return isAllTypes ? workRepository.findAllByOrderByAverageRatingDesc() : workRepository.findByTypeNameOrderByAverageRatingDesc(type);
        } else { // 기본값은 최신순 (newest)
            // [수정] Repository의 변경된 메소드 이름(findByTypeName...)을 호출합니다.
            return isAllTypes ? workRepository.findAllByOrderByReleaseDateDesc() : workRepository.findByTypeNameOrderByReleaseDateDesc(type);
        }
    }

    public List<Work> findTopWorks(int size) {
        Pageable pageable = PageRequest.of(0, size);
        return workRepository.findTopWorksByRating(pageable);
    }

    public List<String> findAllWorkTypes() {
        return workRepository.findDistinctTypes();
    }
}