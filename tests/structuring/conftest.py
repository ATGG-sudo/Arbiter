from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest


# Phase 2 inspection note:
# This Spec Kit checkout currently has no production LLMClient / ModelProvider
# module under src/arbiter. These fixtures are test-local guardrails only. The
# future production LLM wrapper must adapt to the real project abstraction when
# it exists instead of introducing a parallel model access layer.
# Real import path found in this checkout: none.
# Test-local expected signature:
#   provider.structured_output(schema=<PydanticModel>, prompt=<str>, context=<dict>) -> model | None
class MockModelProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._responses: list[dict[str, Any] | None] = []

    def queue_response(self, payload: dict[str, Any] | None) -> None:
        """Queue a test payload to be returned on the next structured_output call."""
        self._responses.append(payload)

    def structured_output(
        self,
        *,
        schema: Callable[..., Any],
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> Any:
        self.calls.append({"schema": schema, "prompt": prompt, "context": context})
        if self._responses:
            payload = self._responses.pop(0)
            if payload is not None:
                return schema.model_validate(payload)
            return None
        return None


class BlockingModelProvider:
    def structured_output(self, **_: Any) -> Any:
        raise AssertionError("Real model calls are forbidden in structuring tests")


@pytest.fixture
def mock_model_provider() -> MockModelProvider:
    return MockModelProvider()


@pytest.fixture
def blocking_model_provider() -> BlockingModelProvider:
    return BlockingModelProvider()
