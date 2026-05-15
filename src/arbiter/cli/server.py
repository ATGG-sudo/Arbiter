from __future__ import annotations

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

from dotenv import load_dotenv

from arbiter.llm.base import ModelProvider
from arbiter.llm.factory import build_model_provider
from arbiter.llm.settings import LLMProviderSettings
from arbiter.structuring.workbench_adapter import (
    run_structuring_from_markdown,
    StructuringRunRequest,
    StructuringRunResult,
)

# Load environment variables from .env in the repository root.
# This is safe because .env is gitignored and only affects the server process.
load_dotenv()


class LLMProviderNotConfigured(ValueError):
    pass


def _build_provider_for_request(
    request: StructuringRunRequest,
    settings: LLMProviderSettings | None = None,
) -> ModelProvider | None:
    if not request.llm_assisted or request.model_mode == "mock_provider":
        return None

    resolved = settings or LLMProviderSettings.from_env()
    if resolved.provider == "none":
        raise LLMProviderNotConfigured(
            "LLM-assisted parsing requires ARBITER_LLM_PROVIDER to be configured"
        )
    return build_model_provider(resolved)


class StructuringHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for the Admin structuring workbench endpoint.

    Uses only the standard library. Designed for local, controlled admin use.
    """

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        if self.path != "/api/structuring/run":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            content_len = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_len) if content_len > 0 else b"{}"
            body = json.loads(body_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"Invalid JSON: {exc}"})
            return

        request_id = body.get("request_id", "unknown")

        try:
            request = StructuringRunRequest.model_validate(body)
        except Exception as exc:
            self._send_json(
                422,
                {
                    "request_id": request_id,
                    "run_id": f"struct-run-{id(exc) & 0xFFFFFFFF:08x}",
                    "status": "validation_failed",
                    "output": None,
                    "errors": [{"code": "request_validation_failed", "message": str(exc)}],
                    "warnings": [],
                    "sanitized_trace": {},
                    "token_usage": None,
                    "completed_at": None,
                },
            )
            return

        try:
            provider = _build_provider_for_request(request)
            result = run_structuring_from_markdown(request, model_provider=provider)
            self._send_json(200, result.model_dump(mode="json"))
        except LLMProviderNotConfigured as exc:
            error_result = StructuringRunResult(
                request_id=request.request_id,
                run_id=f"struct-run-config-{id(exc) & 0xFFFFFFFF:08x}",
                status="failed",
                output=None,
                errors=[{"code": "llm_provider_not_configured", "message": str(exc)}],
                warnings=[],
                sanitized_trace={
                    "adapter": "001-structuring",
                    "model_call_count": 0,
                    "redaction_warnings": [],
                },
                token_usage=None,
                completed_at=None,
            )
            self._send_json(200, error_result.model_dump(mode="json"))
        except Exception as exc:
            error_result = StructuringRunResult(
                request_id=request.request_id,
                run_id=f"struct-run-error-{id(exc) & 0xFFFFFFFF:08x}",
                status="failed",
                output=None,
                errors=[{"code": "server_error", "message": str(exc)}],
                warnings=[],
                sanitized_trace={"adapter": "001-structuring", "error": str(exc)},
                token_usage=None,
                completed_at=None,
            )
            self._send_json(500, error_result.model_dump(mode="json"))

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress default request logging; admin server should stay quiet.
        pass


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), StructuringHandler)
    print(f"Admin structuring server listening on http://{host}:{port}")
    print(f"Endpoint: POST http://{host}:{port}/api/structuring/run")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    run_server(host=host, port=port)
