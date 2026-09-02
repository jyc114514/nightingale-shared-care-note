# PHI and credential logging boundary

Round 3 hardens the local application logging path. It does not certify the retention behavior of
Render, Uvicorn host logs, or any third-party provider.

| Boundary | Allowed | Explicitly excluded | Evidence status |
| --- | --- | --- | --- |
| Application safe events | Closed event code, request/clinic/patient opaque IDs, entity ID/type, provider label, safe status/error code, bounded duration/retry counts, input hash, replacement categories/counts, circuit state | Request/response body, note/comment/quote/transcript, patient name, Singapore ID, phone, cookie, token, API key, database URL | Local implementation and negative tests passed |
| Database audit rows | Actor/entity IDs, role, action, request ID, version metadata | Content and provider response | Existing metadata-only schema retained |
| SSE collaboration events | Event ID, resource type/opaque ID, event kind, actor metadata | Titles, bodies, source text, patient name | Existing metadata-only tests passed |
| Uvicorn/application exception boundary | HTTP method, path without query string, generic error code, request ID | Exception string, traceback with request data, headers/Cookie, query string | Local middleware and test passed |
| Render/host access logs | Host-controlled operational records | Not controllable from this repository | Retention and exact host configuration: **Unknown** |
| Optional DeepSeek boundary | Typed redacted synthetic payload only | Raw text/identifiers, source reference, cookies, keys, raw provider response | Local MockTransport boundary tests passed; provider retention: **Unknown** |

## Defense in depth

`safe_event()` has an explicit keyword signature and closed event/error vocabularies. It rejects
arbitrary dictionaries and unbounded strings. A process-wide record factory and filter sanitize
common Singapore IDs, phones, configured synthetic names, bearer/API-key patterns, credentialed
database URLs, cookies, and control characters. If the sanitizer itself fails, the entire message
becomes `log_sanitization_failed` and exception details are removed.

The sanitizer cannot recognize every natural-language name. The primary defense is therefore the
allowlist and schema boundary, not name detection alone. The local script below audits only the
explicit paths supplied to it; it never recursively scans a home directory or repository.

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m app.scripts.audit_phi_logs path\to\application.log --known-name "Sarah Tan"
Pop-Location
```

Clean input exits `0`; a detected category or unreadable input exits non-zero and reports only file,
category, hit count, and line count. No matched value is printed.
