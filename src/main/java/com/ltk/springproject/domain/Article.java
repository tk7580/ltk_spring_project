package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "article")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Article {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "regDate", nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false)
    private LocalDateTime updateDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "memberId")
    private Member member;

    // ★★★ [수정] Series 와의 관계를 Work 와의 관계로 변경 ★★★
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workId")
    private Work work;

    @Column(name = "title")
    private String title;

    @Lob
    @Column(name = "body", columnDefinition = "TEXT")
    private String body;

    @Column(name = "hitCount")
    private Integer hitCount;

    @Column(name = "goodReactionPoint")
    private Integer goodReactionPoint;

    @Column(name = "badReactionPoint")
    private Integer badReactionPoint;

    @OneToMany(mappedBy = "article", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Reply> replies = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
        this.hitCount = 0;
        this.goodReactionPoint = 0;
        this.badReactionPoint = 0;
    }

    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }
}