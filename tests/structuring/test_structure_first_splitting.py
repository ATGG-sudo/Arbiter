from __future__ import annotations

import pytest

from arbiter.schemas.regulation_structuring import NormalizedTextInput, ValidationSeverity
from arbiter.structuring.extraction import split_text


def test_markdown_headings_create_hierarchy() -> None:
    text = "# Example Regulation\n\n## Chapter 1\n\nArticle 1 Scope\n\nContent.\n\nArticle 2\n\nMore content."
    inp = NormalizedTextInput(source_id="md", source_file="reg.md", content_type="markdown", text=text)
    candidates, findings = split_text(inp)

    kinds = [c["kind"] for c in candidates]
    assert "part" in kinds
    assert "chapter" in kinds
    assert "article" in kinds

    # Articles should be children of the chapter
    chapter = next(c for c in candidates if c["kind"] == "chapter")
    articles = [c for c in candidates if c["kind"] == "article"]
    for art in articles:
        assert art["parent_id"] == chapter["unit_id"]


def test_article_x_splitting_in_plain_text() -> None:
    text = "Article 1 Scope\n\nThis applies.\n\nArticle 2 Reporting\n\nReport changes."
    inp = NormalizedTextInput(source_id="txt", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    articles = [c for c in candidates if c["kind"] == "article"]
    assert len(articles) == 2
    assert articles[0]["hierarchy"]["article_number"] == "Article 1"
    assert articles[1]["hierarchy"]["article_number"] == "Article 2"


def test_numbered_paragraph_splitting() -> None:
    text = "1. Scope\nThis applies.\n\n2. Required action\nDo this."
    inp = NormalizedTextInput(source_id="txt", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    articles = [c for c in candidates if c["kind"] == "article"]
    assert len(articles) == 2
    assert articles[0]["hierarchy"]["article_number"] == "1."


def test_paragraph_fallback_when_no_structure() -> None:
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    inp = NormalizedTextInput(source_id="txt", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    paragraphs = [c for c in candidates if c["kind"] == "paragraph"]
    assert len(paragraphs) >= 1
    assert not any(c.get("warning") == "token_count_fallback_used" for c in candidates)


def test_char_count_fallback_warning_for_long_unstructured_english_text() -> None:
    text = "word " * 5000  # Very long text with no structure
    inp = NormalizedTextInput(source_id="txt", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    assert any(c.get("warning") == "char_count_fallback_used" for c in candidates)
    assert any(
        f.code == "char_count_fallback" and f.severity is ValidationSeverity.WARNING
        for f in findings
    )


def test_char_count_fallback_warning_for_long_unstructured_chinese_text() -> None:
    text = "这是一些非常长的中文文本，没有任何明确的结构或条号。" * 200
    inp = NormalizedTextInput(source_id="cn", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    assert any(c.get("warning") == "char_count_fallback_used" for c in candidates)
    assert any(
        f.code == "char_count_fallback" and f.severity is ValidationSeverity.WARNING
        for f in findings
    )


def test_chinese_article_splitting() -> None:
    text = "第1条 范围\n\n适用于所有情况。\n\n第2条 报告\n\n须在三日内报告。"
    inp = NormalizedTextInput(source_id="cn", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    articles = [c for c in candidates if c["kind"] == "article"]
    assert len(articles) == 2
    assert articles[0]["hierarchy"]["article_number"] == "第1条"


def test_chinese_numeral_article_splitting() -> None:
    text = "第一条 范围\n\n适用于所有情况。\n\n第二条 报告\n\n须在三日内报告。\n\n第十条 处罚\n\n罚款。"
    inp = NormalizedTextInput(source_id="cn", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    articles = [c for c in candidates if c["kind"] == "article"]
    assert len(articles) == 3
    assert articles[0]["hierarchy"]["article_number"] == "第一条"
    assert articles[1]["hierarchy"]["article_number"] == "第二条"
    assert articles[2]["hierarchy"]["article_number"] == "第十条"


def test_article_titles_are_preserved_for_english_and_chinese_articles() -> None:
    english = NormalizedTextInput(
        source_id="en",
        source_file="reg.txt",
        content_type="normalized_text",
        text="Article 1 Scope\n\nThis applies.",
    )
    english_candidates, _ = split_text(english)
    english_article = next(c for c in english_candidates if c["kind"] == "article")
    assert english_article["hierarchy"]["article_title"] == "Scope"

    chinese = NormalizedTextInput(
        source_id="cn",
        source_file="reg.txt",
        content_type="normalized_text",
        text="第一条 范围\n\n适用于所有情况。",
    )
    chinese_candidates, _ = split_text(chinese)
    chinese_article = next(c for c in chinese_candidates if c["kind"] == "article")
    assert chinese_article["hierarchy"]["article_title"] == "范围"


def test_chinese_numeral_reference_detection() -> None:
    text = "参见第三条及第五条。"
    inp = NormalizedTextInput(source_id="cn", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    # Text has no article structure; should fall back to paragraph
    paragraphs = [c for c in candidates if c["kind"] == "paragraph"]
    assert len(paragraphs) >= 1


def test_chinese_complex_numeral_article_splitting() -> None:
    text = (
        "第一百二十一条 范围\n\n适用于所有情况。\n\n"
        "第一千零一条 定义\n\n定义内容。\n\n"
        "第一千零二十三条 处罚\n\n罚款内容。\n\n"
        "第一百二十二条 程序\n\n程序内容。"
    )
    inp = NormalizedTextInput(source_id="cn", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    articles = [c for c in candidates if c["kind"] == "article"]
    assert len(articles) == 4
    labels = {a["hierarchy"]["article_number"] for a in articles}
    assert "第一百二十一条" in labels
    assert "第一千零一条" in labels
    assert "第一千零二十三条" in labels
    assert "第一百二十二条" in labels


def test_chinese_complex_numeral_reference_in_text() -> None:
    text = "参见第一百二十一条及第一千零一条。"
    inp = NormalizedTextInput(source_id="cn", source_file="reg.txt", content_type="normalized_text", text=text)
    candidates, findings = split_text(inp)

    # No article structure; should fall back to paragraph
    paragraphs = [c for c in candidates if c["kind"] == "paragraph"]
    assert len(paragraphs) >= 1
