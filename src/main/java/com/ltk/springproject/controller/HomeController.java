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
    private final MemberRepository memberRepository; // Member 정보를 가져오기 위해 주입

    @GetMapping("/")
    public String redirectToHome() {
        return "redirect:/home";
    }

    @GetMapping("/home")
    public String home(Model model, Principal principal) {
        // --- 이 부분이 추가/수정되었습니다 ---
        // 사용자가 로그인한 상태인지 확인
        if (principal != null) {
            // principal.getName()은 현재 로그인된 사용자의 ID(여기서는 loginId)를 반환합니다.
            String loginId = principal.getName();
            // loginId를 사용해 DB에서 전체 Member 정보를 찾아옵니다.
            Optional<Member> _member = memberRepository.findByLoginId(loginId);
            // Member 정보가 존재하면, "currentUser"라는 이름으로 Model에 담습니다.
            if (_member.isPresent()){
                model.addAttribute("currentUser", _member.get());
            }
        }
        // ---------------------------------

        List<Work> workList = workService.findAllWorks();
        model.addAttribute("popularWorks", workList);

        return "home";
    }
}