package com.ltk.springproject.문제풀이; // 패키지 이름은 소문자로 시작하는 것이 일반적입니다.

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import java.time.LocalDateTime;

@Entity // 이 클래스가 JPA 엔티티임을 나타냅니다.
@Table(name = "product") // 매핑될 데이터베이스 테이블 이름
@Getter // 모든 필드의 Getter 메서드를 자동으로 생성합니다.
@Setter // 모든 필드의 Setter 메서드를 자동으로 생성합니다.
@NoArgsConstructor // 기본 생성자를 자동으로 생성합니다. (JPA에서 필요)
@AllArgsConstructor // 모든 필드를 인자로 받는 생성자를 자동으로 생성합니다.
@Builder // Builder 패턴을 사용하여 객체 생성을 유연하게 합니다.
public class Product { // 클래스 이름 수정: product -> Product

    @Id // 기본 키(Primary Key)를 나타냅니다.
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 기본 키 값이 자동으로 생성되도록 합니다.
    @Column(name = "id", nullable = false, updatable = false)
    private Long id;

    @Column(name = "name", nullable = false, length = 100) // 상품명, 필수, 길이 제한
    private String name;

    @Column(name = "price", nullable = false) // 가격, 필수. 숫자 타입이므로 length 불필요
    private int price; // int 또는 Integer 타입으로 변경

    @Column(name = "stock", nullable = false) // 재고 수량, 필수. 숫자 타입이므로 length 불필러
    private int stock; // int 또는 Integer 타입으로 변경

    @Column(name = "created_at", nullable = false, updatable = false) // 생성일, DB 컬럼명 컨벤션 (snake_case)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false) // 수정일, DB 컬럼명 컨벤션 (snake_case)
    private LocalDateTime updatedAt;

    // 엔티티가 영속화되기 전에 호출되어 createdAt와 updatedAt를 자동으로 설정
    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now(); // 생성 시점의 updateAt도 현재 시간으로 설정
    }

    // 엔티티가 업데이트되기 전에 호출되어 updatedAt를 자동으로 설정
    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}