from __future__ import annotations

import re
from datetime import date
from typing import Any

from arbiter.schemas.regulation_structuring import (
    DependencyEdgeDraft,
    DocumentCategory,
    DocumentClassificationDraft,
    DocumentSourceType,
    DocumentStatus,
    HierarchyPath,
    IssuerType,
    NormalizedTextInput,
    ParseStatus,
    ReferenceCandidate,
    RegulationDocumentDraft,
    RegulationUnitDraft,
    RelationKind,
    ResolvedDependencyGraphDraft,
    ReviewStatus,
    SemanticUnitDraft,
    SourceLocation,
    SourceLocationKind,
    StructuringValidationFinding,
    TemporalMetadata,
    ValidationSeverity,
)

_CN_DIGITS = "〇零一二两二三四五六七八九十百千"

MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
ARTICLE_RE = re.compile(
    rf"^(?:Article\s+\d+[a-zA-Z0-9\-]*[^\n]*|[第第](?:\d+|[{_CN_DIGITS}]+)[条條][^\n]*)",
    re.MULTILINE,
)
NUMBERED_PARAGRAPH_RE = re.compile(
    r"^(?:\d+\.\s+\S.*)$",
    re.MULTILINE,
)
REFERENCE_RE = re.compile(
    rf"(?:Article\s+\d+[a-zA-Z0-9\-]*|[第第](?:\d+|[{_CN_DIGITS}]+)[条條]|External\s+[\w\s]+Rules|《[^》]+》)",
    re.IGNORECASE,
)


def _make_doc_id(source_id: str) -> str:
    return f"doc-{source_id}"


def _make_unit_id(document_id: str, index: int) -> str:
    return f"{document_id}-unit-{index}"


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _make_location(paragraph_index: int) -> SourceLocation:
    return SourceLocation(
        kind=SourceLocationKind.PARAGRAPH_INDEX,
        value=str(paragraph_index),
        confidence=0.8,
    )


def build_document_draft(input: NormalizedTextInput) -> RegulationDocumentDraft:
    """Create a RegulationDocumentDraft from normalized input and optional metadata."""
    meta = input.metadata or {}

    category_tags: list[str] = meta.get("category_tags", [])
    categories: list[DocumentCategory] = [
        DocumentCategory(
            category_scheme="custom",
            category_label=tag,
        )
        for tag in category_tags
    ]

    classification = DocumentClassificationDraft(
        source_type=input.source_type or DocumentSourceType.UNKNOWN,
        issuer_type=meta.get("issuer_type", IssuerType.UNKNOWN),
        issuer_name=meta.get("issuer_name"),
        categories=categories,
        topic_tags=meta.get("topic_tags", []),
        classification_tags=[],
        evidence_text=[],
        ambiguity_notes=[],
    )

    temporal = TemporalMetadata(
        version_label=meta.get("version_label"),
        effective_date_text=meta.get("effective_date_text") or (
            meta.get("effective_date") if isinstance(meta.get("effective_date"), str) else None
        ),
        promulgation_date_text=meta.get("promulgation_date_text") or (
            meta.get("promulgation_date") if isinstance(meta.get("promulgation_date"), str) else None
        ),
        repeal_date_text=meta.get("repeal_date_text") or (
            meta.get("repeal_date") if isinstance(meta.get("repeal_date"), str) else None
        ),
        amendment_history_text=meta.get("amendment_history_text"),
        validity_notes=meta.get("validity_notes", []),
        ambiguity_notes=[],
    )

    return RegulationDocumentDraft(
        document_id=_make_doc_id(input.source_id),
        source_id=input.source_id,
        source_file=input.source_file,
        classification=classification,
        title=meta.get("title"),
        document_number=meta.get("document_number"),
        document_status=meta.get("document_status", DocumentStatus.UNKNOWN),
        effective_date=_parse_date(meta.get("effective_date")),
        promulgation_date=_parse_date(meta.get("promulgation_date")),
        repeal_date=_parse_date(meta.get("repeal_date")),
        temporal_metadata=temporal,
        parse_status=ParseStatus.NEEDS_REVIEW,
        warnings=[],
    )


def _extract_heading_kind(level: int) -> str:
    if level == 1:
        return "part"
    if level == 2:
        return "chapter"
    if level == 3:
        return "section"
    return "section"


def _hierarchy_from_heading_stack(
    heading_stack: list[tuple[int, str, str]],
) -> dict[str, Any]:
    hierarchy: dict[str, Any] = {
        "heading_path": [title for _, _, title in heading_stack],
    }
    for level, _, title in heading_stack:
        kind = _extract_heading_kind(level)
        if kind in {"part", "chapter", "section"}:
            hierarchy[kind] = title
    return hierarchy


def _split_markdown(text: str, document_id: str) -> list[dict[str, Any]]:
    """Split markdown text into candidate units preserving heading hierarchy."""
    candidates: list[dict[str, Any]] = []
    headings = list(MARKDOWN_HEADING_RE.finditer(text))

    if not headings:
        return _split_plain_text(text, document_id)

    positions = [(m.start(), m.end(), m.group(1), m.group(2).strip()) for m in headings]
    positions.append((len(text), len(text), "", ""))

    heading_stack: list[tuple[int, str, str]] = []

    for i in range(len(positions) - 1):
        start = positions[i][0]
        end = positions[i + 1][0]
        hashes = positions[i][2]
        title = positions[i][3]
        level = len(hashes)
        section_text = text[start:end].strip()

        heading_unit_id = _make_unit_id(document_id, len(candidates))
        parent_id = None
        while heading_stack and heading_stack[-1][0] >= level:
            heading_stack.pop()
        if heading_stack:
            parent_id = heading_stack[-1][1]
        heading_stack.append((level, heading_unit_id, title))
        heading_hierarchy = _hierarchy_from_heading_stack(heading_stack)

        candidates.append({
            "kind": _extract_heading_kind(level),
            "level": level,
            "title": title,
            "text": section_text,
            "unit_id": heading_unit_id,
            "parent_id": parent_id,
            "display_label": title,
            "hierarchy": heading_hierarchy,
            "paragraph_index": i,
        })

        # Articles within this heading section
        article_matches = list(ARTICLE_RE.finditer(section_text))
        for j, match in enumerate(article_matches):
            art_start = match.start()
            art_end = article_matches[j + 1].start() if j + 1 < len(article_matches) else len(section_text)
            art_text = section_text[art_start:art_end].strip()
            art_title = match.group(0).strip()

            art_num: str | None = None
            art_name: str | None = None
            m = re.match(r"Article\s+(\d+[a-zA-Z0-9\-]*)\s*(.*)", art_title, re.IGNORECASE)
            if m:
                art_num = f"Article {m.group(1)}"
                art_name = m.group(2).strip() or None
            else:
                m = re.match(rf"[第第](\d+|[{_CN_DIGITS}]+)[条條]\s*(.*)", art_title)
                if m:
                    art_num = f"第{m.group(1)}条"
                    art_name = m.group(2).strip() or None

            article_hierarchy = _hierarchy_from_heading_stack(heading_stack)
            article_hierarchy.update({
                "article_number": art_num,
                "article_title": art_name,
            })

            candidates.append({
                "kind": "article",
                "level": 0,
                "title": art_title,
                "text": art_text,
                "unit_id": _make_unit_id(document_id, len(candidates)),
                "parent_id": heading_unit_id,
                "display_label": art_title,
                "hierarchy": article_hierarchy,
                "paragraph_index": i + j + 1,
            })

    return candidates


def _split_plain_text(text: str, document_id: str) -> list[dict[str, Any]]:
    """Split plain text by article or numbered paragraph patterns."""
    candidates: list[dict[str, Any]] = []

    matches = list(ARTICLE_RE.finditer(text))
    if not matches:
        matches = list(NUMBERED_PARAGRAPH_RE.finditer(text))

    if matches:
        # Leading text before first match becomes a paragraph unit
        if matches[0].start() > 0:
            lead = text[:matches[0].start()].strip()
            if lead:
                candidates.append({
                    "kind": "paragraph",
                    "level": 0,
                    "title": None,
                    "text": lead,
                    "unit_id": _make_unit_id(document_id, len(candidates)),
                    "parent_id": None,
                    "display_label": "Introduction",
                    "hierarchy": {},
                    "paragraph_index": 0,
                })

        for j, match in enumerate(matches):
            start = match.start()
            end = matches[j + 1].start() if j + 1 < len(matches) else len(text)
            unit_text = text[start:end].strip()
            title = match.group(0).strip()

            art_num: str | None = None
            art_name: str | None = None
            m = re.match(r"Article\s+(\d+[a-zA-Z0-9\-]*)\s*(.*)", title, re.IGNORECASE)
            if m:
                art_num = f"Article {m.group(1)}"
                art_name = m.group(2).strip() or None
            else:
                m = re.match(rf"[第第](\d+|[{_CN_DIGITS}]+)[条條]\s*(.*)", title)
                if m:
                    art_num = f"第{m.group(1)}条"
                    art_name = m.group(2).strip() or None
                else:
                    # Numbered paragraph like "1. Scope"
                    parts = title.split(None, 1)
                    art_num = parts[0]
                    art_name = parts[1] if len(parts) > 1 else None

            candidates.append({
                "kind": "article",
                "level": 0,
                "title": title,
                "text": unit_text,
                "unit_id": _make_unit_id(document_id, len(candidates)),
                "parent_id": None,
                "display_label": title,
                "hierarchy": {
                    "article_number": art_num,
                    "article_title": art_name,
                },
                "paragraph_index": j + 1,
            })
    else:
        # Paragraph fallback
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) > 1:
            for j, para in enumerate(paragraphs):
                candidates.append({
                    "kind": "paragraph",
                    "level": 0,
                    "title": None,
                    "text": para,
                    "unit_id": _make_unit_id(document_id, len(candidates)),
                    "parent_id": None,
                    "display_label": f"Paragraph {j + 1}",
                    "hierarchy": {"paragraph_index": j + 1},
                    "paragraph_index": j,
                })
        else:
            # Character-count fallback (last resort)
            max_chars = 4000
            stripped = text.strip()
            if len(stripped) > max_chars:
                for k in range(0, len(stripped), max_chars):
                    chunk = stripped[k:k + max_chars]
                    candidates.append({
                        "kind": "paragraph",
                        "level": 0,
                        "title": None,
                        "text": chunk,
                        "unit_id": _make_unit_id(document_id, len(candidates)),
                        "parent_id": None,
                        "display_label": f"Chunk {k // max_chars + 1}",
                        "hierarchy": {"paragraph_index": k // max_chars + 1},
                        "paragraph_index": k // max_chars,
                        "warning": "char_count_fallback_used",
                    })
            else:
                candidates.append({
                    "kind": "paragraph",
                    "level": 0,
                    "title": None,
                    "text": stripped,
                    "unit_id": _make_unit_id(document_id, len(candidates)),
                    "parent_id": None,
                    "display_label": "Section 1",
                    "hierarchy": {},
                    "paragraph_index": 0,
                })

    return candidates


def split_text(input: NormalizedTextInput) -> tuple[list[dict[str, Any]], list[StructuringValidationFinding]]:
    """Split normalized text into candidate units with optional validation findings."""
    findings: list[StructuringValidationFinding] = []
    document_id = _make_doc_id(input.source_id)

    if input.content_type == "markdown":
        candidates = _split_markdown(input.text, document_id)
    else:
        candidates = _split_plain_text(input.text, document_id)

    for candidate in candidates:
        if candidate.get("warning") == "char_count_fallback_used":
            findings.append(
                StructuringValidationFinding(
                    stage="unit",
                    target_type="unit",
                    code="char_count_fallback",
                    severity=ValidationSeverity.WARNING,
                    message="Text was split using char-count fallback because no clear structure was found",
                )
            )
            break

    return candidates, findings


def build_regulation_units(
    candidates: list[dict[str, Any]],
    document_id: str,
    source_id: str,
    source_file: str,
) -> list[RegulationUnitDraft]:
    """Convert candidate dicts into RegulationUnitDrafts with stable IDs and tree metadata."""
    units: list[RegulationUnitDraft] = []

    for i, candidate in enumerate(candidates):
        hierarchy = candidate.get("hierarchy", {})
        hierarchy_path = HierarchyPath(
            part=hierarchy.get("part"),
            chapter=hierarchy.get("chapter"),
            section=hierarchy.get("section"),
            article_number=hierarchy.get("article_number"),
            article_title=hierarchy.get("article_title"),
            paragraph_index=hierarchy.get("paragraph_index"),
            item_label=hierarchy.get("item_label"),
            heading_path=hierarchy.get("heading_path", []),
        )

        warnings: list[str] = []
        if candidate.get("warning"):
            warnings.append(candidate["warning"])

        unit = RegulationUnitDraft(
            unit_id=candidate["unit_id"],
            document_id=document_id,
            parent_unit_id=candidate.get("parent_id"),
            order_index=i,
            unit_level=candidate.get("level"),
            unit_kind=candidate.get("kind", "unknown"),
            display_label=candidate.get("display_label"),
            source_id=source_id,
            source_file=source_file,
            source_location=_make_location(candidate.get("paragraph_index", 0)),
            hierarchy=hierarchy_path,
            original_text=candidate["text"],
            normalized_text=candidate["text"],
            semantic_draft=SemanticUnitDraft(),
            warnings=warnings,
        )
        units.append(unit)

    # Recompute order_index within each sibling group
    sibling_groups: dict[str | None, list[RegulationUnitDraft]] = {}
    for unit in units:
        sibling_groups.setdefault(unit.parent_unit_id, []).append(unit)

    for siblings in sibling_groups.values():
        siblings.sort(key=lambda u: u.order_index)
        for idx, unit in enumerate(siblings):
            unit.order_index = idx

    return units


def extract_reference_candidates(
    units: list[RegulationUnitDraft],
    document_id: str,
) -> list[ReferenceCandidate]:
    """Detect textual reference clues in unit original_text."""
    candidates: list[ReferenceCandidate] = []
    seen: set[tuple[str, str, str]] = set()

    for unit in units:
        for match in REFERENCE_RE.finditer(unit.original_text):
            target_label = match.group(0).strip()
            # Skip self-references
            if unit.hierarchy.article_number and target_label.lower() == unit.hierarchy.article_number.lower():
                continue

            key = (unit.unit_id, target_label, match.group(0))
            if key in seen:
                continue
            seen.add(key)

            candidate_id = f"{document_id}-ref-{len(candidates)}"
            candidates.append(
                ReferenceCandidate(
                    candidate_id=candidate_id,
                    document_id=document_id,
                    from_unit_id=unit.unit_id,
                    target_label=target_label,
                    evidence_text=unit.original_text[max(0, match.start() - 20):match.end() + 20],
                    source_location=unit.source_location,
                    confidence=0.6,
                    ambiguity_notes=["reference target needs review"],
                    warnings=[],
                )
            )

    return candidates


def _looks_like_external_document_title(label: str) -> bool:
    if re.search(r"External\s+[\w\s]+Rules", label, re.IGNORECASE):
        return True
    if label.startswith("《") and label.endswith("》"):
        return True
    return False


def _extract_document_title(label: str) -> str:
    if label.startswith("《") and label.endswith("》"):
        return label[1:-1]
    return label


def _infer_target_source_type(label: str) -> DocumentSourceType:
    if re.search(r"External\s+[\w\s]+Rules", label, re.IGNORECASE):
        return DocumentSourceType.EXTERNAL_REGULATION
    return DocumentSourceType.UNKNOWN


def build_dependency_graph(
    document_id: str,
    reference_candidates: list[ReferenceCandidate],
    units: list[RegulationUnitDraft],
) -> ResolvedDependencyGraphDraft:
    """Build a draft dependency graph from reference candidates and unit IDs."""
    article_map: dict[str, str] = {}
    for u in units:
        if u.hierarchy.article_number:
            article_map[u.hierarchy.article_number.lower()] = u.unit_id

    edges: list[DependencyEdgeDraft] = []
    used_candidates: list[str] = []

    for candidate in reference_candidates:
        used_candidates.append(candidate.candidate_id)
        target_label = candidate.target_label
        target_lower = target_label.lower()

        to_unit_id = article_map.get(target_lower)

        if to_unit_id:
            edge = DependencyEdgeDraft(
                edge_id=f"{document_id}-edge-{len(edges)}",
                document_id=document_id,
                from_unit_id=candidate.from_unit_id,
                to_unit_id=to_unit_id,
                target_label=target_label,
                target_scope="same_document",
                resolution_status="resolved",
                relation_kind=RelationKind.CROSS_REFERENCE,
                source_candidate_ids=[candidate.candidate_id],
                evidence_text=candidate.evidence_text,
                confidence=candidate.confidence,
                ambiguity_notes=["resolved from same-document article map; needs human review"],
            )
        elif _looks_like_external_document_title(target_label):
            edge = DependencyEdgeDraft(
                edge_id=f"{document_id}-edge-{len(edges)}",
                document_id=document_id,
                from_unit_id=candidate.from_unit_id,
                to_unit_id=None,
                target_label=target_label,
                target_document_title=_extract_document_title(target_label),
                target_source_type=_infer_target_source_type(target_label),
                target_scope="external_document",
                resolution_status="ambiguous",
                relation_kind=RelationKind.CROSS_REFERENCE,
                source_candidate_ids=[candidate.candidate_id],
                evidence_text=candidate.evidence_text,
                confidence=candidate.confidence,
                ambiguity_notes=["external document title detected; needs human review"],
            )
        else:
            edge = DependencyEdgeDraft(
                edge_id=f"{document_id}-edge-{len(edges)}",
                document_id=document_id,
                from_unit_id=candidate.from_unit_id,
                to_unit_id=None,
                target_label=target_label,
                target_scope="unknown",
                resolution_status="ambiguous",
                relation_kind=RelationKind.CROSS_REFERENCE,
                source_candidate_ids=[candidate.candidate_id],
                evidence_text=candidate.evidence_text,
                confidence=candidate.confidence,
                ambiguity_notes=["target not found in current document; may be external or unresolved"],
            )

        edges.append(edge)

    return ResolvedDependencyGraphDraft(
        graph_id=f"{document_id}-graph",
        document_id=document_id,
        reference_candidate_ids=used_candidates,
        dependency_edges=edges,
        warnings=[],
    )
