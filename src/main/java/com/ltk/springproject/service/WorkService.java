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
            // '전체' 타입일 경우, 커스텀 정렬 메소드를 호출하도록 변경
            return isAllTypes ? workRepository.findAllByOrderByAverageRatingDescCustom() : workRepository.findByTypeOrderByAverageRatingDesc(type);
        } else { // 기본값은 최신순 (newest)
            // '전체' 타입일 경우, 커스텀 정렬 메소드를 호출하도록 변경
            return isAllTypes ? workRepository.findAllByOrderByReleaseDateDescCustom() : workRepository.findByTypeOrderByReleaseDateDesc(type);
        }
    }

    public List<String> findAllWorkTypes() {
        return workRepository.findDistinctTypes();
    }
}