package com.ltk.springproject.service;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.ReactionPoint;
import com.ltk.springproject.domain.Reply;
import com.ltk.springproject.repository.ArticleRepository;
import com.ltk.springproject.repository.ReactionPointRepository;
import com.ltk.springproject.repository.ReplyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.Optional;

@Service
@Transactional
@RequiredArgsConstructor
public class ReactionService {

    private final ReactionPointRepository reactionPointRepository;
    private final ArticleRepository articleRepository;
    private final ReplyRepository replyRepository;

    public String toggleReaction(Member member, String relTypeCode, Long relId, String reactionType) {
        Optional<ReactionPoint> oldReactionOpt = reactionPointRepository.findByMemberIdAndRelTypeCodeAndRelId(member.getId(), relTypeCode, relId);

        if (oldReactionOpt.isPresent()) {
            ReactionPoint oldReaction = oldReactionOpt.get();
            if (oldReaction.getReactionType().equals(reactionType)) {
                reactionPointRepository.delete(oldReaction);
                updateReactionCounts(relTypeCode, relId, reactionType, -1);
                return "reaction_cancelled";
            } else {
                String oldReactionType = oldReaction.getReactionType();
                oldReaction.setReactionType(reactionType);
                oldReaction.setPoint(reactionType.equals("GOOD") ? 1 : -1);
                updateReactionCounts(relTypeCode, relId, oldReactionType, -1);
                updateReactionCounts(relTypeCode, relId, reactionType, 1);
                return "reaction_changed";
            }
        } else {
            ReactionPoint newReaction = ReactionPoint.builder()
                    .member(member).relTypeCode(relTypeCode).relId(relId)
                    .reactionType(reactionType).point(reactionType.equals("GOOD") ? 1 : -1)
                    .build();
            reactionPointRepository.save(newReaction);
            updateReactionCounts(relTypeCode, relId, reactionType, 1);
            return "reaction_added";
        }
    }

    private void updateReactionCounts(String relTypeCode, Long relId, String reactionType, int amount) {
        if ("article".equals(relTypeCode)) {
            Article article = articleRepository.findById(relId).orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));
            if ("GOOD".equals(reactionType)) {
                article.setGoodReactionPoint(article.getGoodReactionPoint() + amount);
            } else {
                article.setBadReactionPoint(article.getBadReactionPoint() + amount);
            }
        } else if ("reply".equals(relTypeCode)) {
            Reply reply = replyRepository.findById(relId).orElseThrow(() -> new IllegalArgumentException("댓글을 찾을 수 없습니다."));
            if ("GOOD".equals(reactionType)) {
                reply.setGoodReactionPoint(reply.getGoodReactionPoint() + amount);
            } else {
                reply.setBadReactionPoint(reply.getBadReactionPoint() + amount);
            }
        }
    }
}