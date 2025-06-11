package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Conpro;
import com.ltk.springproject.domain.Work;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ConproRepository extends JpaRepository<Conpro, Long> { // Long으로 변경
    // 특정 작품에 대한 콘텐츠 제공처 정보 찾기
    List<Conpro> findByWork(Work work);
    List<Conpro> findByWorkId(Long workId); // Long으로 변경

    // 특정 제공처 이름으로 검색
    // List<Conpro> findByProviderNameContaining(String providerName);
}