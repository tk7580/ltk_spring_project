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

    @Column(name = "regDate") // "reg_date" -> "regDate"
    private LocalDateTime regDate;

    @Column(name = "updateDate") // "update_date" -> "updateDate"
    private LocalDateTime updateDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "memberId") // "member_id" -> "memberId"
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "seriesId") // "series_id" -> "seriesId"
    private Series series;

    @Column(name = "title")
    private String title;

    @Lob
    @Column(name = "body")
    private String body;

    @Column(name = "hitCount") // "hit_count" -> "hitCount"
    private Integer hitCount;

    @Column(name = "goodReactionPoint") // "good_reaction_point" -> "goodReactionPoint"
    private Integer goodReactionPoint;

    @Column(name = "badReactionPoint") // "bad_reaction_point" -> "badReactionPoint"
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