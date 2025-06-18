package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "work_identifier")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkIdentifier {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(nullable = false)
    private LocalDateTime updateDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workId", nullable = false)
    private Work work;

    @Column(nullable = false, length = 50)
    private String sourceName; // 예: "TMDB_MOVIE", "ANILIST_ANIME"

    @Column(nullable = false)
    private String sourceId; // 예: "550"

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