package com.ltk.springproject.dto;

import lombok.Getter;
import lombok.Setter;
import java.math.BigDecimal;

@Getter
@Setter
public class RateRequestDto {
    private BigDecimal score;
    private String comment;
}