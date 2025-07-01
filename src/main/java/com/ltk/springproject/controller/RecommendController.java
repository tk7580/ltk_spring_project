
package com.ltk.springproject.controller;

import com.ltk.springproject.service.RecommendService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class RecommendController {

    private final RecommendService recommendService;

    public RecommendController(RecommendService recommendService){
        this.recommendService = recommendService;
    }

    @GetMapping("/recommend/personal")
    public String personal(Model model){
        long memberId = 1L; // TODO: obtain from session
        model.addAttribute("recs", recommendService.getPersonal(memberId));
        return "recommend_personal";
    }
}
