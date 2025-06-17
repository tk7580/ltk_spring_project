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

    // --- 찜하기 기능 ---

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
        if (isWorkWishlisted(memberId, workId)) {
            return; // 이미 찜 목록에 있으면 아무것도 하지 않음
        }
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        MemberWishlistWork wishlistItem = MemberWishlistWork.builder()
                .member(member)
                .work(work)
                .build();

        wishlistRepository.save(wishlistItem);
    }

    public void removeWorkFromWishlist(Long memberId, Long workId) {
        wishlistRepository.findByMemberIdAndWorkId(memberId, workId)
                .ifPresent(wishlistRepository::delete);
    }


    // --- 감상 완료 기능 ---

    @Transactional
    public void markWorkAsWatched(Long memberId, Long workId) {
        // 이미 감상 완료 목록에 있다면 아무것도 하지 않음
        if (watchedRepository.existsByMemberIdAndWorkId(memberId, workId)) {
            return;
        }

        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        MemberWatchedWork watchedItem = MemberWatchedWork.builder()
                .member(member)
                .work(work)
                .build();
        watchedRepository.save(watchedItem);

        // 감상 완료 시, 찜 목록에 있었다면 자동으로 제거
        removeWorkFromWishlist(memberId, workId);
    }


    // --- 작품 평가 기능 ---

    public void rateWork(Long memberId, Long workId, BigDecimal score, String comment) {
        // 평점을 남기면, 자동으로 '감상 완료' 처리
        markWorkAsWatched(memberId, workId);

        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        Optional<MemberWorkRating> existingRatingOpt = ratingRepository.findByMemberIdAndWorkId(memberId, workId);

        if (existingRatingOpt.isPresent()) {
            // 이미 평점이 있으면 점수와 코멘트만 업데이트
            MemberWorkRating existingRating = existingRatingOpt.get();
            existingRating.setScore(score);
            existingRating.setComment(comment);
            ratingRepository.save(existingRating);
        } else {
            // 평점이 없으면 새로 생성
            MemberWorkRating newRating = MemberWorkRating.builder()
                    .member(member)
                    .work(work)
                    .score(score)
                    .comment(comment)
                    .build();
            ratingRepository.save(newRating);
        }
    }
}