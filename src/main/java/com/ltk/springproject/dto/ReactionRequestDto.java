package com.ltk.springproject.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ReactionRequestDto {
    private String relTypeCode;
    private Long relId;
    private String reactionType;
}