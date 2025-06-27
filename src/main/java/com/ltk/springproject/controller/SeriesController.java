package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Series;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.SeriesService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import java.security.Principal;
import java.util.List; // [수정] List 임포트 추가

@Controller
@RequestMapping("/series")
@RequiredArgsConstructor
public class SeriesController {

    private final SeriesService seriesService;
    private final MemberRepository memberRepository;

    // [수정] 시리즈 목록 페이지를 처리하는 메소드 추가
    @GetMapping("")
    public String showSeriesList(Model model, Principal principal) {
        // 모든 시리즈 조회
        List<Series> seriesList = seriesService.findAll();
        model.addAttribute("seriesList", seriesList);

        // 현재 로그인한 사용자 정보 처리 (레이아웃에 필요)
        if (principal != null) {
            memberRepository.findByLoginId(principal.getName())
                    .ifPresent(member -> model.addAttribute("currentUser", member));
        }

        // 'templates/series/list.html' 뷰를 렌더링
        return "series/list";
    }

    @GetMapping("/{id}")
    public String showSeriesDetail(@PathVariable("id") Long id, Model model, Principal principal) {
        // SeriesService를 통해 ID에 해당하는 시리즈 정보 조회
        Series series = seriesService.findById(id);

        // 현재 로그인한 사용자 정보 처리 (레이아웃에 필요)
        if (principal != null) {
            memberRepository.findByLoginId(principal.getName())
                    .ifPresent(member -> model.addAttribute("currentUser", member));
        }

        // 모델에 시리즈 정보를 담아 뷰로 전달
        model.addAttribute("series", series);

        // 'templates/series/detail.html' 뷰를 렌더링
        return "series/detail";
    }
}