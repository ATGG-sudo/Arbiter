from __future__ import annotations

import os

from arbiter.schemas.regulation_structuring import NormalizedTextInput
from arbiter.structuring.pipeline import structure_regulation


def test_no_runtime_agent_or_tool_directories_created() -> None:
    # These paths should not exist for this feature
    for path in [
        "src/arbiter/agent",
        "src/arbiter/tools",
        "src/arbiter/runtime",
        "src/arbiter/web",
    ]:
        assert not os.path.isdir(path), f"Unexpected runtime directory: {path}"


def test_pipeline_output_does_not_contain_judgment_result() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    raw = output.model_dump_json()
    assert "JudgmentResult" not in raw
    assert "RulePack" not in raw
    assert "RuleItem" not in raw
    assert "final_compliance_conclusion" not in raw.lower()


def test_pipeline_output_is_not_runtime_safe() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    # All parse_status values should be draft/needs_review
    assert output.document.parse_status.value == "needs_review"
    for unit in output.units:
        assert unit.review_status.value == "needs_review"


def test_structuring_package_is_admin_only() -> None:
    from arbiter.structuring import __init__ as structuring_init

    # No runtime or agent registrations should exist in the package init
    init_source = open("src/arbiter/structuring/__init__.py").read()
    assert "agent" not in init_source.lower()
    assert "runtime" not in init_source.lower()
    assert "tool" not in init_source.lower()
