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

@Controller
@RequestMapping("/works")
@RequiredArgsConstructor
public class WorkListController {

    private final WorkService workService;
    private final MemberRepository memberRepository;

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

        List<String> workTypes = workService.findAllWorkTypes();
        model.addAttribute("workTypes", workTypes);

        model.addAttribute("selectedType", type);
        model.addAttribute("selectedSortBy", sortBy);

        // ==========================================================
        // ★★★ 페이지 제목 생성 로직 수정 ★★★
        // ==========================================================
        String pageTitle;
        switch (type.toLowerCase()) { // 소문자로 변경하여 비교
            case "animation":
                pageTitle = "애니메이션";
                break;
            case "movie":
                pageTitle = "영화";
                break;
            case "tv":
                pageTitle = "TV 시리즈";
                break;
            default: // "All" 또는 기타
                pageTitle = "전체 작품";
                break;
        }
        model.addAttribute("pageTitle", pageTitle);
        // ==========================================================

        return "work/list";
    }
}