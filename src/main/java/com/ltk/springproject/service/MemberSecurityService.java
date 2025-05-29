package com.ltk.springproject.service;

import com.ltk.springproject.domain.Member; // Member 엔티티의 정확한 경로로 수정
import com.ltk.springproject.repository.MemberRepository;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service // 스프링 빈으로 등록
@Transactional(readOnly = true) // 읽기 전용 트랜잭션 설정
public class MemberSecurityService implements UserDetailsService { // UserDetailsService 인터페이스 구현

    private final MemberRepository memberRepository;

    // 생성자 주입 (Autowired 대신 권장)
    public MemberSecurityService(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }

    /**
     * 사용자 이름 (여기서는 loginId)으로 사용자 정보를 불러오는 핵심 메서드
     * Spring Security가 로그인 처리 시 이 메서드를 호출합니다.
     */
    @Override
    public Member loadUserByUsername(String loginId) throws UsernameNotFoundException {
        // MemberRepository를 사용하여 loginId로 DB에서 Member 정보를 조회
        Optional<Member> _member = memberRepository.findByLoginId(loginId);

        // 만약 사용자를 찾지 못하면 UsernameNotFoundException 발생
        if (_member.isEmpty()) {
            throw new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + loginId);
        }

        // 찾은 Member 객체를 반환 (Member 클래스가 UserDetails를 구현했으므로 바로 반환 가능)
        return _member.get();
    }
}