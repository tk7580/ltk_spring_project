package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
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
@RequestMapping("/chart")
@RequiredArgsConstructor
public class ChartController {

    private final WorkService workService;
    private final MemberRepository memberRepository;

    @GetMapping("")
    public String showChartPage(
            @RequestParam(name = "type", required = false, defaultValue = "All") String type,
            @RequestParam(name = "sortBy", required = false, defaultValue = "rating") String sortBy,
            Model model,
            Principal principal
    ) {
        if (principal != null) {
            memberRepository.findByLoginId(principal.getName())
                    .ifPresent(member -> model.addAttribute("currentUser", member));
        }

        List<Work> works = workService.findWorksForChart(type, sortBy);
        model.addAttribute("works", works);

        List<String> workTypes = workService.findAllWorkTypes();
        model.addAttribute("workTypes", workTypes);

        model.addAttribute("selectedType", type);
        model.addAttribute("selectedSortBy", sortBy);

        return "chart/index";
    }
}