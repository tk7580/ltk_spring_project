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
@Transactional // 여러 DB 작업을 하나의 단위로 묶어서 처리합니다. (예: 시청 기록 추가 + 찜 목록 삭제)
@RequiredArgsConstructor // final 필드에 대한 생성자 자동 생성 (Lombok)
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
    public void addWorkToWishlist(Long memberId, Integer workId) {
        // 이미 찜한 작품인지 확인
        if (wishlistRepository.findByMemberIdAndWorkId(memberId, workId).isPresent()) {
            // 이미 찜 목록에 있다면 아무것도 하지 않거나, 예외를 발생시킬 수 있습니다.
            // 여기서는 간단히 종료합니다.
            return;
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

    /**
     * 작품을 찜 목록에서 제거(취소)합니다.
     */
    public void removeWorkFromWishlist(Long memberId, Integer workId) {
        // 찜 기록을 찾아서 있으면 삭제합니다.
        wishlistRepository.findByMemberIdAndWorkId(memberId, workId)
                .ifPresent(wishlistRepository::delete);
    }


    // --- 시청 기록 기능 ---

    /**
     * 작품을 시청 완료 목록에 추가합니다.
     * 이 때, 찜 목록에 해당 작품이 있다면 자동으로 제거됩니다.
     */
    @Transactional // 이 메소드는 여러 DB 작업을 하므로 트랜잭션 처리가 중요합니다.
    public void markWorkAsWatched(Long memberId, Integer workId) {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        // 이미 시청 기록이 있는지 확인하고, 없다면 새로 생성합니다.
        if (!watchedRepository.existsByMemberIdAndWorkId(memberId, workId)) {
            MemberWatchedWork watchedItem = MemberWatchedWork.builder()
                    .member(member)
                    .work(work)
                    .build();
            watchedRepository.save(watchedItem);
        }

        // 찜 목록에 있었다면 제거합니다.
        removeWorkFromWishlist(memberId, workId);
    }


    // --- 작품 평가 기능 ---

    /**
     * 작품에 대한 평가(별점, 코멘트)를 저장합니다.
     * 시청 기록이 있는 작품에 대해서만 평가할 수 있습니다.
     */
    public void rateWork(Long memberId, Integer workId, BigDecimal score, String comment) {
        // 1. 시청 기록이 있는지 확인
        if (!watchedRepository.existsByMemberIdAndWorkId(memberId, workId)) {
            throw new IllegalStateException("시청 기록이 없는 작품은 평가할 수 없습니다.");
        }

        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다. id=" + memberId));
        Work work = workRepository.findById(workId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 작품입니다. id=" + workId));

        // 2. 기존 평가가 있는지 확인 후, 있으면 업데이트, 없으면 새로 생성
        Optional<MemberWorkRating> existingRatingOpt = ratingRepository.findByMemberIdAndWorkId(memberId, workId);

        if (existingRatingOpt.isPresent()) {
            // 기존 평가 업데이트
            MemberWorkRating existingRating = existingRatingOpt.get();
            existingRating.setScore(score);
            existingRating.setComment(comment);
            ratingRepository.save(existingRating); // 변경 감지(dirty checking)로 자동 업데이트될 수도 있지만, 명시적으로 save 호출
        } else {
            // 신규 평가 생성
            MemberWorkRating newRating = MemberWorkRating.builder()
                    .member(member)
                    .work(work)
                    .score(score)
                    .comment(comment)
                    .build();
            ratingRepository.save(newRating);
        }
    }

    // (참고) 리포지토리에 findByMemberIdAndWorkId 추가 필요
    // MemberWorkRatingRepository 에 아래 메소드 추가:
    // Optional<MemberWorkRating> findByMemberIdAndWorkId(Long memberId, Integer workId);
}
