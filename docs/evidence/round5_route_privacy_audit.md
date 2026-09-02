# Round 5 route and privacy audit

This is a safe structured inventory of the FastAPI application at the Round 5 candidate
checkpoint `39ab0f0`. It records route shape and authorization behavior, not request payloads or
secrets.

## Inventory summary

- OpenAPI-visible API routes inspected: **54**.
- Every protected application API route requires the authenticated HttpOnly session dependency;
  the only deliberate data-plane exception is `POST /auth/login`, the authentication bootstrap.
  `/health` and SPA root/static fallback are non-data health/serving routes.
- All state-changing routes inspected have `require_allowed_origin` as a route dependency.
- Patient-facing response families are limited to patient entry/timeline and the typed
  `published-care` projection; internal routes call `require_internal` or a stricter role check.
- No database URL, API key, cookie, password value, raw provider response, or note body is emitted
  by this inventory.

## Round 1–4 route matrix

| Surface and routes | Authentication/scope | Role policy | Write Origin guard | Patient/admin policy | Audit/event and safe-error boundary |
| --- | --- | --- | --- | --- | --- |
| `GET /patients/{id}/clinical-conflicts`, `GET /clinical-conflicts/{id}`, `GET /clinical-assertions/{id}/source` | session + patient/clinic scope | internal read | n/a | Patient denied; Admin read-only | source validation returns safe 404/422; no raw logs |
| `PATCH /clinical-conflicts/{id}/adjudicate` | session + conflict patient/clinic scope | Clinician only | yes | Patient/Staff/Admin denied | version CAS, metadata audit and invalidation event, safe 409 |
| `POST /patients/{id}/glance-impressions`, `GET /patients/{id}/glance-impressions/summary` | session + clinic/patient scope | internal only | POST yes | Patient denied; Admin read-only telemetry | metadata-only impression rows; payload conflicts use safe 409/422 |
| `POST /patients/{id}/ai-processing`, `GET /ai-processing/{id}` | session + clinic/patient scope | Staff/Clinician submit/read; internal read | POST yes | Patient denied; provider info excludes key/base URL | redaction/provider boundary, safe provider errors, job audit/events |
| `GET /ai-processing/provider`, `GET /patients/{id}/ai-processing/provider-status` | session; membership or patient/clinic scope | provider info Staff/Clinician; status internal | n/a | Patient denied; Admin status is read-only | safe provider metadata only; no response/key logging |
| `POST /entries/{source}/patient-publications` | session + source Entry clinic/patient scope | Staff/Clinician prepare | yes | Patient/Admin denied | creates draft/version/evidence and metadata event; safe 404/422 |
| `GET /patients/{id}/patient-publications`, `GET /patient-publications/{id}` | session + publication clinic/patient scope | internal read; Admin oversight | n/a | Patient denied | internal detail contains source/version evidence only inside scope |
| `PATCH /patient-publications/{id}` | session + publication scope | Staff/Clinician edit draft/approved; Admin read-only | yes | Patient denied | append-only content version, approval invalidation, workflow CAS 409 |
| `POST /patient-publications/{id}/approve` | session + publication scope | Clinician only | yes | Patient/Staff/Admin denied | dosage/source checks, exact approval version, audit/event, safe 409/422 |
| `POST /patient-publications/{id}/publish` | session + publication scope | Clinician only | yes | Patient/Staff/Admin denied | repeats source/dosage/CAS checks; portal state only, no delivery |
| `POST /patient-publications/{id}/recall` | session + publication scope | Clinician only | yes | Patient/Staff/Admin denied | safe reason code, withdrawal notice, audit/event, no external recall |
| `POST /patient-publications/{id}/corrections` | session + publication scope | Clinician only | yes | Patient/Staff/Admin denied | linked draft; corrected publish supersedes old state atomically |
| `GET /patients/{id}/published-care` | session + patient/clinic scope | safe projection | n/a | Patient sees own current published items/notices; no internal fields | no workflow/source IDs, comments, tasks, assertions, conflicts, impressions or provider status |
| `GET /patients/{id}/timeline` and `GET /patients/{id}/entries` | session + patient/clinic scope | internal full projection; Patient safe types only | n/a | Patient sees summaries/instructions only | legacy path preserved; no raw AI/internal comments |
| Entry, comments, tasks, Voice, SSE and source routes | session + scope; route-specific internal checks | existing Round 1–3 role matrix | all writes yes | Patient privacy checks retained by prior suites | existing immutable/CAS/event/source validation retained |

## Reconciled semantic distinctions

| Potential confusion | Release-candidate rule |
| --- | --- |
| Accepted vs Published | Highlight Accept changes only an internal suggestion; it never creates a PatientPublication. |
| Write conflict vs semantic conflict | Entry/task/publication workflow versions use CAS; clinical allergy conflicts use a separate adjudication state. |
| Risk vs priority vs safety floor | Explicit risk, Glance display priority, and protected safety floor remain separate fields. |
| Provider failure vs fixture fallback | Provider failure remains visible/degraded; it does not silently return fixture output. |
| Impression logging vs debiasing | Impressions provide bounded denominators/metadata; no inverse-propensity or fairness claim is made. |
| Internal vs patient-facing | Patient projection filters server-side; publication does not flip internal Entry visibility. |
| Recall vs external delivery | Recall removes portal content only; no external message was sent, so no external recall/receipt exists. |
| SQLite vs PostgreSQL | SQLite fresh/legacy tests and PostgreSQL offline SQL remain separate evidence; Round 6 now adds real PostgreSQL 18 CI execution evidence. |
| Portal visibility vs communication receipt | `PUBLISHED` means visible in this portal projection, not delivered or read by a patient. |

## Known integration limitations

- Fresh PostgreSQL offline SQL generation from `base:head` is blocked by the pre-existing
  `0003_gate_b_repair` offline `inspect()` call. Targeted PostgreSQL offline SQL from
  `0010_postgres_compat` through `0014_patient_publications` succeeds, contains the publication
  tables/self-references, and contains no SQLite batch temp-table token.
- No Docker/Podman/local PostgreSQL runtime is available on this host. The new workflow is ready
  but has not run in GitHub Actions during Round 5 because push/external CI is not authorized.
- The existing `.env.example` is a placeholder template only; it is not a credential file.
- The 13 old `.pytest-tmp-round*` directories are test-generated but ACL-protected. They are
  ignored and were not force-deleted or ownership-modified.
