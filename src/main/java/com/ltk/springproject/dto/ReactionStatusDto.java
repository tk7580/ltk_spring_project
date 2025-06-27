package com.ltk.springproject.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class ReactionStatusDto {
    private long goodReactionCount;
    private long badReactionCount;
    private String currentUserReaction; // "GOOD", "BAD", or null
}