package com.ltk.springproject.service;

import com.ltk.springproject.domain.*;
import com.ltk.springproject.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@Transactional
@RequiredArgsConstructor
public class UserActivityService {

    private final MemberRepository memberRepository;
    private final WorkRepository workRepository;
    private final MemberWishlistWorkRepository wishlistRepository;
    private final MemberWatchedWorkRepository watchedRepository;
    private final MemberWorkRatingRepository ratingRepository;

    @Transactional(readOnly = true)
    public List<Work> findWishlistedWorksByMemberId(Long memberId) {
        return wishlistRepository.findByMemberId(memberId).stream()
                .map(MemberWishlistWork::getWork)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public boolean isWorkWishlisted(Long memberId, Long workId) {
        return wishlistRepository.findByMemberIdAndWorkId(memberId, workId).isPresent();
    }

    public void addWorkToWishlist(Long memberId, Long workId) {
        if (isWorkWishlisted(memberId, workId)) return;
        Member member = memberRepository.findById(memberId).orElseThrow();
        Work work = workRepository.findById(workId).orElseThrow();
        wishlistRepository.save(MemberWishlistWork.builder().member(member).work(work).build());
    }

    public void removeWorkFromWishlist(Long memberId, Long workId) {
        wishlistRepository.findByMemberIdAndWorkId(memberId, workId).ifPresent(wishlistRepository::delete);
    }

    // (이하 다른 메소드들은 생략, 기존 코드와 동일)
}