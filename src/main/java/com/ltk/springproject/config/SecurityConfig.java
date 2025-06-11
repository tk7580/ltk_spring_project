package com.ltk.springproject.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.header.writers.ContentSecurityPolicyHeaderWriter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers(
                                "/", // 루트 경로도 허용
                                "/home",
                                "/member/joinForm",
                                "/member/doJoin",
                                "/member/login",
                                "/css/**",
                                "/js/**",
                                "/images/**",
                                "/favicon.ico"
                        ).permitAll()
                        .anyRequest().authenticated()
                )
                // --- 이 부분을 추가하여 콘텐츠 보안 정책(CSP)을 설정합니다 ---
                .headers(headers -> headers
                        .addHeaderWriter(new ContentSecurityPolicyHeaderWriter(
                                "default-src 'self';" +
                                        " script-src 'self' 'unsafe-inline';" +
                                        " style-src 'self' 'unsafe-inline';" +
                                        " img-src 'self' https://image.tmdb.org data:;" +
                                        " frame-src 'none';" +
                                        " object-src 'none';"
                        ))
                )
                // --------------------------------------------------------
                .formLogin(formLogin -> formLogin
                        .loginPage("/member/login")
                        .defaultSuccessUrl("/home", true)
                        .permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/member/login?logout")
                        .permitAll()
                );
        return http.build();
    }
}