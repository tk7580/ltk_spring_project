package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.WorkService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.security.Principal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/works")
@RequiredArgsConstructor
public class WorkListController {

    private final WorkService workService;
    private final MemberRepository memberRepository;

    // DB에 저장된 영문 타입명과 화면에 표시할 한글명 매핑
    private static final Map<String, String> typeDisplayNames = Map.of(
            "Movie", "영화",
            "Animation", "애니메이션",
            "Drama", "드라마",
            "Live-Action", "실사"
    );

    @GetMapping("")
    public String showListPage(
            @RequestParam(name = "type", required = false, defaultValue = "All") String type,
            @RequestParam(name = "sortBy", required = false, defaultValue = "newest") String sortBy,
            Model model,
            Principal principal
    ) {
        if (principal != null) {
            memberRepository.findByLoginId(principal.getName())
                    .ifPresent(member -> model.addAttribute("currentUser", member));
        }

        List<Work> works = workService.findWorksByCriteria(type, sortBy);
        model.addAttribute("works", works);

        // [수정] DB의 work_type에 있는 모든 타입을 가져옴
        List<String> workTypes = workService.findAllWorkTypes();
        model.addAttribute("workTypes", workTypes);

        // [수정] 필터링과 페이지 제목에 사용할 한글 타입명 맵을 모델에 추가
        model.addAttribute("typeDisplayNames", typeDisplayNames);

        model.addAttribute("selectedType", type);
        model.addAttribute("selectedSortBy", sortBy);

        // [수정] pageTitle 로직을 Map을 사용하여 더 유연하게 변경
        String pageTitle = typeDisplayNames.getOrDefault(type, "전체 작품");
        model.addAttribute("pageTitle", pageTitle);

        return "work/list";
    }
}