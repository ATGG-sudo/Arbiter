from __future__ import annotations

from typing import Any

from arbiter.llm import ModelProvider
from arbiter.schemas.regulation_structuring import (
    DependencyEdgeDraft,
    DocumentClassificationDraft,
    ReferenceCandidate,
    RegulationUnitDraft,
    SemanticUnitDraft,
    StructuringValidationFinding,
    ValidationSeverity,
)


class LLMExtractionWrapper:
    """Thin wrapper for LLM-assisted extraction through a provider object.

    The provider must expose a ``structured_output(schema=..., prompt=...,
    context=...)`` method. This wrapper constructs bounded prompts from
    document text and unit content, validates returned payloads against
    Pydantic schemas, and converts validation failures into structured
    findings rather than silently accepting invalid data.
    """

    def __init__(self, provider: ModelProvider) -> None:
        self.provider = provider
        self.findings: list[StructuringValidationFinding] = []
        self.validated_call_count: int = 0

    def _call_or_find(
        self,
        schema: type[Any],
        prompt: str,
        context: dict[str, Any] | None,
        error_context: str,
        *,
        stage: str = "semantic",
        target_type: str = "semantic_draft",
        target_id: str | None = None,
    ) -> Any | None:
        try:
            raw = self.provider.structured_output(
                schema=schema,
                prompt=prompt,
                context=context or {},
            )
            if raw is None:
                return None
            # Provider may return a validated instance or a raw dict. Anything
            # else, including a different Pydantic model, must be revalidated
            # against the requested schema before it enters pipeline output.
            if isinstance(raw, schema):
                result = raw
            else:
                result = schema.model_validate(raw)
            self.validated_call_count += 1
            return result
        except Exception as exc:
            self.findings.append(
                StructuringValidationFinding(
                    stage=stage,
                    target_type=target_type,
                    target_id=target_id,
                    code="llm_schema_validation_failure",
                    severity=ValidationSeverity.WARNING,
                    message=f"{error_context}: {exc}",
                )
            )
            return None

    def _build_classification_prompt(
        self, document_title: str | None, document_text: str
    ) -> str:
        preview = document_text[:2000]
        return (
            "Classify the following regulation document into a structured draft.\n\n"
            f"Title: {document_title or 'Unknown'}\n\n"
            f"Text preview (first {len(preview)} characters):\n{preview}"
        )

    def _build_semantic_prompt(self, display_label: str | None, unit_text: str) -> str:
        preview = unit_text[:3000]
        return (
            "Extract semantic structure from the following regulation unit.\n\n"
            f"Label: {display_label or 'Unknown'}\n\n"
            f"Text (first {len(preview)} characters):\n{preview}"
        )

    def _build_dependency_prompt(
        self, document_id: str, candidates: list[ReferenceCandidate]
    ) -> str:
        lines = "\n".join(
            f"- target='{c.target_label}' from_unit={c.from_unit_id}"
            for c in candidates[:20]
        )
        return (
            f"Propose dependency edges for document {document_id}.\n\n"
            f"Reference candidates ({len(candidates)} total, showing up to 20):\n{lines}"
        )

    def enrich_classification(
        self,
        draft: DocumentClassificationDraft,
        document_title: str | None,
        document_text: str,
    ) -> DocumentClassificationDraft:
        prompt = self._build_classification_prompt(document_title, document_text)
        context = {
            "document_title": document_title,
            "text_length": len(document_text),
        }
        result = self._call_or_find(
            DocumentClassificationDraft,
            prompt,
            context,
            "LLM classification enrichment failed schema validation",
            stage="document",
            target_type="document",
        )
        if result is not None:
            return result
        return draft

    def enrich_semantic_draft(
        self,
        unit: RegulationUnitDraft,
    ) -> RegulationUnitDraft:
        prompt = self._build_semantic_prompt(unit.display_label, unit.original_text)
        context = {
            "unit_id": unit.unit_id,
            "text_length": len(unit.original_text),
        }
        result = self._call_or_find(
            SemanticUnitDraft,
            prompt,
            context,
            f"LLM semantic enrichment for unit {unit.unit_id} failed schema validation",
            stage="semantic",
            target_type="semantic_draft",
            target_id=unit.unit_id,
        )
        if result is not None:
            unit.semantic_draft = result
        return unit

    def propose_dependency_edges(
        self,
        document_id: str,
        reference_candidates: list[ReferenceCandidate],
        units: list[RegulationUnitDraft],
    ) -> list[DependencyEdgeDraft]:
        if not reference_candidates:
            return []
        prompt = self._build_dependency_prompt(document_id, reference_candidates)
        context = {
            "document_id": document_id,
            "candidate_count": len(reference_candidates),
        }
        result = self._call_or_find(
            DependencyEdgeDraft,
            prompt,
            context,
            "LLM dependency edge proposal failed schema validation",
            stage="dependency",
            target_type="dependency_edge",
        )
        if result is not None:
            return [result]
        return []
