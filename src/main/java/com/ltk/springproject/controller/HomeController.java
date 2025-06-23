package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.WorkService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.security.Principal;
import java.util.List;
import java.util.Optional;

@Controller
@RequiredArgsConstructor
public class HomeController {

    private final WorkService workService;
    private final MemberRepository memberRepository;

    @GetMapping("/")
    public String redirectToHome() {
        return "redirect:/home";
    }

    @GetMapping("/home")
    public String home(Model model, Principal principal) {
        if (principal != null) {
            Optional<Member> _member = memberRepository.findByLoginId(principal.getName());
            if (_member.isPresent()){
                model.addAttribute("currentUser", _member.get());
            }
        }

        // '전체(All)' 타입에 대해 '평점순(rating)'으로 정렬하는 새 메소드 호출
        List<Work> workList = workService.findWorksByCriteria("All", "rating");
        model.addAttribute("popularWorks", workList);

        return "home";
    }
}