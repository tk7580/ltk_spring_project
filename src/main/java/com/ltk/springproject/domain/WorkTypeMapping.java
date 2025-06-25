package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "work_type_mapping",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "UK_work_type_mapping_workId_typeId",
                        columnNames = {"workId", "typeId"}
                )
        }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkTypeMapping {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, updatable = false)
    private LocalDateTime regDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workId", nullable = false)
    private Work work;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "typeId", nullable = false)
    private WorkType workType;

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
    }
}