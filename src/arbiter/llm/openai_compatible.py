from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from typing import Any

from arbiter.llm.base import SchemaT


Transport = Callable[[dict[str, Any], dict[str, str]], dict[str, Any]]


class OpenAICompatibleModelProvider:
    """Minimal OpenAI-compatible structured-output provider.

    The provider is not used unless explicitly built through configuration or
    injected by a caller. Unit tests should use an injected transport.
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
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_options = request_options or {}
        self.timeout_seconds = timeout_seconds
        self._transport = transport or self._urllib_transport

    def structured_output(
        self,
        *,
        schema: type[SchemaT],
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> SchemaT | None:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": _render_prompt(prompt, context or {}),
                }
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
