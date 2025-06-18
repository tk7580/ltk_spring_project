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

    public boolean addWorkToWishlist(Long memberId, Long workId) {
        if (isWorkWishlisted(memberId, workId)) {
            return false;
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
        return true;
    }

    public boolean removeWorkFromWishlist(Long memberId, Long workId) {
        Optional<MemberWishlistWork> wishlistItem = wishlistRepository.findByMemberIdAndWorkId(memberId, workId);

        if (wishlistItem.isPresent()) {
            wishlistRepository.delete(wishlistItem.get());
            return true;
        }

        return false;
    }


    // --- 감상 완료 기능 ---

    @Transactional(readOnly = true)
    public boolean isWorkWatched(Long memberId, Long workId) {
        return watchedRepository.existsByMemberIdAndWorkId(memberId, workId);
    }

    @Transactional
    public void markWorkAsWatched(Long memberId, Long workId) {
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

        removeWorkFromWishlist(memberId, workId);
    }

    /**
     * @return 실제로 시청 기록이 삭제되었으면 true, 원래 없었으면 false
     */
    public boolean cancelWorkWatch(Long memberId, Long workId) {
        return watchedRepository.findByMemberIdAndWorkId(memberId, workId)
                .map(watchedWork -> {
                    watchedRepository.delete(watchedWork);
                    return true;
                })
                .orElse(false);
    }


    // --- 작품 평가 기능 ---

    public void rateWork(Long memberId, Long workId, BigDecimal score, String comment) {
        markWorkAsWatched(memberId, workId);

        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        Optional<MemberWorkRating> existingRatingOpt = ratingRepository.findByMemberIdAndWorkId(memberId, workId);

        if (existingRatingOpt.isPresent()) {
            MemberWorkRating existingRating = existingRatingOpt.get();
            existingRating.setScore(score);
            existingRating.setComment(comment);
            ratingRepository.save(existingRating);
        } else {
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