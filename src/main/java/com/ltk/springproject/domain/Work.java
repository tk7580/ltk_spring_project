package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "work")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Work {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "seriesId")
    private Series series;

    @Column(name = "regDate")
    private LocalDateTime regDate;

    @Column(name = "updateDate")
    private LocalDateTime updateDate;

    @Column(name = "titleKr")
    private String titleKr;

    @Column(name = "titleOriginal")
    private String titleOriginal;

    @Column(name = "type")
    private String type;

    @Column(name = "releaseDate")
    private LocalDate releaseDate;

    @Column(name = "releaseSequence")
    private Integer releaseSequence;

    @Column(name = "timelineSequence")
    private Integer timelineSequence;

    // --- 여기를 수정합니다 ---
    @Column(name = "isCompleted")
    private Boolean isCompleted; // private boolean -> private Boolean

    @Lob
    @Column(name = "description")
    private String description;

    @Column(name = "thumbnailUrl")
    private String thumbnailUrl;

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }
}