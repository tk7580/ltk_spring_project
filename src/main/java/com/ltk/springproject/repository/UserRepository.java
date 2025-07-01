package com.ltk.springproject.repository;

import com.ltk.springproject.domain.Member;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<Member, Long> {
}
