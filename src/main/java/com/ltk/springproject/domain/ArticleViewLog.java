package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(
        name = "article_view_log",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "UK_memberId_articleId",
                        columnNames = {"memberId", "articleId"}
                )
        }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ArticleViewLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "memberId", nullable = false)
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "articleId", nullable = false)
    private Article article;

    @Column(nullable = false, updatable = false)
    private LocalDateTime regDate;

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
    }
}