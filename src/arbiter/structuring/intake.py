from __future__ import annotations

from pathlib import Path

from arbiter.schemas.regulation_structuring import (
    ExtractedTextBundle,
    FileInput,
    NormalizedTextInput,
    StructuringValidationFinding,
    ValidationSeverity,
)


def file_input_to_extracted_text_bundle(file_input: FileInput) -> ExtractedTextBundle:
    """Optional adapter boundary for future file-upload workflows.

    This first slice does not implement OCR, password handling, or full
    layout recovery. PDF and DOCX are not first-slice direct inputs; callers
    must provide pre-extracted text as NormalizedTextInput instead.

    Markdown and plain text files are read directly from ``file_ref`` as a
    controlled local path using UTF-8 encoding. If the path does not exist
    or cannot be read, the underlying OS exception is raised.
    """
    if file_input.file_type in ("pdf", "docx"):
        raise NotImplementedError(
            f"File extraction for '{file_input.file_type}' is not implemented in this slice. "
            "Provide pre-extracted text as NormalizedTextInput instead."
        )
    path = Path(file_input.file_ref)
    text = path.read_text(encoding="utf-8")
    return ExtractedTextBundle(
        source_id=file_input.source_id,
        source_file=file_input.source_file,
        text=text,
        extraction_method="deterministic",
        warnings=[],
    )


def extracted_text_bundle_to_normalized_input(
    bundle: ExtractedTextBundle,
) -> NormalizedTextInput:
    """Convert an extracted text bundle into the direct pipeline input.

    Markdown files are inferred from the source_file extension.
    """
    lowered = bundle.source_file.lower()
    content_type: str = "markdown" if lowered.endswith((".md", ".markdown")) else "normalized_text"
    return NormalizedTextInput(
        source_id=bundle.source_id,
        source_file=bundle.source_file,
        content_type=content_type,
        text=bundle.text,
    )


def validate_normalized_input(
    input: NormalizedTextInput,
) -> list[StructuringValidationFinding]:
    """Return intake-level validation findings for a normalized input."""
    findings: list[StructuringValidationFinding] = []
    if not input.text or not input.text.strip():
        findings.append(
            StructuringValidationFinding(
                code="empty_input_text",
                severity=ValidationSeverity.ERROR,
                message="Normalized text input is empty after trimming",
            )
        )
    if input.content_type not in {"normalized_text", "markdown"}:
        findings.append(
            StructuringValidationFinding(
                code="unsupported_content_type",
                severity=ValidationSeverity.ERROR,
                message=f"Content type '{input.content_type}' is not a supported direct input",
            )
        )
    return findings
