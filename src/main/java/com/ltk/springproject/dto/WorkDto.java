package com.ltk.springproject.dto;

import com.ltk.springproject.domain.Work;

public class WorkDto {
    private Long id;
    private String title;
    private String description;
    private Double averageScore;

    // 기본 생성자
    public WorkDto() {}

    /**
     * Work 엔티티를 DTO로 변환합니다.
     * title은 한글 제목 우선, 없으면 원제목을 사용합니다.
     */
    public static WorkDto fromEntity(Work w) {
        WorkDto dto = new WorkDto();
        dto.setId(w.getId());
        // 한글 제목이 있으면 사용, 없으면 원제목
        String koreanTitle = w.getTitleKr();
        dto.setTitle(koreanTitle != null && !koreanTitle.isEmpty()
                ? koreanTitle : w.getTitleOriginal());
        dto.setDescription(w.getDescription());
        // averageRating 필드를 averageScore로 매핑
        dto.setAverageScore(w.getAverageRating());
        return dto;
    }

    // ───────── getter / setter ─────────
    public Long getId() {
        return id;
    }
    public void setId(Long id) {
        this.id = id;
    }
    public String getTitle() {
        return title;
    }
    public void setTitle(String title) {
        this.title = title;
    }
    public String getDescription() {
        return description;
    }
    public void setDescription(String description) {
        this.description = description;
    }
    public Double getAverageScore() {
        return averageScore;
    }
    public void setAverageScore(Double averageScore) {
        this.averageScore = averageScore;
    }
}
