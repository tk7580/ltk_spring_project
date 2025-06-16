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
@RequestMapping("/work")
public class WorkController {

    private final WorkService workService;

    @GetMapping("/{id}")
    public String showWorkDetail(@PathVariable("id") Long id, Model model) {
        Work work = workService.findWorkById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "작품을 찾을 수 없습니다."));
        model.addAttribute("work", work);
        return "work/detail";
    }
}