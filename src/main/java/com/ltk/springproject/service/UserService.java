package com.ltk.springproject.service;

import com.ltk.springproject.dto.MyPageDto;
import com.ltk.springproject.dto.WorkDto;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.MemberWishlistWork;
import com.ltk.springproject.domain.MemberWatchedWork;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.repository.MemberWishlistWorkRepository;
import com.ltk.springproject.repository.MemberWatchedWorkRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class UserService {

    private final MemberRepository memberRepo;
    private final MemberWishlistWorkRepository wishlistRepo;
    private final MemberWatchedWorkRepository watchedRepo;

    public UserService(MemberRepository memberRepo,
                       MemberWishlistWorkRepository wishlistRepo,
                       MemberWatchedWorkRepository watchedRepo) {
        this.memberRepo   = memberRepo;
        this.wishlistRepo = wishlistRepo;
        this.watchedRepo  = watchedRepo;
    }

    /**
     * 로그인 멤버의 마이페이지 DTO를 구성합니다.
     */
    public MyPageDto buildMyPage(Long memberId) {
        Member m = memberRepo.findById(memberId)
                .orElseThrow(() -> new IllegalArgumentException("멤버를 찾을 수 없습니다: " + memberId));

        MyPageDto dto = new MyPageDto();
        dto.setUserId(m.getId());
        dto.setUsername(m.getUsername());

        // 즐겨찾기
        List<WorkDto> favorites = wishlistRepo.findByMemberId(memberId).stream()
                .map(MemberWishlistWork::getWork)
                .map(WorkDto::fromEntity)
                .collect(Collectors.toList());
        dto.setFavorites(favorites);

        // 시청 기록
        List<WorkDto> history = watchedRepo.findByMemberId(memberId).stream()
                .map(MemberWatchedWork::getWork)
                .map(WorkDto::fromEntity)
                .collect(Collectors.toList());
        dto.setWatchHistory(history);

        return dto;
    }
}
