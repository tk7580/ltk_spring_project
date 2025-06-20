package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

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

    @Column(name = "isCompleted")
    private Boolean isCompleted;

    @Lob
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "thumbnailUrl")
    private String thumbnailUrl;

    @OneToMany(mappedBy = "work", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<WorkIdentifier> identifiers = new ArrayList<>();

    // ===== WorkGenre 와의 관계 추가 =====
    @OneToMany(mappedBy = "work", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<WorkGenre> workGenres = new ArrayList<>();
    // =====================================

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