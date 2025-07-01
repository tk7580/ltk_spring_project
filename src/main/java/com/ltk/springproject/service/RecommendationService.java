// src/main/java/com/ltk/springproject/service/RecommendationService.java
package com.ltk.springproject.service;

import com.ltk.springproject.dto.WorkDto;
import com.ltk.springproject.domain.Work;
import com.ltk.springproject.domain.MemberWishlistWork;
import com.ltk.springproject.domain.MemberWatchedWork;
import com.ltk.springproject.repository.MemberWishlistWorkRepository;
import com.ltk.springproject.repository.MemberWatchedWorkRepository;
import com.ltk.springproject.repository.WorkRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class RecommendationService {
    private final MemberWishlistWorkRepository wishlistRepo;
    private final MemberWatchedWorkRepository watchedRepo;
    private final WorkRepository workRepository;

    public RecommendationService(MemberWishlistWorkRepository wishlistRepo,
                                 MemberWatchedWorkRepository watchedRepo,
                                 WorkRepository workRepository) {
        this.wishlistRepo = wishlistRepo;
        this.watchedRepo = watchedRepo;
        this.workRepository = workRepository;
    }

    public List<WorkDto> recommendFor(Long memberId) {
        List<Work> favoriteWorks = wishlistRepo.findByMemberId(memberId)
                .stream().map(MemberWishlistWork::getWork).collect(Collectors.toList());
        List<Work> watchedWorks = watchedRepo.findByMemberId(memberId)
                .stream().map(MemberWatchedWork::getWork).collect(Collectors.toList());

        Set<String> favGenres = favoriteWorks.stream()
                .flatMap(w -> w.getWorkGenres().stream()
                        .map(wg -> wg.getGenre().getName()))
                .collect(Collectors.toSet());

        Set<Long> excludedIds = new HashSet<>();
        favoriteWorks.forEach(w -> excludedIds.add(w.getId()));
        watchedWorks.forEach(w -> excludedIds.add(w.getId()));

        List<Work> works = workRepository.recommendWorksByGenres(
                new ArrayList<>(favGenres),
                new ArrayList<>(excludedIds),
                PageRequest.of(0, 10)
        );

        return works.stream().map(WorkDto::fromEntity).collect(Collectors.toList());
    }
}
