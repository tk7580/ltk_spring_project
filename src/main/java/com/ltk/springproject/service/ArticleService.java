package com.ltk.springproject.service;

import com.ltk.springproject.domain.*;
import com.ltk.springproject.dto.ArticleWithCommentsDto;
import com.ltk.springproject.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
public class ArticleService {

    private final ArticleRepository articleRepository;
    private final ReplyRepository replyRepository;
    private final MemberRepository memberRepository;
    private final BoardRepository boardRepository;
    private final ArticleViewLogRepository articleViewLogRepository; // [신규] 조회 기록 리포지토리 주입

    // 게시판 ID로 게시글 목록 조회 (최신순)
    @Transactional(readOnly = true)
    public List<Article> findArticlesByBoardId(Long boardId) {
        return articleRepository.findByBoardIdOrderByIdDesc(boardId);
    }

    // [수정] 게시글 상세 조회 로직 변경 (세션 -> DB 기반)
    public ArticleWithCommentsDto getArticleWithComments(Long articleId, Long memberId) {
        Article article = articleRepository.findById(articleId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시글을 찾을 수 없습니다."));

        // 로그인한 사용자이고, 이 게시글을 처음 조회하는 경우에만 조회수 증가
        if (memberId != null) {
            if (!articleViewLogRepository.existsByMemberIdAndArticleId(memberId, articleId)) {
                // 조회 기록 테이블에 로그 저장
                Member member = memberRepository.findById(memberId)
                        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
                ArticleViewLog viewLog = ArticleViewLog.builder()
                        .member(member)
                        .article(article)
                        .build();
                articleViewLogRepository.save(viewLog);

                // 게시글의 조회수(hitCount) 1 증가
                article.setHitCount(article.getHitCount() + 1);
            }
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