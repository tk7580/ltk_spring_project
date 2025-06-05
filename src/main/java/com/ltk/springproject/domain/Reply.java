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
@Table(name = "reply")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Reply {

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

    @Column(name = "relTypeCode", nullable = false, length = 50)
    private String relTypeCode; // 이 경우 항상 "article"

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "relId", nullable = false) // article.id 참조
    private Article article;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parentId") // 자기 자신을 참조 (부모 댓글 ID)
    private Reply parent;

    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @Builder.Default
    private List<Reply> children = new ArrayList<>(); // 자식 댓글들

    @Lob
    @Column(name = "body", nullable = false, columnDefinition = "TEXT")
    private String body;

    @Column(name = "goodReactionPoint", nullable = false)
    private Integer goodReactionPoint; // INT(10) UNSIGNED, DB DEFAULT 0

    @Column(name = "badReactionPoint", nullable = false)
    private Integer badReactionPoint; // INT(10) UNSIGNED, DB DEFAULT 0

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
        this.goodReactionPoint = 0;
        this.badReactionPoint = 0;
        if (this.relTypeCode == null) { // 기본값 설정
            this.relTypeCode = "article";
        }
    }

    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }

    // 양방향 연관관계 편의 메소드 (자식 댓글)
    public void addChildReply(Reply child) {
        this.children.add(child);
        if (child.getParent() != this) {
            child.setParent(this);
        }
    }
}