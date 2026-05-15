from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from typing import Any

from arbiter.llm.base import SchemaT


Transport = Callable[[dict[str, Any], dict[str, str]], dict[str, Any]]


class OpenAICompatibleModelProvider:
    """Minimal OpenAI-compatible structured-output provider.

    Uses JSON Schema injection in the system prompt + client-side field
    stripping to enforce schema compliance on providers that do not support
    ``response_format: {type: "json_schema"}`` (e.g. DeepSeek).

    For providers that *do* support ``json_schema`` (e.g. OpenAI), the
    prompt-level schema still acts as a strong signal; the client-side strip
    serves as a second line of defence.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        request_options: dict[str, Any] | None = None,
        timeout_seconds: float = 30.0,
        transport: Transport | None = None,
        locale: str | None = "en",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_options = request_options or {}
        self.timeout_seconds = timeout_seconds
        self.locale = (locale or "en").strip().lower()
        self._transport = transport or self._urllib_transport

    def structured_output(
        self,
        *,
        schema: type[SchemaT],
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> SchemaT | None:
        original_schema = schema.model_json_schema()
        json_schema = original_schema
        reverse_maps: dict[str, dict[str, str]] | None = None
        translate_response_enums = None

        if self.locale != "en":
            from arbiter.llm.i18n_enums import (
                translate_response_enums,
                translate_schema_enums,
            )

            json_schema, reverse_maps = translate_schema_enums(original_schema)

        system_prompt = _build_schema_system_prompt(json_schema)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": _render_prompt(prompt, context or {}),
                },
            ],
            "response_format": {"type": "json_object"},
            **self.request_options,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = self._transport(payload, headers)
        content = _extract_message_content(response)
        if content is None:
            return None
        raw = json.loads(content) if isinstance(content, str) else content
        if reverse_maps and translate_response_enums:
            raw = translate_response_enums(raw, reverse_maps)
        if isinstance(raw, dict):
            raw = _strip_extra_fields(raw, original_schema, original_schema)
        return schema.model_validate(raw)

    def _urllib_transport(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


def _build_schema_system_prompt(json_schema: dict[str, Any]) -> str:
    schema_text = json.dumps(json_schema, indent=2, ensure_ascii=False)
    return (
        "You are a structured-data extractor.\n"
        "Your response must be a single JSON object and nothing else.\n"
        "Do NOT wrap the JSON in markdown code blocks.\n"
        "Do NOT include any fields that are not defined in the schema below.\n"
        "Do NOT add explanations, comments, or nested structures outside the schema.\n\n"
        "Schema:\n"
        f"{schema_text}"
    )


def _render_prompt(prompt: str, context: dict[str, Any]) -> str:
    if not context:
        return prompt
    return (
        f"{prompt}\n\n"
        "Context JSON:\n"
        f"{json.dumps(context, ensure_ascii=False, sort_keys=True)}"
    )


def _extract_message_content(response: dict[str, Any]) -> Any | None:
    choices = response.get("choices")
    if not choices:
        return None
    message = choices[0].get("message", {})
    return message.get("content")


# ---------------------------------------------------------------------------
# Client-side schema cleaning (removes fields not declared in the JSON Schema)
# ---------------------------------------------------------------------------

def _resolve_ref(ref: str, root: dict[str, Any]) -> dict[str, Any] | None:
    """Follow a JSON Schema \"$ref\" pointer within *root*."""
    if not ref.startswith("#/"):
        return None
    parts = ref[2:].split("/")
    current: Any = root
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current if isinstance(current, dict) else None


def _get_nested_schema(
    prop_schema: dict[str, Any] | None,
    root: dict[str, Any],
) -> dict[str, Any] | None:
    """Extract an object/array sub-schema from a property schema."""
    if not isinstance(prop_schema, dict):
        return None

    # Direct $ref
    ref = prop_schema.get("$ref")
    if ref:
        resolved = _resolve_ref(ref, root)
        if resolved:
            return resolved

    # Direct type
    t = prop_schema.get("type")
    if t in ("object", "array"):
        return prop_schema

    # anyOf / oneOf (e.g. str | None)
    for key in ("anyOf", "oneOf"):
        for sub in prop_schema.get(key, []):
            if not isinstance(sub, dict):
                continue
            st = sub.get("type")
            if st in ("object", "array"):
                return sub
            sr = sub.get("$ref")
            if sr:
                resolved = _resolve_ref(sr, root)
                if resolved:
                    return resolved

    return None


def _strip_extra_fields(
    value: Any,
    prop_schema: dict[str, Any] | None,
    root: dict[str, Any],
) -> Any:
    """Recursively remove keys that are not declared in the JSON Schema."""
    if not isinstance(value, dict):
        return value

    nested = _get_nested_schema(prop_schema, root)
    if not nested or nested.get("type") != "object":
        return value

    props = nested.get("properties", {})
    cleaned: dict[str, Any] = {k: v for k, v in value.items() if k in props}

    for key, val in cleaned.items():
        child_schema = props.get(key)
        child_nested = _get_nested_schema(child_schema, root)
        if not child_nested:
            continue

        if child_nested.get("type") == "object" and isinstance(val, dict):
            cleaned[key] = _strip_extra_fields(val, child_schema, root)
        elif child_nested.get("type") == "array" and isinstance(val, list):
            items_schema = child_nested.get("items", {})
            item_nested = _get_nested_schema(items_schema, root)
            if item_nested and item_nested.get("type") == "object":
                cleaned[key] = [
                    _strip_extra_fields(item, items_schema, root)
                    if isinstance(item, dict)
                    else item
                    for item in val
                ]

    return cleaned
