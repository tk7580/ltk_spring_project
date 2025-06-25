package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

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

    @Column(name = "isOriginal")
    private Boolean isOriginal;

    @Column(name = "releaseDate")
    private LocalDate releaseDate;

    @Column(name = "watchedCount")
    private Integer watchedCount;

    @Column(name = "averageRating")
    private Double averageRating;

    @Column(name = "ratingCount")
    private Integer ratingCount;

    @Column(name = "episodes")
    private Integer episodes;

    @Column(name = "duration")
    private Integer duration;

    @Column(name = "creators")
    private String creators;

    @Column(name = "studios")
    private String studios;

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

    @Column(name = "trailerUrl")
    private String trailerUrl;

    @OneToMany(mappedBy = "work", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<WorkIdentifier> identifiers = new ArrayList<>();

    @OneToMany(mappedBy = "work", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<WorkGenre> workGenres = new ArrayList<>();

    @OneToMany(mappedBy = "work", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private Set<WorkTypeMapping> workTypeMappings = new HashSet<>();


    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
        this.watchedCount = 0;
        this.ratingCount = 0;
        this.averageRating = 0.0;
    }

    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }
}