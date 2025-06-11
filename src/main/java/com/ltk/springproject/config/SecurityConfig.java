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

    // ... (bCryptPasswordEncoder, authenticationManager 빈은 동일)

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(authorize -> authorize
                        // --- 여기를 수정합니다 ---
                        .requestMatchers(
                                "/home",                // "/" 에서 "/home" 으로 변경
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
                .formLogin(formLogin -> formLogin
                        .loginPage("/member/login")
                        // --- 여기도 수정합니다 ---
                        .defaultSuccessUrl("/home", true) // "/" 에서 "/home" 으로 변경
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