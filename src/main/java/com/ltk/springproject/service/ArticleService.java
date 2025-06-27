package com.ltk.springproject.service;

import com.ltk.springproject.domain.*;
import com.ltk.springproject.dto.ArticleWithCommentsDto;
import com.ltk.springproject.repository.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.server.ResponseStatusException;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
@Transactional
@RequiredArgsConstructor
public class ArticleService {

    private final ArticleRepository articleRepository;
    private final ReplyRepository replyRepository;
    private final MemberRepository memberRepository;
    private final BoardRepository boardRepository;

    // 게시판 ID로 게시글 목록 조회 (최신순)
    @Transactional(readOnly = true)
    public List<Article> findArticlesByBoardId(Long boardId) {
        return articleRepository.findByBoardIdOrderByIdDesc(boardId);
    }

    // 게시글 상세 조회 (조회수 중복 방지 로직 포함)
    public ArticleWithCommentsDto getArticleWithComments(Long articleId) {
        Article article = articleRepository.findById(articleId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시글을 찾을 수 없습니다."));

        // 세션을 이용한 조회수 중복 증가 방지
        HttpServletRequest req = ((ServletRequestAttributes) RequestContextHolder.currentRequestAttributes()).getRequest();
        HttpSession session = req.getSession();
        Set<Long> viewedArticles = (Set<Long>) session.getAttribute("viewedArticles");

        if (viewedArticles == null) {
            viewedArticles = new HashSet<>();
        }

        if (!viewedArticles.contains(articleId)) {
            article.setHitCount(article.getHitCount() + 1);
            viewedArticles.add(articleId);
            session.setAttribute("viewedArticles", viewedArticles);
        }

        List<Reply> replies = replyRepository.findByArticleAndParentIsNullOrderByRegDateAsc(article);
        return new ArticleWithCommentsDto(article, replies);
    }

    @Transactional(readOnly = true)
    public Article getArticle(Long articleId) {
        return articleRepository.findById(articleId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시글을 찾을 수 없습니다."));
    }

    // 게시글 작성
    public Article writeArticle(Long memberId, Long boardId, String title, String body) {
        Member member = memberRepository.findById(memberId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
        Board board = boardRepository.findById(boardId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시판을 찾을 수 없습니다."));
        Article newArticle = Article.builder().member(member).board(board).title(title).body(body).build();
        return articleRepository.save(newArticle);
    }

    // 게시글 수정
    public void modifyArticle(Long articleId, Long memberId, String title, String body) {
        Article article = getArticle(articleId);
        if (!article.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "수정 권한이 없습니다.");
        }
        article.setTitle(title);
        article.setBody(body);
    }

    // 게시글 삭제
    public void deleteArticle(Long articleId, Long memberId) {
        Article article = getArticle(articleId);
        if (!article.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "삭제 권한이 없습니다.");
        }
        articleRepository.delete(article);
    }

    // 댓글 작성
    public Reply writeReply(Long memberId, Long articleId, Long parentId, String body) {
        Member member = memberRepository.findById(memberId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
        Article article = getArticle(articleId);
        Reply parent = (parentId != null) ? replyRepository.findById(parentId).orElse(null) : null;
        Reply reply = Reply.builder().member(member).article(article).parent(parent).body(body).build();
        return replyRepository.save(reply);
    }

    // 댓글 삭제 (수정은 없음)
    public void deleteReply(Long replyId, Long memberId) {
        Reply reply = replyRepository.findById(replyId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "댓글을 찾을 수 없습니다."));
        if (!reply.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "삭제 권한이 없습니다.");
        }
        replyRepository.delete(reply);
    }
}