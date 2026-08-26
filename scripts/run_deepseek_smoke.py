"""Run one bounded synthetic DeepSeek smoke; never print key, prompt, or response text."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

from app.ai.deepseek import DeepSeekProvider, ProviderError
from app.ai.schemas import RedactedPayload


def main() -> int:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    requested_at = datetime.now(timezone.utc).isoformat()
    if not key:
        print(
            json.dumps(
                {
                    "provider": "deepseek-v4-flash",
                    "model": "deepseek-v4-flash",
                    "requested_at": requested_at,
                    "http_category": "not_attempted",
                    "success": False,
                    "output_schema_valid": False,
                    "error_code": "provider_configuration_missing_key",
                },
                sort_keys=True,
            )
        )
        return 1

    started = time.perf_counter()
    try:
        with DeepSeekProvider(key, max_tokens=600) as provider:
            output = provider.process(
                RedactedPayload(
                    interaction_type="ai_nurse_consult_summary",
                    redacted_text=(
                        "Synthetic nurse follow-up: the scheduled laboratory review remains "
                        "pending. No diagnosis or treatment recommendation was made."
                    ),
                    source_reference="synthetic-live-smoke",
                )
            )
            usage = provider.last_usage
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        print(
            json.dumps(
                {
                    "provider": "deepseek-v4-flash",
                    "model": "deepseek-v4-flash",
                    "requested_at": requested_at,
                    "elapsed_ms": elapsed_ms,
                    "http_category": "2xx",
                    "success": True,
                    "output_schema_valid": True,
                    "quote_length": len(output.quote),
                    "token_usage": usage,
                },
                sort_keys=True,
            )
        )
        return 0
    except ProviderError as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        print(
            json.dumps(
                {
                    "provider": "deepseek-v4-flash",
                    "model": "deepseek-v4-flash",
                    "requested_at": requested_at,
                    "elapsed_ms": elapsed_ms,
                    "http_category": "provider_error",
                    "success": False,
                    "output_schema_valid": False,
                    "error_code": exc.error_code,
                },
                sort_keys=True,
            )
        )
        return 1
    except Exception:
        print(
            json.dumps(
                {
                    "provider": "deepseek-v4-flash",
                    "model": "deepseek-v4-flash",
                    "requested_at": requested_at,
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                    "http_category": "provider_error",
                    "success": False,
                    "output_schema_valid": False,
                    "error_code": "provider_unavailable",
                },
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
