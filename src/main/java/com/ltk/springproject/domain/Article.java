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
@Table(name = "article")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Article {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", nullable = false, updatable = false)
    private Integer id; // INT(10) UNSIGNED

    @Column(name = "regDate", nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false)
    private LocalDateTime updateDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "memberId", nullable = false)
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "seriesId", nullable = false)
    private Series series;

    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Lob
    @Column(name = "body", nullable = false, columnDefinition = "TEXT")
    private String body;

    @Column(name = "hitCount", nullable = false)
    private Integer hitCount; // INT(10) UNSIGNED, DB DEFAULT 0

    @Column(name = "goodReactionPoint", nullable = false)
    private Integer goodReactionPoint; // INT(10) UNSIGNED, DB DEFAULT 0

    @Column(name = "badReactionPoint", nullable = false)
    private Integer badReactionPoint; // INT(10) UNSIGNED, DB DEFAULT 0

    // Article과 Reply 간의 관계 (1:N)
    @OneToMany(mappedBy = "article", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<Reply> replies = new ArrayList<>();

    // Article과 ReactionPoint 간의 관계 (1:N) - 만약 ReactionPoint가 Article에만 달린다면.
    // relTypeCode로 구분하므로, 여기서는 직접적인 @OneToMany를 걸기보다 ReactionPoint 쪽에서 Article을 참조.
    // 필요하다면 서비스 계층에서 관련 반응을 조회하는 로직 구현.

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

    // 양방향 연관관계 편의 메소드 (Reply)
    public void addReply(Reply reply) {
        this.replies.add(reply);
        if (reply.getArticle() != this) {
            reply.setArticle(this);
        }
    }
}