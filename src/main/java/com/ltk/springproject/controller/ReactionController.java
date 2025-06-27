package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.ReactionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.server.ResponseStatusException;

import java.security.Principal;

@Controller
@RequestMapping("/reaction")
@RequiredArgsConstructor
public class ReactionController {

    private final ReactionService reactionService;
    private final MemberRepository memberRepository;

    /**
     * 게시글 또는 댓글에 대한 반응(좋아요/싫어요)을 처리하는 API
     * @param principal 현재 로그인한 사용자 정보
     * @param relTypeCode 반응을 남길 대상의 타입 ('article' 또는 'reply')
     * @param relId 대상의 고유 ID (게시글 ID 또는 댓글 ID)
     * @param reactionType 반응 종류 ('GOOD' 또는 'BAD')
     * @return 처리 결과 메시지를 담은 ResponseEntity 객체
     */
    @PreAuthorize("isAuthenticated()")
    @PostMapping("")
    @ResponseBody
    public ResponseEntity<String> doReaction(Principal principal,
                                             @RequestParam String relTypeCode,
                                             @RequestParam Long relId,
                                             @RequestParam String reactionType) {

        Member member = memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "사용자 정보를 찾을 수 없습니다."));

        try {
            String resultMessage = reactionService.toggleReaction(member, relTypeCode, relId, reactionType);
            return ResponseEntity.ok(resultMessage);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}