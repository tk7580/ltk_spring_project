package com.ltk.springproject.dto;

import java.util.List;

public class MyPageDto {
    private Long userId;
    private String username;
    private List<WorkDto> favorites;
    private List<WorkDto> watchHistory;

    // 기본 생성자
    public MyPageDto() {}

    // ─── getter / setter ────────────────────────────────────────────
    public Long getUserId() {
        return userId;
    }
    public void setUserId(Long userId) {
        this.userId = userId;
    }
    public String getUsername() {
        return username;
    }
    public void setUsername(String username) {
        this.username = username;
    }
    public List<WorkDto> getFavorites() {
        return favorites;
    }
    public void setFavorites(List<WorkDto> favorites) {
        this.favorites = favorites;
    }
    public List<WorkDto> getWatchHistory() {
        return watchHistory;
    }
    public void setWatchHistory(List<WorkDto> watchHistory) {
        this.watchHistory = watchHistory;
    }
}
