package com.example.ltkspring.service;

import com.example.ltkspring.dto.WorkDto;
import com.example.ltkspring.model.User;
import com.example.ltkspring.repository.WorkRepository;
import com.example.ltkspring.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class RecommendationService {
    private final UserRepository userRepository;
    private final WorkRepository workRepository;

    public RecommendationService(UserRepository userRepository, WorkRepository workRepository) {
        this.userRepository = userRepository;
        this.workRepository = workRepository;
    }

    /**
     * 사용자 시청/즐겨찾기 기반으로 추천 목록 생성
     */
    @Transactional(readOnly = true)
    public List<WorkDto> recommendFor(Long userId) {
        User user = userRepository.findById(userId).orElseThrow();
        // 사용자가 좋아한 장르 수집
        List<String> favGenres = user.getFavorites().stream()
                .flatMap(w -> w.getGenres().stream())
                .distinct()
                .collect(Collectors.toList());
        // 유사 장르 작품 상위 10개 조회 (평점·최신순)
        return workRepository.findTop10ByGenresInAndIdNotInOrderByAverageScoreDesc(favGenres,
                        user.getWatchedIds())
                .stream()
                .map(WorkDto::fromEntity)
                .collect(Collectors.toList());
    }
}
