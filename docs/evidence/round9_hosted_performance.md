# Round 9 hosted performance evidence

Status: **PARTIAL — AUTHENTICATED HOSTED BENCHMARK PENDING**

The repaired Render service is healthy, but no authenticated Glance or Patient read-path
benchmark was executed. The available Chrome control surface allowed UI canaries but did not
provide a safe page-request API for a bounded benchmark without extracting browser cookies or
tokens. The password file was not read, no password/token was printed, and no credential was
inserted into a benchmark script.

The anonymous transport watch is recorded here only as deployment evidence:

- HTTP health redirect: `301` to HTTPS.
- HTTPS health: `200`.
- Sustained health/root/current-asset watch: **15/15**, zero failures, zero observed 5xx.
- It is not a warm Glance benchmark and must not be reported as a clinical or production SLA.

Machine-readable record: [`round9_hosted_performance.json`](round9_hosted_performance.json).
The exact deployed commit and Render service are in
[`round9_render_live.md`](round9_render_live.md).
