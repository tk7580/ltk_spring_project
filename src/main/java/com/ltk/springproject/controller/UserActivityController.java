package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.UserActivityService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.security.Principal;

@Controller
@RequiredArgsConstructor
@RequestMapping("/member/activity") // 사용자 활동 관련 URL을 명확히 분리
public class UserActivityController {

    private final UserActivityService userActivityService;
    private final MemberRepository memberRepository;

    // 로그인한 사용자의 Member 객체를 가져오는 헬퍼 메소드
    private Member getCurrentUser(Principal principal) {
        if (principal == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }
        return memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자 정보를 찾을 수 없습니다."));
    }

    /**
     * 특정 작품을 찜 목록에 추가하는 API
     * @param workId 찜할 작품의 ID
     * @param principal 현재 로그인한 사용자 정보
     * @return 성공 시 200 OK
     */
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/work/{workId}/wishlist")
    @ResponseBody
    public ResponseEntity<Void> addWishlist(@PathVariable Long workId, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        userActivityService.addWorkToWishlist(currentUser.getId(), workId);
        return ResponseEntity.ok().build();
    }

    /**
     * 특정 작품을 찜 목록에서 제거하는 API
     * @param workId 찜 취소할 작품의 ID
     * @param principal 현재 로그인한 사용자 정보
     * @return 성공 시 200 OK
     */
    @PreAuthorize("isAuthenticated()")
    @DeleteMapping("/work/{workId}/wishlist")
    @ResponseBody
    public ResponseEntity<Void> removeWishlist(@PathVariable Long workId, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        userActivityService.removeWorkFromWishlist(currentUser.getId(), workId);
        return ResponseEntity.ok().build();
    }
}