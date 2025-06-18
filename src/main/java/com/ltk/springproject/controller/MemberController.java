package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Work;
import com.ltk.springproject.dto.WatchedWorkDto;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.MemberService;
import com.ltk.springproject.service.UserActivityService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;
import java.util.List;

@Controller
@RequestMapping("/member")
@RequiredArgsConstructor
public class MemberController {

    private final MemberService memberService;
    private final AuthenticationManager authenticationManager;
    private final UserActivityService userActivityService;
    private final MemberRepository memberRepository;

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
            memberService.join(loginId, loginPw, name, nickname, cellphoneNum, email);

            UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken(loginId, loginPw);
            Authentication authentication = authenticationManager.authenticate(token);
            SecurityContextHolder.getContext().setAuthentication(authentication);

            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다.");
            return "redirect:/home";

        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "회원가입에 실패했습니다: " + e.getMessage());
            return "redirect:/member/joinForm";
        }
    }

    @GetMapping("/wishlist")
    public String showWishlist(Model model, Principal principal) {
        if (principal == null) {
            return "redirect:/member/login";
        }
        Member member = memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new IllegalStateException("로그인한 사용자 정보를 찾을 수 없습니다."));

        List<Work> wishlistedWorks = userActivityService.findWishlistedWorksByMemberId(member.getId());

        model.addAttribute("currentUser", member);
        model.addAttribute("wishlistedWorks", wishlistedWorks);

        return "member/wishlist";
    }

    @GetMapping("/watched")
    public String showWatchedList(Model model, Principal principal) {
        if (principal == null) {
            return "redirect:/member/login";
        }
        Member member = memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new IllegalStateException("로그인한 사용자 정보를 찾을 수 없습니다."));

        List<WatchedWorkDto> watchedWorks = userActivityService.findWatchedWorksByMemberId(member.getId());

        model.addAttribute("currentUser", member);
        model.addAttribute("watchedWorks", watchedWorks);

        return "member/watched";
    }
}