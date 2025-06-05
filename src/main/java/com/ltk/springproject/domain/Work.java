package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "work")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Work {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", nullable = false, updatable = false)
    private Integer id; // INT(10) UNSIGNED

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "seriesId", nullable = false)
    private Series series;

    @Column(name = "regDate", nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false)
    private LocalDateTime updateDate;

    @Column(name = "titleKr", nullable = false, length = 255)
    private String titleKr;

    @Column(name = "titleOriginal", length = 255)
    private String titleOriginal;

    @Column(name = "type", nullable = false, length = 50)
    private String type;

    @Column(name = "releaseDate")
    private LocalDate releaseDate; // DATE 타입

    @Column(name = "releaseSequence") // NULL 허용
    private Integer releaseSequence; // INT(10) UNSIGNED

    @Column(name = "timelineSequence") // NULL 허용
    private Integer timelineSequence; // INT(10) UNSIGNED

    @Column(name = "isCompleted") // TINYINT(1) UNSIGNED, DB DEFAULT 0
    private boolean isCompleted; // boolean으로 매핑 (0 or 1)

    @Lob
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    // Work와 Conpro 간의 관계 (1:N)
    @OneToMany(mappedBy = "work", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<Conpro> conpros = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
        // isCompleted는 DB에서 DEFAULT 0으로 처리되므로, 객체 생성 시 기본값은 false (Java boolean 기본값)
    }

    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }

    // 양방향 연관관계 편의 메소드
    public void addConpro(Conpro conpro) {
        this.conpros.add(conpro);
        if (conpro.getWork() != this) {
            conpro.setWork(this);
        }
    }

    // Series와의 관계 설정 편의 메소드 (단방향일 경우 Series쪽에서만 관리해도 무방)
    public void setSeries(Series series) {
        this.series = series;
        // 양방향일 경우 series.getWorks().add(this) 와 같은 코드 필요 (Series 엔티티에 addWork 메소드가 있다면 그걸 사용)
    }
}