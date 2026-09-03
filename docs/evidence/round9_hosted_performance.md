# Round 9 hosted performance evidence

Status: **PARTIAL - AUTHENTICATED HOSTED BENCHMARK PENDING**

The exact closure deployment is healthy, but no authenticated Staff Glance or Patient read-path
benchmark was executed. The available Chrome control surface supports authenticated UI
observation but does not expose a safe same-origin page-request/performance API for the required
20 warm-up plus 200 measured requests at concurrency 5. Extracting browser cookies, storage,
passwords, or tokens is prohibited and was not attempted.

The current Staff UI canary is recorded separately from latency:

- six-item Glance cap observed;
- protected allergy conflict observed first under `importance-v3-protected-first`;
- both immutable conflict sources opened;
- Staff read-only adjudication boundary observed;
- patient-publication Draft and immutable evidence observed;
- no write was performed by this canary.

Anonymous transport/deployment evidence:

- HTTP health redirect: `301` to HTTPS.
- HTTPS health/root/current assets: `200`.
- Unauthenticated `/auth/me` and `/patients`: `401`.
- Sustained watch: **15/15**, zero failures, zero observed 5xx.

This is not a warm Glance benchmark and must not be reported as a clinical or production SLA.
Patient privacy, Clinician adjudication, and authenticated SSE were not re-run as exact-commit
closure canaries. `real-clinic-live1` therefore remains intentionally absent.

Machine-readable record: [`round9_hosted_performance.json`](round9_hosted_performance.json).
The exact deployed commit and UI/deployment observations are in
[`round9_closure.md`](round9_closure.md).
