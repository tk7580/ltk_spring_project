package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Work;
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

/**
 * 회원 관련 요청(로그인, 회원가입, 마이페이지 등)을 처리하는 컨트롤러
 */
@Controller
@RequestMapping("/member") // 이 컨트롤러의 모든 메소드는 /member 로 시작하는 URL에 매핑됩니다.
@RequiredArgsConstructor // final 필드에 대한 생성자를 자동으로 만들어주는 Lombok 어노테이션
public class MemberController {

    // final: 이 컨트롤러가 생성될 때 반드시 주입되어야 함을 의미 (생성자 주입)
    private final MemberService memberService; // 회원가입 등 핵심 로직을 처리하는 서비스
    private final AuthenticationManager authenticationManager; // Spring Security의 인증을 처리하는 관리자
    private final UserActivityService userActivityService; // 사용자의 활동(찜하기 등) 관련 서비스
    private final MemberRepository memberRepository; // DB에서 회원 정보를 직접 조회하기 위한 리포지토리

    /**
     * 로그인 페이지를 보여주는 메소드
     * @param principal Spring Security가 현재 로그인한 사용자의 정보를 담아주는 객체
     * @return 보여줄 뷰(html)의 경로
     */
    @GetMapping("/login")
    public String showLoginForm(Principal principal) {
        // 만약 principal 객체가 존재한다면, 이미 로그인한 상태이므로 홈 화면으로 리다이렉트
        if (principal != null) {
            return "redirect:/";
        }
        // 로그인하지 않은 상태라면, 로그인 폼 페이지를 보여줌
        return "member/login";
    }

    /**
     * 회원가입 페이지를 보여주는 메소드
     */
    @GetMapping("/joinForm")
    public String showJoinForm() {
        return "member/joinForm";
    }

    /**
     * 회원가입 폼에서 POST 방식으로 들어온 요청을 처리하는 메소드
     * @param loginId      폼에서 name="loginId"로 넘어온 값
     * @param loginPw      폼에서 name="loginPw"로 넘어온 값
     * @param redirectAttributes 리다이렉트 시 일회성 메시지를 전달하기 위한 객체
     * @return 처리가 끝난 후 리다이렉트할 URL
     */
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
            // 1. 회원가입 로직 실행 (DB에 사용자 정보 저장)
            memberService.join(loginId, loginPw, name, nickname, cellphoneNum, email);

            // 2. 회원가입 성공 시, 해당 정보로 즉시 자동 로그인 처리
            UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken(loginId, loginPw);
            Authentication authentication = authenticationManager.authenticate(token);
            SecurityContextHolder.getContext().setAuthentication(authentication);

            // 3. 리다이렉트된 페이지에서 보여줄 일회성 성공 메시지 추가
            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다.");

            // 4. 모든 처리가 성공하면 홈 화면으로 리다이렉트
            return "redirect:/home";

        } catch (Exception e) {
            // 5. 회원가입 과정에서 오류 발생 시, 에러 메시지를 담아 다시 회원가입 폼으로 리다이렉트
            redirectAttributes.addFlashAttribute("error", "회원가입에 실패했습니다: " + e.getMessage());
            return "redirect:/member/joinForm";
        }
    }

    /**
     * '찜한 작품' 목록 페이지를 보여주는 메소드
     * @param model 뷰(html)에 데이터를 전달하기 위한 객체
     * @param principal 현재 로그인한 사용자 정보
     * @return 보여줄 뷰의 경로
     */
    @GetMapping("/wishlist")
    public String showWishlist(Model model, Principal principal) {
        // 로그인이 되어있지 않다면, 로그인 페이지로 보냄
        if (principal == null) {
            return "redirect:/member/login";
        }

        // Principal 객체에서 사용자 로그인 ID를 얻어, 전체 Member 객체를 조회
        Member member = memberRepository.findByLoginId(principal.getName())
                .orElseThrow(() -> new IllegalStateException("로그인한 사용자 정보를 찾을 수 없습니다."));

        // 조회된 사용자의 ID를 이용해, 해당 사용자가 찜한 작품 목록을 서비스에서 가져옴
        List<Work> wishlistedWorks = userActivityService.findWishlistedWorksByMemberId(member.getId());

        // 뷰(html)에서 헤더 부분 등을 올바르게 표시하기 위해, 현재 사용자 정보를 모델에 담아줌
        model.addAttribute("currentUser", member);
        // 뷰(html)에서 찜한 작품 목록을 사용하기 위해, 조회된 목록을 모델에 담아줌
        model.addAttribute("wishlistedWorks", wishlistedWorks);

        // 'templates/member/wishlist.html' 파일을 렌더링하여 사용자에게 보여줌
        return "member/wishlist";
    }
}