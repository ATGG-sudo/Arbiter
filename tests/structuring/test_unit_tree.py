from __future__ import annotations

from arbiter.schemas.regulation_structuring import NormalizedTextInput
from arbiter.structuring.pipeline import structure_regulation


def test_parent_unit_id_and_order_index_support_tree_rendering() -> None:
    text = "# Title\n\n## Chapter 1\n\nArticle 1\nContent.\n\nArticle 2\nMore."
    inp = NormalizedTextInput(source_id="t", source_file="t.md", content_type="markdown", text=text)
    output = structure_regulation(inp)

    # Build a quick lookup
    by_id = {u.unit_id: u for u in output.units}

    for unit in output.units:
        assert unit.order_index >= 0
        if unit.parent_unit_id is not None:
            assert unit.parent_unit_id in by_id


def test_sibling_order_index_is_sequential() -> None:
    text = "# Title\n\n## Chapter 1\n\nArticle 1\nA.\n\nArticle 2\nB.\n\nArticle 3\nC."
    inp = NormalizedTextInput(source_id="t", source_file="t.md", content_type="markdown", text=text)
    output = structure_regulation(inp)

    chapter = next((u for u in output.units if u.unit_kind == "chapter"), None)
    assert chapter is not None
    children = [u for u in output.units if u.parent_unit_id == chapter.unit_id]
    children.sort(key=lambda u: u.order_index)
    for i, child in enumerate(children):
        assert child.order_index == i


def test_display_label_present_on_units() -> None:
    text = "Article 1 Scope\n\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    for unit in output.units:
        assert unit.display_label is not None
