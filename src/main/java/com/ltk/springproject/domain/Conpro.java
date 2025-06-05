package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

@Entity
@Table(name = "conpro")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Conpro {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", nullable = false, updatable = false)
    private Integer id; // INT(10) UNSIGNED

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "workId", nullable = false)
    private Work work;

    @Column(name = "providerType", nullable = false, length = 50)
    private String providerType;

    @Column(name = "providerName", nullable = false, length = 100)
    private String providerName;

    @Column(name = "contentUrl", length = 255)
    private String contentUrl;

    @Column(name = "appScheme", length = 255)
    private String appScheme;

    @Lob
    @Column(name = "additionalInfo", columnDefinition = "TEXT")
    private String additionalInfo;

    // Conpro는 보통 regDate, updateDate가 필요 없을 수 있으나, 필요하다면 추가 가능
}