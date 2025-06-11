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

    // 이전에 추가했던 WorkService 주입 부분은 그대로 둡니다.
    private final WorkService workService;
    // TODO: 사용자 정보를 가져오기 위해 MemberService도 주입받아야 합니다.
    // private final MemberService memberService;

    // --- 여기를 수정합니다 ---
    @GetMapping("/home") // "/" 에서 "/home"으로 변경
    public String home(Model model, Principal principal) {
        if (principal != null) {
            // ... (로그인 사용자 정보 처리 로직은 그대로)
        }

        List<Work> workList = workService.findAllWorks();
        model.addAttribute("popularWorks", workList);

        return "home"; // "home.html" 템플릿을 사용하는 것은 그대로 유지
    }
}