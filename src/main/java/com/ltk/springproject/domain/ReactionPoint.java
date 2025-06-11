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
    private Long id; // Integer -> Long으로 변경

    @Column(name = "regDate", nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false)
    private LocalDateTime updateDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "memberId", nullable = false)
    private Member member;

    @Column(name = "relTypeCode", nullable = false, length = 50)
    private String relTypeCode;

    @Column(name = "relId", nullable = false)
    private Long relId; // Integer -> Long으로 변경 (Article, Reply의 ID가 Long이 되므로)

    @Column(name = "reactionType", nullable = false, length = 10)
    private String reactionType;

    @Column(name = "point", nullable = false)
    private Integer point;

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