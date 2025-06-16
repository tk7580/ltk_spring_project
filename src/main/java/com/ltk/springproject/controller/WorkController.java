package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.UserActivityService;
import com.ltk.springproject.service.WorkService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.server.ResponseStatusException;

import java.security.Principal;

@Controller
@RequiredArgsConstructor
@RequestMapping("/work")
public class WorkController {

    private final WorkService workService;
    private final UserActivityService userActivityService;
    private final MemberRepository memberRepository;

    @GetMapping("/{id}")
    public String showWorkDetail(@PathVariable("id") Long id, Model model, Principal principal) {
        Work work = workService.findWorkById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "작품을 찾을 수 없습니다."));
        model.addAttribute("work", work);

        boolean isWishlisted = false;
        if (principal != null) {
            memberRepository.findByLoginId(principal.getName()).ifPresent(member -> {
                model.addAttribute("currentUser", member);
            });

            // 위에서 찾은 member 객체 또는 principal을 통해 memberId를 가져와야 합니다.
            // 여기서는 principal.getName()으로 loginId를 가져와 다시 member를 찾는 대신,
            // Member 객체를 한번만 조회하도록 로직을 개선하는 것이 좋습니다.
            // 하지만 지금은 에러 해결에 집중하기 위해, isWishlisted 확인 로직을 아래와 같이 수정합니다.
            Member member = memberRepository.findByLoginId(principal.getName()).orElse(null);
            if (member != null) {
                isWishlisted = userActivityService.isWorkWishlisted(member.getId(), id);
            }
        }
        model.addAttribute("isWishlisted", isWishlisted);

        return "work/detail";
    }
}