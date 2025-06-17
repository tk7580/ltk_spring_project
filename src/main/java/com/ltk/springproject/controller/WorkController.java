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
            Member member = memberRepository.findByLoginId(principal.getName()).orElse(null);
            if (member != null) {
                model.addAttribute("currentUser", member);
                isWishlisted = userActivityService.isWorkWishlisted(member.getId(), id);
            }
        }
        model.addAttribute("isWishlisted", isWishlisted);

        return "work/detail";
    }
}