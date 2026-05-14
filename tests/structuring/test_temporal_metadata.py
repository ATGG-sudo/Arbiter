from __future__ import annotations

from datetime import date

from arbiter.schemas.regulation_structuring import NormalizedTextInput
from arbiter.structuring.pipeline import structure_regulation


def test_temporal_dates_extracted_from_metadata() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
        metadata={
            "effective_date": "2026-01-15",
            "promulgation_date": "2025-12-01",
            "repeal_date": "2027-01-01",
            "version_label": "v2",
            "amendment_history_text": "Amended in 2025",
        },
    )
    output = structure_regulation(inp)

    assert output.document.effective_date == date(2026, 1, 15)
    assert output.document.promulgation_date == date(2025, 12, 1)
    assert output.document.repeal_date == date(2027, 1, 1)
    assert output.document.temporal_metadata.version_label == "v2"
    assert output.document.temporal_metadata.amendment_history_text == "Amended in 2025"


def test_missing_dates_are_null_and_reported() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    assert output.document.effective_date is None
    assert output.document.promulgation_date is None
    assert output.document.repeal_date is None
    assert any(
        f.code == "missing_temporal_metadata"
        for f in output.validation_report.findings
    )


def test_ambiguity_notes_present_when_dates_uncertain() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
        metadata={
            "validity_notes": ["Date not clearly stated in source"],
        },
    )
    output = structure_regulation(inp)

    assert "Date not clearly stated in source" in output.document.temporal_metadata.validity_notes


def test_date_text_fields_preserved_from_metadata() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
        metadata={
            "effective_date": "2026-01-15",
            "promulgation_date": "2025-12-01",
            "repeal_date": "2027-01-01",
        },
    )
    output = structure_regulation(inp)

    assert output.document.temporal_metadata.effective_date_text == "2026-01-15"
    assert output.document.temporal_metadata.promulgation_date_text == "2025-12-01"
    assert output.document.temporal_metadata.repeal_date_text == "2027-01-01"


def test_date_text_fields_null_when_not_provided() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    output = structure_regulation(inp)

    assert output.document.temporal_metadata.effective_date_text is None
    assert output.document.temporal_metadata.promulgation_date_text is None
    assert output.document.temporal_metadata.repeal_date_text is None
