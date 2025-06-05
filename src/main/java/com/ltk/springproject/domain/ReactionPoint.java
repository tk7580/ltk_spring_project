package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import java.time.LocalDateTime;

@Entity
@Table(name = "reactionPoint")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReactionPoint {

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
    private String relTypeCode; // 예: "article", "reply"

    @Column(name = "relId", nullable = false)
    private Integer relId; // 관련 데이터의 ID (articleId 또는 replyId 등)

    @Column(name = "reactionType", nullable = false, length = 10)
    private String reactionType; // 예: "GOOD", "BAD"

    @Column(name = "point", nullable = false)
    private Integer point; // 예: 1 (GOOD), -1 (BAD)

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