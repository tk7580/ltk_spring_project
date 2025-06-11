package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "series")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Series {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "regDate")
    private LocalDateTime regDate;

    @Column(name = "updateDate")
    private LocalDateTime updateDate;

    @Column(name = "titleKr")
    private String titleKr;

    @Column(name = "titleOriginal")
    private String titleOriginal;

    @Lob
    @Column(name = "description")
    private String description;

    @Column(name = "thumbnailUrl")
    private String thumbnailUrl;

    @Column(name = "coverImageUrl")
    private String coverImageUrl;

    @Column(name = "author")
    private String author;

    @OneToMany(mappedBy = "series", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Work> works = new ArrayList<>();

    @OneToMany(mappedBy = "series", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Article> articles = new ArrayList<>();

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