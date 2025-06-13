package com.ltk.springproject.controller;

import com.ltk.springproject.service.MemberService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;

@Controller
@RequestMapping("/member")
@RequiredArgsConstructor
public class MemberController {

    private final MemberService memberService;
    private final AuthenticationManager authenticationManager; // 자동 로그인을 위해 주입

    @GetMapping("/login")
    public String showLoginForm(Principal principal) {
        if (principal != null) {
            return "redirect:/";
        }
        return "member/login";
    }

    @GetMapping("/joinForm")
    public String showJoinForm() {
        return "member/joinForm";
    }

    // ===== 회원가입 후 자동 로그인 및 팝업 기능 적용 =====
    @PostMapping("/doJoin")
    public String doJoin(
            @RequestParam("loginId") String loginId,
            @RequestParam("loginPw") String loginPw,
            @RequestParam("name") String name,
            @RequestParam("nickname") String nickname,
            @RequestParam("cellphoneNum") String cellphoneNum,
            @RequestParam("email") String email,
            RedirectAttributes redirectAttributes
    ) {
        try {
            // 1. 회원가입 실행
            memberService.join(loginId, loginPw, name, nickname, cellphoneNum, email);

            // 2. 가입된 정보로 자동 로그인 처리
            UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken(loginId, loginPw);
            Authentication authentication = authenticationManager.authenticate(token);
            SecurityContextHolder.getContext().setAuthentication(authentication);

            // 3. 리다이렉트 후 팝업으로 띄울 메시지 전달
            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다.");

            // 4. 홈 화면으로 리다이렉트
            return "redirect:/home";

        } catch (Exception e) {
            // 회원가입 실패 시, 실패 메시지와 함께 다시 가입 폼으로 리다이렉트
            redirectAttributes.addFlashAttribute("error", "회원가입에 실패했습니다: " + e.getMessage());
            return "redirect:/member/joinForm";
        }
    }
    // ===============================================
}