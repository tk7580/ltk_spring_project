package com.ltk.springproject.domain;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
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
public class Member implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
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
    @Builder.Default // [수정] 빌더 사용 시 기본값을 0으로 설정합니다.
    private int delStatus = 0; // [수정] 필드 자체에도 기본값을 할당하여 안정성을 높입니다.

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
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        List<GrantedAuthority> authorities = new ArrayList<>();
        authorities.add(new SimpleGrantedAuthority("ROLE_USER"));
        return authorities;
    }

    @Override
    public String getPassword() {
        return this.loginPw;
    }

    @Override
    public String getUsername() {
        return this.loginId;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return this.delStatus == 0;
    }
}