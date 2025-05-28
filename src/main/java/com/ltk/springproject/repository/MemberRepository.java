package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Member; // Member 엔티티 클래스를 임포트합니다.
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository; // 선택 사항이지만 명시적으로 리포지토리임을 나타냅니다.

@Repository // 이 인터페이스가 Spring의 리포지토리 컴포넌트임을 나타냅니다.
public interface MemberRepository extends JpaRepository<Member, Long> {
    // JpaRepository를 상속받습니다.
    // <Member, Long> 에서 Member는 이 리포지토리가 다룰 엔티티 클래스이고,
    // Long은 해당 엔티티의 기본 키(id)의 타입입니다.

    // Spring Data JPA가 자동으로 다음 메서드들을 구현해 줍니다:
    // - save(Member entity): Member 객체 저장 (INSERT/UPDATE)
    // - findById(Long id): id로 Member 객체 조회
    // - findAll(): 모든 Member 객체 조회
    // - delete(Member entity): Member 객체 삭제

    // 필요하다면 여기에 추가적인 쿼리 메서드를 정의할 수 있습니다.
    // 예를 들어, 로그인 아이디로 회원을 찾는 메서드:
    // Optional<Member> findByLoginId(String loginId);
    // 이메일로 회원을 찾는 메서드:
    // Optional<Member> findByEmail(String email);
}