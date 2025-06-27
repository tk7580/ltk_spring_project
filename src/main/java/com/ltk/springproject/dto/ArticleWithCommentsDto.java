package com.ltk.springproject.dto;

import com.ltk.springproject.domain.Article;
import lombok.Getter;
import java.util.List;

@Getter
public class ArticleWithCommentsDto {
    private final Article article;
    private final ReactionStatusDto articleReactionStatus; // [수정]
    private final List<ReplyDto> comments;

    public ArticleWithCommentsDto(Article article, ReactionStatusDto articleReactionStatus, List<ReplyDto> comments) {
        this.article = article;
        this.articleReactionStatus = articleReactionStatus;
        this.comments = comments;
    }
}