package com.ltk.springproject.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
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
    AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers(
                                "/",
                                "/home",
                                "/exam/**",
                                "/member/joinForm",
                                "/member/doJoin",
                                "/member/login",
                                "/css/**",
                                "/js/**",
                                "/images/**",
                                "/favicon.ico",
                                "/apple-touch-icon.png",
                                "/favicon-32x32.png",
                                "/favicon-16x16.png",
                                // ===== 아래 경로들을 permitAll()에 추가합니다 =====
                                "/chart/**",
                                "/works/**"
                                // ==========================================
                        ).permitAll()
                        .requestMatchers("/member/**").authenticated()
                        .anyRequest().authenticated()
                )
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
                .formLogin(formLogin -> formLogin
                        .loginPage("/member/login")
                        .defaultSuccessUrl("/home", true)
                        .permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/member/logout")
                        .logoutSuccessUrl("/")
                        .permitAll()
                );
        return http.build();
    }
}