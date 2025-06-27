package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.dto.ReactionRequestDto; // [수정] DTO 임포트
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.ReactionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*; // [수정] RequestBody 임포트
import org.springframework.web.server.ResponseStatusException;

import java.security.Principal;

@Controller
@RequestMapping("/reaction")
@RequiredArgsConstructor
public class ReactionController {

    private final ReactionService reactionService;
    private final MemberRepository memberRepository;

    /**
     * [수정] @RequestParam 대신 @RequestBody DTO를 사용하여 요청을 처리합니다.
     */
    @PreAuthorize("isAuthenticated()")
    @PostMapping("")
    @ResponseBody
    public ResponseEntity<String> doReaction(Principal principal, @RequestBody ReactionRequestDto reactionRequestDto) {

        Member member = memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "사용자 정보를 찾을 수 없습니다."));

        try {
            // DTO에서 데이터를 가져와 서비스 호출
            String resultMessage = reactionService.toggleReaction(
                    member,
                    reactionRequestDto.getRelTypeCode(),
                    reactionRequestDto.getRelId(),
                    reactionRequestDto.getReactionType()
            );
            return ResponseEntity.ok(resultMessage);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}