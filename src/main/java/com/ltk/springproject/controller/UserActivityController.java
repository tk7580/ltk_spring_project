package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.dto.RateRequestDto;
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
@RequestMapping("/member/activity")
public class UserActivityController {

    private final UserActivityService userActivityService;
    private final MemberRepository memberRepository;

    private Member getCurrentUser(Principal principal) {
        if (principal == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }
        return memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자 정보를 찾을 수 없습니다."));
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/work/{workId}/wishlist")
    @ResponseBody
    public ResponseEntity<String> addWishlist(@PathVariable Long workId, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        boolean isSuccess = userActivityService.addWorkToWishlist(currentUser.getId(), workId);

        if (isSuccess) {
            return ResponseEntity.ok("찜하기가 완료되었습니다.");
        } else {
            return ResponseEntity.status(HttpStatus.CONFLICT).body("이미 찜 목록에 있는 작품입니다.");
        }
    }

    @PreAuthorize("isAuthenticated()")
    @DeleteMapping("/work/{workId}/wishlist")
    @ResponseBody
    public ResponseEntity<String> removeWishlist(@PathVariable Long workId, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        boolean isSuccess = userActivityService.removeWorkFromWishlist(currentUser.getId(), workId);

        if (isSuccess) {
            return ResponseEntity.ok("찜하기가 취소되었습니다.");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("찜 목록에 없는 작품입니다.");
        }
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/work/{workId}/watch")
    @ResponseBody
    public ResponseEntity<String> markAsWatched(@PathVariable Long workId, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        userActivityService.markWorkAsWatched(currentUser.getId(), workId);
        return ResponseEntity.ok("시청 완료 처리되었습니다.");
    }

    @PreAuthorize("isAuthenticated()")
    @DeleteMapping("/work/{workId}/watch")
    @ResponseBody
    public ResponseEntity<String> cancelWatch(@PathVariable Long workId, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        boolean isSuccess = userActivityService.cancelWorkWatch(currentUser.getId(), workId);
        if (isSuccess) {
            return ResponseEntity.ok("시청 완료를 취소했습니다.");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("시청 기록이 없는 작품입니다.");
        }
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/work/{workId}/rate")
    @ResponseBody
    public ResponseEntity<String> rateWork(@PathVariable Long workId,
                                           @RequestBody RateRequestDto rateRequest,
                                           Principal principal) {
        Member currentUser = getCurrentUser(principal);
        userActivityService.rateWork(currentUser.getId(), workId, rateRequest.getScore(), rateRequest.getComment());
        return ResponseEntity.ok("평점이 등록되었습니다.");
    }
}