package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Work;
import com.ltk.springproject.service.WorkService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.security.Principal;
import java.util.List;

@Controller
@RequiredArgsConstructor
public class HomeController {

    private final WorkService workService;
    // TODO: 사용자 정보를 가져오기 위해 MemberService도 주입받아야 합니다.
    // private final MemberService memberService;

    // --- 이 메소드를 추가합니다 ---
    /**
     * 루트 URL("/") 접속 시 "/home"으로 리다이렉트합니다.
     */
    @GetMapping("/")
    public String redirectToHome() {
        return "redirect:/home";
    }

    @GetMapping("/home")
    public String home(Model model, Principal principal) {
        if (principal != null) {
            // ... (로그인 사용자 정보 처리 로직은 그대로)
        }

        List<Work> workList = workService.findAllWorks();
        model.addAttribute("popularWorks", workList);

        return "home";
    }
}