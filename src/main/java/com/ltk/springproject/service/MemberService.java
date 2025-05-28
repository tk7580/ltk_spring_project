package com.ltk.springproject.service;

import com.ltk.springproject.domain.Member;
import com.ltk.springproject.repository.MemberRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional; // 트랜잭션 처리를 위한 어노테이션

import java.time.LocalDateTime; // 날짜 시간 처리를 위해 임포트
import java.util.List; // 모든 회원 조회를 위해 임포트
import java.util.Optional; // 단일 회원 조회를 위해 임포트

@Service // 1. 이 클래스가 Spring의 서비스 컴포넌트임을 나타냅니다.
@Transactional(readOnly = true) // 2. 트랜잭션 설정을 클래스 레벨에 적용 (읽기 전용)
public class MemberService {

    private final MemberRepository memberRepository; // 3. MemberRepository 주입

    // 4. 생성자 주입 (스프링이 자동으로 MemberRepository 빈을 주입해 줍니다.)
    public MemberService(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }

    /**
     * 새로운 회원을 등록합니다.
     *
     * @param loginId      로그인 아이디
     * @param loginPw      로그인 비밀번호
     * @param name         이름
     * @param nickname     닉네임
     * @param cellphoneNum 휴대폰 번호
     * @param email        이메일
     * @return 저장된 Member 객체
     */
    @Transactional // 5. 쓰기 작업에는 별도의 트랜잭션 어노테이션을 적용합니다.
    public Member join(String loginId, String loginPw, String name,
                       String nickname, String cellphoneNum, String email) {

        // 비즈니스 로직: 중복 로그인 아이디 또는 닉네임, 이메일 확인 (선택 사항)
        // findByLoginId(loginId).ifPresent(m -> {
        //     throw new IllegalStateException("이미 존재하는 아이디입니다.");
        // });
        // findByNickname(nickname).ifPresent(m -> {
        //     throw new IllegalStateException("이미 존재하는 닉네임입니다.");
        // });
        // findByEmail(email).ifPresent(m -> {
        //     throw new IllegalStateException("이미 존재하는 이메일입니다.");
        // });

        // Member 객체 생성 (Builder 패턴 활용)
        Member member = Member.builder()
                .loginId(loginId)
                .loginPw(loginPw)
                .name(name)
                .nickname(nickname)
                .cellphoneNum(cellphoneNum)
                .email(email)
                .authLevel(3) // 기본 권한 레벨
                .delStatus(false) // 기본 탈퇴 여부
                // regDate와 updateDate는 @PrePersist에서 자동으로 설정됩니다.
                .build();

        return memberRepository.save(member); // DB에 저장
    }

    /**
     * 모든 회원 정보를 조회합니다.
     *
     * @return 모든 회원 정보 리스트
     */
    public List<Member> findAllMembers() {
        return memberRepository.findAll();
    }

    /**
     * 특정 ID로 회원 정보를 조회합니다.
     *
     * @param id 회원 고유 ID
     * @return Optional<Member> 객체 (회원이 존재하지 않을 수 있으므로 Optional 사용)
     */
    public Optional<Member> findMemberById(Long id) {
        return memberRepository.findById(id);
    }

    // 여기에 로그인 아이디, 닉네임, 이메일로 회원을 찾는 메서드를 추가할 수 있습니다.
    // 예를 들어, MemberRepository에 findByLoginId(String loginId) 메서드를 추가한 후
    // public Optional<Member> findByLoginId(String loginId) {
    //     return memberRepository.findByLoginId(loginId);
    // }

    // 여기에 회원 정보 수정, 탈퇴 등의 비즈니스 로직을 추가할 수 있습니다.
    // @Transactional
    // public Member updateMember(Long id, String newEmail, String newNickname) {
    //     Member member = memberRepository.findById(id)
    //                     .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 회원입니다."));
    //     member.setEmail(newEmail);
    //     member.setNickname(newNickname);
    //     // updateDate는 @PreUpdate에서 자동으로 설정됩니다.
    //     return memberRepository.save(member); // 변경 감지 후 DB 업데이트
    // }
}