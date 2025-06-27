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

    // 현재 로그인한 사용자 정보를 가져오는 헬퍼 메소드
    private Member getCurrentUser(Principal principal) {
        if (principal == null) return null;
        return memberRepository.findByLoginId(principal.getName()).orElse(null);
    }

    // 게시글 목록 페이지
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

    // 게시글 상세 페이지
    @GetMapping("/{articleId}")
    public String showDetail(@PathVariable Long seriesId, @PathVariable Long articleId, Model model, Principal principal) {
        Series series = seriesService.findById(seriesId);
        Member currentUser = getCurrentUser(principal);

        // [수정] 현재 로그인한 사용자의 ID를 서비스로 전달
        Long currentUserId = (currentUser != null) ? currentUser.getId() : null;
        ArticleWithCommentsDto dto = articleService.getArticleWithComments(articleId, currentUserId);

        model.addAttribute("currentUser", currentUser);
        model.addAttribute("series", series);
        model.addAttribute("dto", dto);
        return "article/detail";
    }

    // 게시글 작성 폼 페이지
    @PreAuthorize("isAuthenticated()")
    @GetMapping("/write")
    public String showWriteForm(@PathVariable Long seriesId, Model model) {
        Series series = seriesService.findById(seriesId);
        Board board = boardService.getBoardBySeriesId(seriesId);
        model.addAttribute("series", series);
        model.addAttribute("board", board);
        return "article/form";
    }

    // 게시글 작성 처리
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/write")
    public String doWrite(@PathVariable Long seriesId, @RequestParam Long boardId, @RequestParam String title, @RequestParam String body, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = memberRepository.findByLoginId(principal.getName()).orElseThrow(() -> new ResponseStatusException(HttpStatus.FORBIDDEN, "사용자 정보를 찾을 수 없습니다."));
        Article savedArticle = articleService.writeArticle(member.getId(), boardId, title, body);
        redirectAttributes.addFlashAttribute("message", "게시글이 성공적으로 등록되었습니다.");
        return "redirect:/series/" + seriesId + "/board/" + savedArticle.getId();
    }

    // 게시글 수정 폼 페이지
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
        return "article/form"; // 작성/수정 폼 공유
    }

    // 게시글 수정 처리
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/modify")
    public String doModify(@PathVariable Long seriesId, @PathVariable Long articleId, @RequestParam String title, @RequestParam String body, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = getCurrentUser(principal);
        if (member == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }
        articleService.modifyArticle(articleId, member.getId(), title, body);
        redirectAttributes.addFlashAttribute("message", "게시글이 성공적으로 수정되었습니다.");
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }

    // 게시글 삭제 처리
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/delete")
    public String doDelete(@PathVariable Long seriesId, @PathVariable Long articleId, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = getCurrentUser(principal);
        if (member == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }
        articleService.deleteArticle(articleId, member.getId());
        redirectAttributes.addFlashAttribute("message", "게시글이 삭제되었습니다.");
        return "redirect:/series/" + seriesId + "/board";
    }

    // 댓글 작성 처리
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/replies")
    public String writeReply(@PathVariable Long seriesId, @PathVariable Long articleId, @RequestParam(required = false) Long parentId, @RequestParam String body, Principal principal) {
        Member member = getCurrentUser(principal);
        if (member == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }
        articleService.writeReply(member.getId(), articleId, parentId, body);
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }

    // 댓글 삭제 처리
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/{articleId}/replies/{replyId}/delete")
    public String deleteReply(@PathVariable Long seriesId, @PathVariable Long articleId, @PathVariable Long replyId, Principal principal) {
        Member member = getCurrentUser(principal);
        if (member == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }
        articleService.deleteReply(replyId, member.getId());
        return "redirect:/series/" + seriesId + "/board/" + articleId;
    }
}