package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.springframework.security.core.GrantedAuthority; // import 추가
import org.springframework.security.core.authority.SimpleGrantedAuthority; // import 추가
import org.springframework.security.core.userdetails.UserDetails; // import 추가

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

@Entity
@Table(name = "member")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Member implements UserDetails { // UserDetails 인터페이스 구현

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", nullable = false, updatable = false)
    private Long id;

    @Column(name = "regDate", nullable = false, updatable = false)
    private LocalDateTime regDate;

    @Column(name = "updateDate", nullable = false)
    private LocalDateTime updateDate;

    @Column(name = "loginId", nullable = false, unique = true, length = 30)
    private String loginId;

    @Column(name = "loginPw", nullable = false, length = 100)
    private String loginPw;

    @Column(name = "authLevel", nullable = false)
    private Integer authLevel;

    @Column(name = "name", nullable = false, length = 20)
    private String name;

    @Column(name = "nickname", nullable = false, unique = true, length = 20)
    private String nickname;

    @Column(name = "cellphoneNum", nullable = false, length = 20)
    private String cellphoneNum;

    @Column(name = "email", nullable = false, length = 50)
    private String email;

    @Column(name = "delStatus", nullable = false)
    private int delStatus;

    @Column(name = "delDate")
    private LocalDateTime delDate;

    @PrePersist
    protected void onCreate() {
        this.regDate = LocalDateTime.now();
        this.updateDate = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updateDate = LocalDateTime.now();
    }

    // --- UserDetails 인터페이스 구현 메서드 ---

    /**
     * 계정이 가지고 있는 권한 목록을 리턴합니다. (예: ROLE_USER, ROLE_ADMIN)
     */
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        List<GrantedAuthority> authorities = new ArrayList<>();
        // 현재는 모든 사용자에게 "ROLE_USER" 권한을 부여합니다.
        // authLevel 필드를 사용하여 동적으로 권한을 부여할 수도 있습니다.
        // 예: if (this.authLevel == 7) authorities.add(new SimpleGrantedAuthority("ROLE_ADMIN"));
        authorities.add(new SimpleGrantedAuthority("ROLE_USER"));
        return authorities;
    }

    /**
     * 사용자의 비밀번호를 리턴합니다. (loginPw 필드 사용)
     */
    @Override
    public String getPassword() {
        return this.loginPw;
    }

    /**
     * 사용자의 고유 ID를 리턴합니다. (여기서는 loginId를 사용)
     */
    @Override
    public String getUsername() {
        return this.loginId;
    }

    /**
     * 계정 만료 여부를 리턴합니다. (true: 만료 안 됨)
     * 필요에 따라 만료 로직을 여기에 구현할 수 있습니다.
     */
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    /**
     * 계정 잠김 여부를 리턴합니다. (true: 잠기지 않음)
     * 필요에 따라 잠금 로직을 여기에 구현할 수 있습니다.
     */
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    /**
     * 비밀번호 만료 여부를 리턴합니다. (true: 만료 안 됨)
     * 필요에 따라 비밀번호 만료 로직을 여기에 구현할 수 있습니다.
     */
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    /**
     * 계정 활성화 여부를 리턴합니다. (true: 활성화 됨)
     * 탈퇴 여부(delStatus)를 활용하여 비활성화할 수 있습니다.
     * 예: return this.delStatus == 0;
     */
    @Override
    public boolean isEnabled() {
        return this.delStatus == 0; // delStatus가 0일 때만 활성화 (탈퇴하지 않았을 때)
    }
}