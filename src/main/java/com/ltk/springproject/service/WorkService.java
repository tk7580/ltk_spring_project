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

    /**
     * 모든 작품 목록을 조회합니다.
     * @return 작품 엔티티 리스트
     */
    public List<Work> findAllWorks() {
        return workRepository.findAll();
    }

    /**
     * ID로 작품 한 개를 조회합니다.
     * @param workId 작품의 ID
     * @return 작품 엔티티. 존재하지 않을 경우 Optional.empty()
     */
    public Optional<Work> findWorkById(Long workId) {
        return workRepository.findById(workId);
    }
}