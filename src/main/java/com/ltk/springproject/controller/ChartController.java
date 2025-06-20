package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Genre;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Work;
import com.ltk.springproject.repository.GenreRepository;
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

@Controller
@RequestMapping("/chart")
@RequiredArgsConstructor
public class ChartController {

    private final WorkService workService;
    private final GenreRepository genreRepository;
    private final MemberRepository memberRepository;

    @GetMapping("")
    public String showChartPage(
            @RequestParam(name = "type", required = false, defaultValue = "Movie") String type,
            @RequestParam(name = "sortBy", required = false, defaultValue = "rating") String sortBy,
            Model model,
            Principal principal
    ) {
        // 로그인한 사용자 정보 전달
        if (principal != null) {
            memberRepository.findByLoginId(principal.getName())
                    .ifPresent(member -> model.addAttribute("currentUser", member));
        }

        // 서비스 로직을 호출하여 작품 목록 조회
        List<Work> works = workService.findWorksForChart(type, sortBy);
        model.addAttribute("works", works);

        // 필터링 UI를 위해 전체 장르 목록 조회
        List<Genre> genres = genreRepository.findAll();
        model.addAttribute("genres", genres);

        // 현재 선택된 필터/정렬 값을 뷰로 전달하여 UI에 표시
        model.addAttribute("selectedType", type);
        model.addAttribute("selectedSortBy", sortBy);

        return "chart/index";
    }
}