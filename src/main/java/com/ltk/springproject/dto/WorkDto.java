package com.example.ltkspring.dto;

public class WorkDto {
    private Long id;
    private String title;
    private String description;
    private Double averageScore;

    // fromEntity 메소드 예시
    public static WorkDto fromEntity(Work w) {
        WorkDto dto = new WorkDto();
        dto.setId(w.getId());
        dto.setTitle(w.getTitle());
        dto.setDescription(w.getDescription());
        dto.setAverageScore(w.getAverageScore());
        return dto;
    }
    // getter/setter
}
