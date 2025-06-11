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

    @Column(name = "reg_date") // regDate -> reg_date
    private LocalDateTime regDate;

    @Column(name = "update_date") // updateDate -> update_date
    private LocalDateTime updateDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id") // memberId -> member_id
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "series_id") // seriesId -> series_id
    private Series series;

    @Column(name = "title")
    private String title;

    @Lob
    @Column(name = "body")
    private String body;

    @Column(name = "hit_count") // hitCount -> hit_count
    private Integer hitCount;

    @Column(name = "good_reaction_point") // goodReactionPoint -> good_reaction_point
    private Integer goodReactionPoint;

    @Column(name = "bad_reaction_point") // badReactionPoint -> bad_reaction_point
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