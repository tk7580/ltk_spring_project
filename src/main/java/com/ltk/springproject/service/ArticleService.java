package com.ltk.springproject.service;

import com.ltk.springproject.domain.*;
import com.ltk.springproject.dto.ArticleWithCommentsDto;
import com.ltk.springproject.dto.ReactionStatusDto;
import com.ltk.springproject.dto.ReplyDto;
import com.ltk.springproject.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
@RequiredArgsConstructor
public class ArticleService {

    private final ArticleRepository articleRepository;
    private final ReplyRepository replyRepository;
    private final MemberRepository memberRepository;
    private final BoardRepository boardRepository;
    private final ArticleViewLogRepository articleViewLogRepository;
    private final ReactionPointRepository reactionPointRepository;

    // [추가] 누락되었던 메소드를 다시 추가합니다.
    @Transactional(readOnly = true)
    public List<Article> findArticlesByBoardId(Long boardId) {
        return articleRepository.findByBoardIdOrderByIdDesc(boardId);
    }

    public ArticleWithCommentsDto getArticleWithComments(Long articleId, Long memberId) {
        Article article = articleRepository.findById(articleId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시글을 찾을 수 없습니다."));

        if (memberId != null) {
            if (!articleViewLogRepository.existsByMemberIdAndArticleId(memberId, articleId)) {
                Member member = memberRepository.findById(memberId)
                        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
                ArticleViewLog viewLog = ArticleViewLog.builder().member(member).article(article).build();
                articleViewLogRepository.save(viewLog);
                article.setHitCount(article.getHitCount() + 1);
            }
        }

        ReactionStatusDto articleReactionStatus = getReactionStatus("article", articleId, memberId);
        List<Reply> topLevelReplies = replyRepository.findByArticleAndParentIsNullOrderByRegDateAsc(article);
        List<ReplyDto> flattenedReplies = new ArrayList<>();
        flattenReplies(topLevelReplies, 0, flattenedReplies, memberId);

        return new ArticleWithCommentsDto(article, articleReactionStatus, flattenedReplies);
    }

    private void flattenReplies(List<Reply> replies, int level, List<ReplyDto> flattenedList, Long memberId) {
        for (Reply reply : replies) {
            int displayLevel = Math.min(level, 1);
            ReactionStatusDto replyReactionStatus = getReactionStatus("reply", reply.getId(), memberId);
            flattenedList.add(new ReplyDto(reply, displayLevel, replyReactionStatus));
            if (reply.getChildren() != null && !reply.getChildren().isEmpty()) {
                flattenReplies(reply.getChildren(), level + 1, flattenedList, memberId);
            }
        }
    }

    private ReactionStatusDto getReactionStatus(String relTypeCode, Long relId, Long memberId) {
        long goodCount, badCount;
        String currentUserReaction = null;

        if ("article".equals(relTypeCode)) {
            Article article = articleRepository.findById(relId).orElseThrow(() -> new IllegalArgumentException("게시글 정보를 찾을 수 없습니다."));
            goodCount = article.getGoodReactionPoint();
            badCount = article.getBadReactionPoint();
        } else {
            Reply reply = replyRepository.findById(relId).orElseThrow(() -> new IllegalArgumentException("댓글 정보를 찾을 수 없습니다."));
            goodCount = reply.getGoodReactionPoint();
            badCount = reply.getBadReactionPoint();
        }

        if (memberId != null) {
            Optional<ReactionPoint> reactionPoint = reactionPointRepository.findByMemberIdAndRelTypeCodeAndRelId(memberId, relTypeCode, relId);
            if (reactionPoint.isPresent()) {
                currentUserReaction = reactionPoint.get().getReactionType();
            }
        }

        return new ReactionStatusDto(goodCount, badCount, currentUserReaction);
    }

    @Transactional(readOnly = true)
    public Article getArticle(Long articleId) {
        return articleRepository.findById(articleId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시글을 찾을 수 없습니다."));
    }

    public Article writeArticle(Long memberId, Long boardId, String title, String body) {
        Member member = memberRepository.findById(memberId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
        Board board = boardRepository.findById(boardId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시판을 찾을 수 없습니다."));
        Article newArticle = Article.builder().member(member).board(board).title(title).body(body).build();
        return articleRepository.save(newArticle);
    }

    public void modifyArticle(Long articleId, Long memberId, String title, String body) {
        Article article = getArticle(articleId);
        if (!article.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "수정 권한이 없습니다.");
        }
        article.setTitle(title);
        article.setBody(body);
    }

    public void deleteArticle(Long articleId, Long memberId) {
        Article article = getArticle(articleId);
        if (!article.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "삭제 권한이 없습니다.");
        }
        articleRepository.delete(article);
    }

    public Reply writeReply(Long memberId, Long articleId, Long parentId, String body) {
        Member member = memberRepository.findById(memberId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
        Article article = getArticle(articleId);
        Reply parent = null;
        if (parentId != null) {
            parent = replyRepository.findById(parentId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "부모 댓글을 찾을 수 없습니다."));
        }
        Reply reply = Reply.builder().member(member).article(article).parent(parent).body(body).build();
        return replyRepository.save(reply);
    }

    public void modifyReply(Long replyId, Long memberId, String body) {
        Reply reply = replyRepository.findById(replyId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "댓글을 찾을 수 없습니다."));
        if (!reply.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "수정 권한이 없습니다.");
        }
        reply.setBody(body);
    }

    public void deleteReply(Long replyId, Long memberId) {
        Reply reply = replyRepository.findById(replyId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "댓글을 찾을 수 없습니다."));
        if (!reply.getMember().getId().equals(memberId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "삭제 권한이 없습니다.");
        }
        replyRepository.delete(reply);
    }
}