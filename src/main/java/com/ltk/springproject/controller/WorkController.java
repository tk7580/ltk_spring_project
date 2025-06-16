package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Work;
import com.ltk.springproject.service.WorkService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.server.ResponseStatusException;

@Controller
@RequiredArgsConstructor
@RequestMapping("/work") // "/work"로 시작하는 모든 URL은 이 컨트롤러가 담당합니다.
public class WorkController {

    private final WorkService workService;

    /**
     * 작품 상세 페이지를 보여줍니다.
     * @param id URL 경로에서 받아온 작품의 ID
     * @param model 뷰에 데이터를 전달할 모델
     * @return 작품 상세 페이지 템플릿 경로
     */
    @GetMapping("/{id}")
    public String showWorkDetail(@PathVariable("id") Long id, Model model) {
        // 1. WorkService를 통해 작품 정보를 조회합니다.
        Work work = workService.findWorkById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "작품을 찾을 수 없습니다."));

        // 2. 조회된 Work 객체를 "work"라는 이름으로 모델에 담습니다.
        model.addAttribute("work", work);

        // 3. "work/detail.html" 템플릿을 사용자에게 보여줍니다.
        return "work/detail";
    }
}