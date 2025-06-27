package com.ltk.springproject.controller;

import com.ltk.springproject.domain.*;
import com.ltk.springproject.dto.ArticleWithCommentsDto;
import com.ltk.springproject.repository.MemberRepository;
import com.ltk.springproject.service.ArticleService;
import com.ltk.springproject.service.BoardService;
import com.ltk.springproject.service.SeriesService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
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
        ArticleWithCommentsDto dto = articleService.getArticleWithComments(articleId);

        model.addAttribute("currentUser", getCurrentUser(principal));
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
    public String doWrite(@PathVariable Long seriesId, @RequestParam Long boardId, @RequestParam String title, @RequestParam String body, Principal principal, RedirectAttributes redirectAttributes) {
        Member member = memberRepository.findByLoginId(principal.getName()).orElseThrow(() -> new ResponseStatusException(HttpStatus.FORBIDDEN));
        Article savedArticle = articleService.writeArticle(member.getId(), boardId, title, body);
        redirectAttributes.addFlashAttribute("message", "게시글이 성공적으로 등록되었습니다.");
        return "redirect:/series/" + seriesId + "/board/" + savedArticle.getId();
    }

    // ... 이하 수정/삭제/댓글 API 등
}