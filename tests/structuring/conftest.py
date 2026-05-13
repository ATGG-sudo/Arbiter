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
#   provider.structured_output(schema=<PydanticModel>, payload=<dict>) -> model
class MockModelProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def structured_output(self, *, schema: Callable[..., Any], payload: dict[str, Any]) -> Any:
        self.calls.append({"schema": schema, "payload": payload})
        return schema.model_validate(payload)


class BlockingModelProvider:
    def structured_output(self, **_: Any) -> Any:
        raise AssertionError("Real model calls are forbidden in structuring tests")


@pytest.fixture
def mock_model_provider() -> MockModelProvider:
    return MockModelProvider()


@pytest.fixture
def blocking_model_provider() -> BlockingModelProvider:
    return BlockingModelProvider()
