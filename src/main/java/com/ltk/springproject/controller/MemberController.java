package com.ltk.springproject.controller;

import com.ltk.springproject.service.MemberService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import java.security.Principal; // Principal 클래스 임포트 추가

@Controller
@RequestMapping("/member")
public class MemberController {

    @Autowired
    private MemberService memberService;

    // 로그인 폼을 보여주는 메서드 추가
    @GetMapping("/login")
    public String showLoginForm(Principal principal) {
        // 이미 로그인된 사용자가 로그인 페이지에 접근하려고 할 때
        // 무한 리다이렉트를 방지하기 위해 홈으로 리다이렉트
        if (principal != null) {
            return "redirect:/"; // 이미 로그인된 상태면 홈으로 보냄
        }
        return "member/login"; // 로그인 폼 템플릿의 경로
    }

    @GetMapping("/joinForm")
    public String showJoinForm() {
        return "member/joinForm";
    }

    @PostMapping("/doJoin")
    @ResponseBody
    public String doJoin(
            @RequestParam("loginId") String loginId,
            @RequestParam("loginPw") String loginPw,
            @RequestParam("name") String name,
            @RequestParam("nickname") String nickname,
            @RequestParam("cellphoneNum") String cellphoneNum,
            @RequestParam("email") String email
    ) {
        try {
            int memberId = memberService.join(loginId, loginPw, name, nickname, cellphoneNum, email);
            return String.format("%d번 회원이 가입되었습니다!", memberId);
        } catch (Exception e) {
            return "회원 가입 실패: " + e.getMessage();
        }
    }
}