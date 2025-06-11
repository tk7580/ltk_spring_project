package com.ltk.springproject.service;

import com.ltk.springproject.domain.*;
import com.ltk.springproject.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

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

    /**
     * 작품을 찜 목록에 추가합니다.
     */
    // workId 타입을 Long으로 변경
    public void addWorkToWishlist(Long memberId, Long workId) {
        if (wishlistRepository.findByMemberIdAndWorkId(memberId, workId).isPresent()) {
            return;
        }

        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        // workRepository.findById()의 파라미터도 Long 타입 workId를 사용
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        MemberWishlistWork wishlistItem = MemberWishlistWork.builder()
                .member(member)
                .work(work)
                .build();

        wishlistRepository.save(wishlistItem);
    }

    /**
     * 작품을 찜 목록에서 제거(취소)합니다.
     */
    // workId 타입을 Long으로 변경
    public void removeWorkFromWishlist(Long memberId, Long workId) {
        wishlistRepository.findByMemberIdAndWorkId(memberId, workId)
                .ifPresent(wishlistRepository::delete);
    }


    // --- 시청 기록 기능 ---

    /**
     * 작품을 시청 완료 목록에 추가합니다.
     * 이 때, 찜 목록에 해당 작품이 있다면 자동으로 제거됩니다.
     */
    @Transactional
    // workId 타입을 Long으로 변경
    public void markWorkAsWatched(Long memberId, Long workId) {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        if (!watchedRepository.existsByMemberIdAndWorkId(memberId, workId)) {
            MemberWatchedWork watchedItem = MemberWatchedWork.builder()
                    .member(member)
                    .work(work)
                    .build();
            watchedRepository.save(watchedItem);
        }

        removeWorkFromWishlist(memberId, workId);
    }


    // --- 작품 평가 기능 ---

    /**
     * 작품에 대한 평가(별점, 코멘트)를 저장합니다.
     * 시청 기록이 있는 작품에 대해서만 평가할 수 있습니다.
     */
    // workId 타입을 Long으로 변경
    public void rateWork(Long memberId, Long workId, BigDecimal score, String comment) {
        if (!watchedRepository.existsByMemberIdAndWorkId(memberId, workId)) {
            throw new IllegalStateException("시청 기록이 없는 작품은 평가할 수 없습니다.");
        }

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