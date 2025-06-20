package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "work_genre",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "UK_work_genre_workId_genreId",
                        columnNames = {"workId", "genreId"}
                )
        }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkGenre {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, updatable = false)
    private LocalDateTime regDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workId", nullable = false)
    private Work work;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "genreId", nullable = false)
    private Genre genre;

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
    }
}