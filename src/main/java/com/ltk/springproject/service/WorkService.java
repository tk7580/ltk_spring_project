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

    public Optional<Work> findWorkById(Long workId) {
        return workRepository.findById(workId);
    }

    public List<Work> findWorksByCriteria(String type, String sortBy) {
        boolean isAllTypes = type == null || type.isEmpty() || "All".equalsIgnoreCase(type);

        if ("rating".equalsIgnoreCase(sortBy)) {
            return isAllTypes ? workRepository.findAllByOrderByAverageRatingDesc() : workRepository.findByTypeOrderByAverageRatingDesc(type);
        } else { // "newest" 등 나머지 모든 경우는 최신순으로 처리
            return isAllTypes ? workRepository.findAllByOrderByReleaseDateDesc() : workRepository.findByTypeOrderByReleaseDateDesc(type);
        }
    }

    public List<String> findAllWorkTypes() {
        return workRepository.findDistinctTypes();
    }
}