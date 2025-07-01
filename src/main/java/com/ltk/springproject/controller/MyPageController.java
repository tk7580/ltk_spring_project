// src/main/java/com/ltk/springproject/controller/MyPageController.java
package com.ltk.springproject.controller;

import com.ltk.springproject.dto.MyPageDto;
import com.ltk.springproject.dto.WorkDto;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.service.UserService;
import com.ltk.springproject.service.RecommendationService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
public class MyPageController {
    private final UserService userService;
    private final RecommendationService recommendationService;

    public MyPageController(UserService userService, RecommendationService recommendationService) {
        this.userService = userService;
        this.recommendationService = recommendationService;
    }

    @GetMapping("/mypage")
    public ResponseEntity<MyPageDto> getMyPage(@AuthenticationPrincipal Member member) {
        MyPageDto dto = userService.buildMyPage(member.getId());
        return ResponseEntity.ok(dto);
    }

    @GetMapping("/recommendations")
    public ResponseEntity<List<WorkDto>> getRecommendations(@AuthenticationPrincipal Member member) {
        List<WorkDto> recommendations = recommendationService.recommendFor(member.getId());
        return ResponseEntity.ok(recommendations);
    }
}