package com.ltk.springproject.dto;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Reply;
import lombok.Getter;

import java.util.List;

@Getter
public class ArticleWithCommentsDto {
    private final Article article;
    private final List<Reply> comments; // 최상위 댓글 목록

    public ArticleWithCommentsDto(Article article, List<Reply> comments) {
        this.article = article;
        this.comments = comments;
    }
}