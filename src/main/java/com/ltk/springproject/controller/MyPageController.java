package com.example.ltkspring.controller;

import com.example.ltkspring.dto.MyPageDto;
import com.example.ltkspring.dto.WorkDto;
import com.example.ltkspring.model.User;
import com.example.ltkspring.service.RecommendationService;
import com.example.ltkspring.service.UserService;
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

    /**
     * 로그인된 사용자의 마이페이지 정보(즐겨찾기, 시청 기록 등)를 반환합니다.
     */
    @GetMapping("/mypage")
    public ResponseEntity<MyPageDto> getMyPage(@AuthenticationPrincipal User user) {
        MyPageDto dto = userService.buildMyPage(user.getId());
        return ResponseEntity.ok(dto);
    }

    /**
     * 로그인된 사용자를 위한 추천 작품 목록을 반환합니다.
     */
    @GetMapping("/recommendations")
    public ResponseEntity<List<WorkDto>> getRecommendations(@AuthenticationPrincipal User user) {
        List<WorkDto> list = recommendationService.recommendFor(user.getId());
        return ResponseEntity.ok(list);
    }
}
