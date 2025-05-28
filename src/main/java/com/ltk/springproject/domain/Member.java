package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder; // Builder 패턴을 사용하기 위해 Lombok Builder 어노테이션 추가
import java.time.LocalDateTime; // DATETIME 타입을 위해 LocalDateTime 임포트

@Entity // 이 클래스가 JPA 엔티티임을 나타냅니다.
@Table(name = "member") // 매핑될 데이터베이스 테이블 이름
@Getter // 모든 필드의 Getter 메서드를 자동으로 생성합니다.
@Setter // 모든 필드의 Setter 메서드를 자동으로 생성합니다.
@NoArgsConstructor // 기본 생성자를 자동으로 생성합니다. (JPA에서 필요)
@AllArgsConstructor // 모든 필드를 인자로 받는 생성자를 자동으로 생성합니다.
@Builder // Builder 패턴을 사용하여 객체 생성을 유연하게 합니다.
public class Member {

    @Id // 기본 키(Primary Key)를 나타냅니다.
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 기본 키 값이 자동으로 생성되도록 합니다.
    @Column(name = "id", nullable = false, updatable = false) // '회원 고유 번호'
    private Long id; // SQL의 INT(10) UNSIGNED는 Java의 Long으로 매핑하는 것이 안전합니다.

    @Column(name = "regDate", nullable = false, updatable = false) // '회원 가입 날짜'
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false) // '회원 정보 최종 수정 날짜'
    private LocalDateTime updateDate;

    @Column(name = "loginId", nullable = false, unique = true, length = 30) // '로그인 아이디'
    private String loginId;

    @Column(name = "loginPw", nullable = false, length = 100) // '로그인 비밀번호'
    private String loginPw;

    @Column(name = "authLevel", nullable = false) // '권한 레벨 (3=일반, 7=관리자)'
    private Integer authLevel; // SQL의 SMALLINT(2) UNSIGNED는 Java의 Integer로 매핑합니다.

    @Column(name = "name", nullable = false, length = 20) // '회원 이름'
    private String name;

    @Column(name = "nickname", nullable = false, unique = true, length = 20) // '회원 닉네임'
    private String nickname;

    @Column(name = "cellphoneNum", nullable = false, length = 20) // '휴대폰 번호'
    private String cellphoneNum;

    @Column(name = "email", nullable = false, length = 50) // '이메일 주소'
    private String email;

    @Column(name = "delStatus", nullable = false) // '탈퇴 여부 (0=탈퇴 전, 1=탈퇴 후)'
    private Boolean delStatus; // TINYINT(1)은 Java의 Boolean으로 매핑할 수 있습니다. (0=false, 1=true)

    @Column(name = "delDate") // '탈퇴 날짜', NULLable 이므로 nullable=true 생략 가능
    private LocalDateTime delDate;

    // 엔티티가 영속화되기 전에 호출되어 regDate와 updateDate를 자동으로 설정
    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
        // delStatus는 기본값이 0 (false)이므로 별도 설정 필요 없음
        if (this.authLevel == null) { // authLevel의 기본값이 3이므로 null일 경우 설정
            this.authLevel = 3;
        }
        if (this.delStatus == null) { // delStatus의 기본값이 0 (false)이므로 null일 경우 설정
            this.delStatus = false;
        }
    }

    // 엔티티가 업데이트되기 전에 호출되어 updateDate를 자동으로 설정
    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }
}