from __future__ import annotations

from typing import Any, Protocol, TypeVar

from pydantic import BaseModel


SchemaT = TypeVar("SchemaT", bound=BaseModel)


class ModelProvider(Protocol):
    """Structured-output provider boundary used by Arbiter admin modules."""

    def structured_output(
        self,
        *,
        schema: type[SchemaT],
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> SchemaT | None:
        """Return a schema-validated object or None when no proposal is available."""


class DisabledModelProvider:
    """Offline provider used when live model access is not configured."""

    def structured_output(
        self,
        *,
        schema: type[SchemaT],
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> SchemaT | None:
        return None
