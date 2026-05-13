from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from arbiter.schemas.regulation_structuring import SECRET_PATTERN, StructuringPipelineOutput


class UnsafeExportError(ValueError):
    pass


ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^/((mnt|home|Users|var|tmp|etc)/|[A-Za-z]/))|(^[A-Za-z]:\\)"
)
FULL_PROMPT_PATTERN = re.compile(r"(full prompt|system prompt|developer prompt)", re.IGNORECASE)
PROVIDER_PAYLOAD_PATTERN = re.compile(r'("choices"\s*:|"messages"\s*:|"usage"\s*:)', re.IGNORECASE)
RAW_SENSITIVE_PATTERN = re.compile(r"RAW_SENSITIVE_TEXT", re.IGNORECASE)


def assert_sanitized_for_export(value: Any) -> None:
    _scan(value)


def to_json(output: StructuringPipelineOutput | dict[str, Any], *, indent: int = 2) -> str:
    bundle = (
        output
        if isinstance(output, StructuringPipelineOutput)
        else StructuringPipelineOutput.model_validate(output)
    )
    assert_sanitized_for_export(bundle)
    return bundle.model_dump_json(indent=indent)


def from_json(raw: str) -> StructuringPipelineOutput:
    return StructuringPipelineOutput.model_validate_json(raw)


def write_json(output: StructuringPipelineOutput | dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(to_json(output), encoding="utf-8")


def read_json(path: str | Path) -> StructuringPipelineOutput:
    return from_json(Path(path).read_text(encoding="utf-8"))


def _scan(value: Any) -> None:
    if isinstance(value, BaseModel):
        _scan(value.model_dump(mode="json"))
        return
    if isinstance(value, dict):
        for item in value.values():
            _scan(item)
        return
    if isinstance(value, list):
        for item in value:
            _scan(item)
        return
    if isinstance(value, str):
        _scan_string(value)


def _scan_string(value: str) -> None:
    checks = (
        (SECRET_PATTERN, "secret-like value"),
        (FULL_PROMPT_PATTERN, "full prompt text"),
        (PROVIDER_PAYLOAD_PATTERN, "provider payload"),
        (ABSOLUTE_PATH_PATTERN, "absolute local path"),
        (RAW_SENSITIVE_PATTERN, "unnecessary raw sensitive text"),
    )
    for pattern, label in checks:
        if pattern.search(value):
            raise UnsafeExportError(f"Export contains {label}")


__all__ = [
    "UnsafeExportError",
    "assert_sanitized_for_export",
    "from_json",
    "read_json",
    "to_json",
    "write_json",
]
