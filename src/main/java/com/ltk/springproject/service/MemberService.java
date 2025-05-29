package com.ltk.springproject.service;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.repository.MemberRepository;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime; // LocalDateTime 임포트 추가

@Service
@Transactional
public class MemberService {

    private final MemberRepository memberRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    public MemberService(MemberRepository memberRepository, BCryptPasswordEncoder bCryptPasswordEncoder) {
        this.memberRepository = memberRepository;
        this.bCryptPasswordEncoder = bCryptPasswordEncoder;
    }

    public int join(String loginId, String loginPw, String name, String nickname, String cellphoneNum, String email) {
        // 비밀번호 암호화
        String encodedLoginPw = bCryptPasswordEncoder.encode(loginPw);
        LocalDateTime now = LocalDateTime.now(); // 현재 시간 가져오기

        Member newMember = Member.builder()
                .loginId(loginId)
                .loginPw(encodedLoginPw) // 암호화된 비밀번호 저장
                .name(name)
                .nickname(nickname)
                .cellphoneNum(cellphoneNum)
                .email(email)
                .authLevel(3) // 기본 권한 레벨 설정 (예시)
                .delStatus(0) // 탈퇴 상태 초기값 (예시)
                .regDate(now)    // <<-- regDate 직접 초기화
                .updateDate(now) // <<-- updateDate 직접 초기화
                .build();

        memberRepository.save(newMember);
        return newMember.getId().intValue();
    }
}