package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
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
    @Column(name = "id", nullable = false, updatable = false)
    private Integer id; // DB DDL에서 INT(10) UNSIGNED 이므로 Integer 사용

    @Column(name = "regDate", nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false)
    private LocalDateTime updateDate;

    @Column(name = "titleKr", nullable = false, length = 255)
    private String titleKr;

    @Column(name = "titleOriginal", length = 255)
    private String titleOriginal;

    @Lob // TEXT 타입 매핑 시 @Lob을 사용하는 것이 일반적입니다.
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "thumbnailUrl", length = 255)
    private String thumbnailUrl;

    @Column(name = "coverImageUrl", length = 255)
    private String coverImageUrl;

    @Column(name = "author", length = 100)
    private String author;

    // Series와 Work 간의 관계 (1:N)
    // Series가 삭제되면 관련된 Work도 함께 삭제 (CascadeType.ALL)
    // mappedBy는 Work 엔티티에서 Series를 참조하는 필드명으로 가정 (예: private Series series;)
    @OneToMany(mappedBy = "series", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default // Lombok Builder 사용 시 초기화 보장
    private List<Work> works = new ArrayList<>();

    // Series와 Article 간의 관계 (1:N)
    // Series가 삭제되면 관련된 Article도 함께 삭제 (CascadeType.ALL)
    // mappedBy는 Article 엔티티에서 Series를 참조하는 필드명으로 가정 (예: private Series series;)
    @OneToMany(mappedBy = "series", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default // Lombok Builder 사용 시 초기화 보장
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

    // 양방향 연관관계 편의 메소드 (필요에 따라 추가)
    public void addWork(Work work) {
        this.works.add(work);
        if (work.getSeries() != this) { // 무한루프 방지
            work.setSeries(this);
        }
    }

    public void addArticle(Article article) {
        this.articles.add(article);
        if (article.getSeries() != this) { // 무한루프 방지
            article.setSeries(this);
        }
    }
}