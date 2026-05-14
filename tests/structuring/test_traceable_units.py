from __future__ import annotations

from arbiter.schemas.regulation_structuring import NormalizedTextInput, SourceLocationKind
from arbiter.structuring.pipeline import structure_regulation


def test_units_preserve_original_text() -> None:
    text = "Article 1 Scope\n\nThe manager must report."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    assert len(output.units) >= 1
    for unit in output.units:
        assert unit.original_text
        assert unit.original_text.strip()


def test_units_link_to_source_document_and_file() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="src-1", source_file="policy.md", content_type="markdown", text=text)
    output = structure_regulation(inp)

    for unit in output.units:
        assert unit.source_id == "src-1"
        assert unit.source_file == "policy.md"
        assert unit.document_id == output.document.document_id


def test_units_include_source_location() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    for unit in output.units:
        assert unit.source_location is not None
        assert unit.source_location.kind is not None


def test_hierarchy_path_preserved_for_articles() -> None:
    text = "Article 1 Scope\n\nContent.\n\nArticle 2 Reporting\n\nMore content."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    articles = [u for u in output.units if u.hierarchy.article_number is not None]
    assert len(articles) == 2
    assert articles[0].hierarchy.article_number == "Article 1"
    assert articles[1].hierarchy.article_number == "Article 2"


def test_markdown_heading_labels_populate_hierarchy_fields() -> None:
    text = "# Part A\n\n## Chapter 1\n\n### Section A\n\nArticle 1 Scope\n\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.md", content_type="markdown", text=text)
    output = structure_regulation(inp)

    article = next(u for u in output.units if u.unit_kind == "article")
    assert article.hierarchy.part == "Part A"
    assert article.hierarchy.chapter == "Chapter 1"
    assert article.hierarchy.section == "Section A"
    assert article.hierarchy.heading_path == ["Part A", "Chapter 1", "Section A"]
