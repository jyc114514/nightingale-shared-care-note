# Round 3 safe-failure design

Date: 2026-09-02

Scope: local synthetic prototype only. The design preserves canonical records, the existing
materialized Glance read path, timeline, tasks, comments, and immutable source navigation when an
optional external AI provider fails. Fixture mode remains deterministic and bypasses the external
provider circuit.

## Failure classes

| Failure | Retry? | Counts toward circuit? | Job/UI result | Workspace result | Safe event |
| --- | --- | --- | --- | --- | --- |
| Redaction failure / detector failure | No | No | `failed_redaction`; no provider call | Existing records remain usable | `ai_redaction_failed` |
| Provider configuration/auth/balance failure | No | No threshold increment; status is unavailable | `failed_provider`; no source | Existing records remain usable | `ai_provider_failed` |
| Per-attempt timeout | Bounded retry until total deadline | Yes | `failed_provider` | Existing records remain usable | `ai_provider_failed` |
| Connection error / transient 5xx | Bounded retry until total deadline | Yes | `failed_provider` | Existing records remain usable | `ai_provider_failed` |
| 429 rate limit | No blind retry | Yes, as a provider availability failure | `failed_provider` | Existing records remain usable | `ai_provider_failed` |
| Persistent 503 / repeated transport failure | Bounded per request; then circuit opens at 3 failures | Yes | `failed_provider`; later calls fail fast | Existing records remain usable | circuit transition + safe failure |
| Invalid/truncated/ambiguous provider output | No | No threshold increment | `failed_provider`; no source | Existing records remain usable | `ai_provider_failed` |
| Provenance failure after valid provider output | No | No | `failed_provenance`; no fabricated highlight | Canonical data is never overwritten | `ai_provider_failed` |
| Unexpected internal exception | No | No | generic HTTP 500 at boundary | Existing records remain usable | `request_internal_error` |

The failure code is a closed internal vocabulary. Raw request text, response bodies, exception
strings, URLs with query strings, cookies, tokens, names, IDs, phones, and database credentials are
never log fields. A provider failure never silently falls back to the fixture and never creates a
fake suggestion.

## Total provider budget

The optional DeepSeek adapter uses an 8-second per-attempt timeout, a 12-second total monotonic
budget, and at most two attempts. The second attempt receives only the remaining deadline. Timeout,
connection, and transient 5xx failures are retryable; auth, balance, 429, invalid output, and
provenance failures are not blindly retried. These values are bounded prototype controls, not a
clinical SLA. Tests use `MockTransport`/patched clocks and do not sleep for 45 seconds.

## Circuit semantics

The circuit is persisted per `(clinic_id, provider_name)` in `ai_provider_circuits`; it is not a
process-local global. The default threshold is three counted failures and the cooldown is 60
seconds.

- **Closed:** external calls are allowed. Counted failures increment the consecutive count; a
  success resets it. The third counted failure moves the row to Open.
- **Open:** calls fail fast with `provider_circuit_open` while cooldown remains. The response exposes
  only a bounded retry-after value. Existing care data remains available.
- **Half-open:** after cooldown, one database compare-and-swap transition reserves one probe. Other
  workers fail fast while the probe is in flight. A valid provider result closes and resets the
  circuit; a failure reopens it for another cooldown.

State/version updates use database conditional updates. A race that loses the CAS does not issue a
second probe. The persistence is safe at the bounded database-CAS level; this prototype does not
claim a distributed queue or perfect cross-region incident coordination.

Counted failures are `provider_timeout`, `provider_unavailable`, and `provider_rate_limited`.
Configuration, auth, balance, bad request, invalid output, redaction, and provenance failures are
observed safely but do not turn model-quality or local-input errors into an outage threshold.

## Logging semantics

`app/observability/safe_logging.py` exposes `safe_event(logger, event_code, ...)` with a closed event
set and an explicit field allowlist. Values are primitive, length-bounded, control-character
sanitized, and serialized as stable JSON. Unknown keyword fields, arbitrary dictionaries, exception
objects, and free-form messages are programming errors. The second-layer logging filter sanitizes
IDs, phones, configured synthetic names, bearer/API-key patterns, database credential URLs, and
CRLF injection; if sanitization itself fails, the whole message becomes
`log_sanitization_failed` and exception details are discarded.

The AI event order is:

1. `ai_job_created`
2. `ai_redaction_completed`
3. `ai_provider_call_started`
4. `ai_provider_call_completed` or `ai_provider_failed`
5. `ai_provenance_completed` only after an immutable source is persisted

Redaction failure stops before step 3. DB audit and SSE events remain metadata-only and are not a
replacement for application logs. The local audit script scans only explicit user-supplied log
paths. Uvicorn access logging is limited to method/path/status metadata; query strings are not
used by this feature, and third-party/host retention remains **Unknown**.

## Explicit non-goals

- no durable queue, external worker, or automatic replay;
- no cached generated fallback, fake AI card, or silent fixture fallback;
- no production incident-response, third-party retention, or PHI-certification claim;
- no change to Voice, DeepSeek live calls, allergy vocabulary, patient publication, RLS, deployment,
  or the existing Glance ranking semantics.
