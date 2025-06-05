package com.ltk.springproject.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model; // <<-- Model 인터페이스 import 추가
import org.springframework.web.bind.annotation.GetMapping;

import java.security.Principal; // <<-- Principal 인터페이스 import 추가

@Controller
public class HomeController {

    // TODO: 실제 데이터 로딩을 위해 필요한 서비스들을 주입받으세요.
    // 예시: private final WorkService workService;
    // 예시: private final MemberService memberService;
    // public HomeController(WorkService workService, MemberService memberService) {
    //     this.workService = workService;
    //     this.memberService = memberService;
    // }

    @GetMapping("/")
    public String home(Model model, Principal principal) { // Model과 Principal 파라미터 추가
        if (principal != null) {
            // 현재 로그인한 사용자의 아이디 (loginId)
            String loginId = principal.getName();

            // TODO: MemberService를 사용하여 사용자 닉네임 또는 전체 Member 객체 조회
            // 예시: Member currentUser = memberService.findByLoginId(loginId);
            // if (currentUser != null) {
            //     model.addAttribute("currentUser", currentUser); // Thymeleaf에서 사용할 수 있도록 모델에 추가
            //     // 예시: 사용자 맞춤 추천 작품 목록 로드
            //     // model.addAttribute("recommendedWorks", workService.getRecommendedWorksForUser(currentUser));
            // }
        }

        // TODO: WorkService 등을 사용하여 인기 작품, 최신 작품 목록 로드
        // 예시: model.addAttribute("popularWorks", workService.getPopularWorks());
        // 예시: model.addAttribute("newWorks", workService.getNewWorks());

        return "home"; // templates/home.html 을 반환 (이전에 index 였던 것을 home으로 변경)
    }
}