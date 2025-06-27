package com.ltk.springproject.controller;

import com.ltk.springproject.domain.Article;
import com.ltk.springproject.domain.Board;
import com.ltk.springproject.domain.Member;
import com.ltk.springproject.domain.Series;
import com.ltk.springproject.dto.ArticleWithCommentsDto;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.ArticleService;
import com.ltk.springproject.service.BoardService;
import com.ltk.springproject.service.SeriesService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.security.Principal;
import java.util.List;

@Controller
@RequestMapping("/series/{seriesId}/board")
@RequiredArgsConstructor
public class ArticleController {

    private final ArticleService articleService;
    private final BoardService boardService;
    private final SeriesService seriesService;
    private final MemberRepository memberRepository;

    private Member getCurrentUser(Principal principal) {
        if (principal == null) return null;
        return memberRepository.findByLoginId(principal.getName()).orElse(null);
    }

    @GetMapping("")
    public String showList(@PathVariable Long seriesId, Model model, Principal principal) {
        Series series = seriesService.findById(seriesId);
        Board board = boardService.getBoardBySeriesId(seriesId);
        List<Article> articles = articleService.findArticlesByBoardId(board.getId());
        model.addAttribute("currentUser", getCurrentUser(principal));
        model.addAttribute("series", series);
        model.addAttribute("board", board);
        model.addAttribute("articles", articles);
        return "article/list";
    }

    @GetMapping("/{articleId}")
    public String showDetail(@PathVariable Long seriesId, @PathVariable Long articleId, Model model, Principal principal) {
        Series series = seriesService.findById(seriesId);
        Member currentUser = getCurrentUser(principal);
        Long currentUserId = (currentUser != null) ? currentUser.getId() : null;
        ArticleWithCommentsDto dto = articleService.getArticleWithComments(articleId, currentUserId);
        model.addAttribute("currentUser", currentUser);
        model.addAttribute("series", series);
        model.addAttribute("dto", dto);
        return "article/detail";
    }

    @PreAuthorize("isAuthenticated()")
    @GetMapping("/write")
    public String showWriteForm(@PathVariable Long seriesId, Model model) {
        Series series = seriesService.findById(seriesId);
        Board board = boardService.getBoardBySeriesId(seriesId);
        model.addAttribute("series", series);
        model.addAttribute("board", board);
        return "article/form";
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/write")
    public String doWrite(@PathVariable Long seriesId, @RequestParam("boardId") Long boardId, @RequestParam("title") String title, @RequestParam("body") String body, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = getCurrentUser(principal);
        Article savedArticle = articleService.writeArticle(member.getId(), boardId, title, body);
        redirectAttributes.addFlashAttribute("message", "게시글이 성공적으로 등록되었습니다.");
        return "redirect:/series/" + seriesId + "/board/" + savedArticle.getId();
    }

    @PreAuthorize("isAuthenticated()")
    @GetMapping("/{articleId}/modify")
    public String showModifyForm(@PathVariable Long seriesId, @PathVariable Long articleId, Model model, Principal principal) {
        Article article = articleService.getArticle(articleId);
        Member currentUser = getCurrentUser(principal);
        if (currentUser == null || !article.getMember().getId().equals(currentUser.getId())) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "수정 권한이 없습니다.");
        }
        model.addAttribute("series", seriesService.findById(seriesId));
        model.addAttribute("article", article);
        return "article/form";
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/modify")
    public String doModify(@PathVariable Long seriesId, @PathVariable Long articleId, @RequestParam("title") String title, @RequestParam("body") String body, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = getCurrentUser(principal);
        articleService.modifyArticle(articleId, member.getId(), title, body);
        redirectAttributes.addFlashAttribute("message", "게시글이 성공적으로 수정되었습니다.");
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/delete")
    public String doDelete(@PathVariable Long seriesId, @PathVariable Long articleId, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = getCurrentUser(principal);
        articleService.deleteArticle(articleId, member.getId());
        redirectAttributes.addFlashAttribute("message", "게시글이 삭제되었습니다.");
        return "redirect:/series/" + seriesId + "/board";
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/replies")
    public String writeReply(@PathVariable("seriesId") Long seriesId,
                             @PathVariable("articleId") Long articleId,
                             @RequestParam(name = "parentId", required = false) Long parentId,
                             @RequestParam("body") String body,
                             Principal principal) {
        Member member = getCurrentUser(principal);
        articleService.writeReply(member.getId(), articleId, parentId, body);
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/replies/{replyId}/delete")
    public String deleteReply(@PathVariable Long seriesId, @PathVariable Long articleId, @PathVariable Long replyId, Principal principal) {
        Member member = getCurrentUser(principal);
        articleService.deleteReply(replyId, member.getId());
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }

    @PreAuthorize("isAuthenticated()")
    @GetMapping("/{articleId}/replies/{replyId}/modify")
    public String showReplyModifyForm(@PathVariable Long seriesId, @PathVariable Long articleId, @PathVariable Long replyId, Model model, Principal principal) {
        Member currentUser = getCurrentUser(principal);
        ArticleWithCommentsDto dto = articleService.getArticleWithComments(articleId, (currentUser != null ? currentUser.getId() : null));
        model.addAttribute("dto", dto);
        model.addAttribute("series", seriesService.findById(seriesId));
        model.addAttribute("modifyReplyId", replyId);
        return "article/detail";
    }

    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/replies/{replyId}/modify")
    public String modifyReply(@PathVariable Long seriesId, @PathVariable Long articleId, @PathVariable Long replyId, @RequestParam String body, Principal principal) {
        Member member = getCurrentUser(principal);
        articleService.modifyReply(replyId, member.getId(), body);
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }
}