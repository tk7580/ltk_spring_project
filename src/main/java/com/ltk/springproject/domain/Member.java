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
    private int delStatus;

    @Column(name = "delDate")
    private LocalDateTime delDate;

    // gender, birthDate 필드는 DB에 없으므로 엔티티에서도 제외하거나,
    // DDL에 추가한 후 @Column 어노테이션을 달아주어야 합니다.
    // 현재는 DDL 기준으로 제외했습니다.

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