package com.ltk.springproject.service;

import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.WorkRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true) // 데이터 조회가 주 목적이므로 readOnly = true 설정
@RequiredArgsConstructor // final 필드에 대한 생성자 자동 생성 (Lombok)
public class WorkService {

    private final WorkRepository workRepository;

    /**
     * 모든 작품 목록을 조회합니다.
     * @return 작품 엔티티 리스트
     */
    public List<Work> findAllWorks() {
        return workRepository.findAll();
    }

    // TODO: 향후 아래와 같은 메소드들을 추가할 수 있습니다.
    /*
    public List<Work> findPopularWorks() {
        // 인기 작품을 조회하는 로직 (예: 특정 기준에 따라 정렬)
        return workRepository.findTop20ByOrderByPopularityDesc(); // 예시 메소드
    }

    public List<Work> findNewWorks() {
        // 최신 작품을 조회하는 로직
        return workRepository.findTop20ByOrderByReleaseDateDesc(); // 예시 메소드
    }

    public Work findWorkById(Integer workId) {
        return workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));
    }
    */
}