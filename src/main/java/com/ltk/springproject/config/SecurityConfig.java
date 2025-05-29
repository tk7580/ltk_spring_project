package com.ltk.springproject.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager; // import 추가
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration; // import 추가
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /**
     * AuthenticationManager 빈을 등록합니다.
     * Spring Security의 인증 처리를 담당하며, UserDetailsService와 BCryptPasswordEncoder를 연결합니다.
     */
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // CSRF 비활성화 (개발 편의상, 실제 운영에서는 CSRF 공격 방지를 위해 활성화 권장)
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(authorize -> authorize
                        // 다음 경로들은 인증 없이 접근 허용
                        .requestMatchers(
                                "/member/joinForm",     // 회원가입 폼
                                "/member/doJoin",       // 회원가입 처리 (POST 요청)
                                "/member/login",        // 로그인 폼
                                "/",                    // 홈 페이지 (기본 인덱스 페이지)
                                "/css/**",              // CSS 파일
                                "/js/**",               // JavaScript 파일
                                "/images/**",           // 이미지 파일
                                "/favicon.ico"          // 파비콘
                        ).permitAll()
                        // 그 외 모든 요청은 인증 필요
                        .anyRequest().authenticated()
                )
                .formLogin(formLogin -> formLogin
                        .loginPage("/member/login")     // 로그인 페이지 경로
                        .defaultSuccessUrl("/", true)   // 로그인 성공 후 리다이렉트될 기본 URL, true는 항상 이 경로로 리다이렉트
                        .permitAll()                    // 로그인 폼 관련 경로도 permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")                   // 로그아웃 처리 URL
                        .logoutSuccessUrl("/member/login?logout") // 로그아웃 성공 후 로그인 페이지로 이동
                        .permitAll()                            // 로그아웃 관련 경로도 permitAll()
                );
        return http.build();
    }
}