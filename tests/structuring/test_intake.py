from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from arbiter.schemas.regulation_structuring import (
    DocumentSourceType,
    FileInput,
    NormalizedTextInput,
    ValidationSeverity,
)
from arbiter.structuring.intake import (
    extracted_text_bundle_to_normalized_input,
    file_input_to_extracted_text_bundle,
    validate_normalized_input,
)

FIXTURES_DIR = Path(__file__).with_suffix("").parent / "fixtures"


def test_file_input_to_extracted_text_bundle_rejects_pdf_and_docx() -> None:
    file_input = FileInput(
        source_id="source-1",
        source_file="policy.docx",
        file_type="docx",
        file_ref="opaque-ref",
    )
    with pytest.raises(NotImplementedError, match="not implemented in this slice"):
        file_input_to_extracted_text_bundle(file_input)

    pdf_input = FileInput(
        source_id="source-2",
        source_file="rule.pdf",
        file_type="pdf",
        file_ref="opaque-ref-2",
    )
    with pytest.raises(NotImplementedError, match="not implemented in this slice"):
        file_input_to_extracted_text_bundle(pdf_input)


def test_file_input_to_extracted_text_bundle_reads_text_file() -> None:
    fixture_path = FIXTURES_DIR / "sample_policy.txt"
    file_input = FileInput(
        source_id="source-1",
        source_file="policy.txt",
        file_type="text",
        file_ref=str(fixture_path),
    )
    bundle = file_input_to_extracted_text_bundle(file_input)

    assert bundle.source_id == "source-1"
    assert bundle.source_file == "policy.txt"
    assert "Internal Policy" in bundle.text
    assert bundle.extraction_method == "deterministic"
    assert "file_extraction_not_implemented_in_this_slice" not in bundle.warnings


def test_file_input_to_extracted_text_bundle_reads_markdown_file() -> None:
    fixture_path = FIXTURES_DIR / "sample_regulation.md"
    file_input = FileInput(
        source_id="source-md",
        source_file="regulation.md",
        file_type="markdown",
        file_ref=str(fixture_path),
    )
    bundle = file_input_to_extracted_text_bundle(file_input)

    assert bundle.source_id == "source-md"
    assert bundle.source_file == "regulation.md"
    assert "# Sample Regulation" in bundle.text
    assert bundle.extraction_method == "deterministic"


def test_file_input_to_extracted_text_bundle_rejects_missing_file() -> None:
    file_input = FileInput(
        source_id="source-1",
        source_file="missing.txt",
        file_type="text",
        file_ref=str(FIXTURES_DIR / "does_not_exist.txt"),
    )
    with pytest.raises((FileNotFoundError, OSError)):
        file_input_to_extracted_text_bundle(file_input)


def test_file_input_to_extracted_text_bundle_boundary_for_text_placeholder_removed() -> None:
    # Ensure the old placeholder behavior is gone
    fixture_path = FIXTURES_DIR / "sample_policy.txt"
    file_input = FileInput(
        source_id="source-1",
        source_file="policy.txt",
        file_type="text",
        file_ref=str(fixture_path),
    )
    bundle = file_input_to_extracted_text_bundle(file_input)
    assert bundle.text != "[extraction pending]"


def test_file_input_to_extracted_text_bundle_rejects_empty_file() -> None:
    fixture_path = FIXTURES_DIR / "empty.txt"
    file_input = FileInput(
        source_id="source-empty",
        source_file="empty.txt",
        file_type="text",
        file_ref=str(fixture_path),
    )
    with pytest.raises(ValueError):
        file_input_to_extracted_text_bundle(file_input)


def test_extracted_text_bundle_to_normalized_input_for_markdown() -> None:
    from arbiter.schemas.regulation_structuring import ExtractedTextBundle, ExtractionMethod

    bundle = ExtractedTextBundle(
        source_id="source-1",
        source_file="policy.md",
        text="# Policy\n\nArticle 1",
        extraction_method=ExtractionMethod.DETERMINISTIC,
        warnings=[],
    )
    normalized = extracted_text_bundle_to_normalized_input(bundle)

    assert normalized.source_id == "source-1"
    assert normalized.content_type == "markdown"
    assert normalized.text == "# Policy\n\nArticle 1"


def test_extracted_text_bundle_to_normalized_input_for_text() -> None:
    from arbiter.schemas.regulation_structuring import ExtractedTextBundle, ExtractionMethod

    bundle = ExtractedTextBundle(
        source_id="source-1",
        source_file="policy.txt",
        text="Policy text",
        extraction_method=ExtractionMethod.DETERMINISTIC,
        warnings=[],
    )
    normalized = extracted_text_bundle_to_normalized_input(bundle)

    assert normalized.content_type == "normalized_text"


def test_validate_normalized_input_accepts_valid_markdown() -> None:
    inp = NormalizedTextInput(
        source_id="s1",
        source_file="policy.md",
        content_type="markdown",
        text="# Title\n\nContent",
    )
    findings = validate_normalized_input(inp)

    assert not any(f.severity is ValidationSeverity.ERROR for f in findings)


def test_validate_normalized_input_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        NormalizedTextInput(
            source_id="s1",
            source_file="policy.md",
            content_type="markdown",
            text="   ",
        )


def test_validate_normalized_input_rejects_unsupported_content_type() -> None:
    # Test the validation function directly with a mock-like input object
    class FakeInput:
        text = "Some text"
        content_type = "pdf"

    findings = validate_normalized_input(FakeInput())

    assert any(
        f.code == "unsupported_content_type" and f.severity is ValidationSeverity.ERROR
        for f in findings
    )
