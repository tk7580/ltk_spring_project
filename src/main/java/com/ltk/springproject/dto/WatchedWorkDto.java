package com.ltk.springproject.dto;

import com.ltk.springproject.domain.Work;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;

@Getter
@Setter
@AllArgsConstructor
public class WatchedWorkDto {
    private Work work;
    private BigDecimal score;
    private String comment;
}