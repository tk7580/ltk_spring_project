package com.ltk.springproject.dto;

import com.ltk.springproject.domain.Reply;
import lombok.Getter;

@Getter
public class ReplyDto {
    private final Reply reply;
    private final int level;
    private final ReactionStatusDto replyReactionStatus; // [수정]

    public ReplyDto(Reply reply, int level, ReactionStatusDto replyReactionStatus) {
        this.reply = reply;
        this.level = level;
        this.replyReactionStatus = replyReactionStatus;
    }
}