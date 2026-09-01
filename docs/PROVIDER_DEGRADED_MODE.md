# Provider degraded mode

This page describes what an internal reviewer sees when the optional external AI provider is slow,
unavailable, misconfigured, or returns unusable output. It applies to the local synthetic prototype;
it is not a production incident-response or clinical-SLA document.

## What remains available

Existing canonical care records continue to be readable. Internal Staff and Clinician users can
continue to use the Glance View, timeline, immutable source links, history/diff/revert, comments,
tasks, and the protected allergy-conflict review path. Patient projection and its privacy boundary
are independent of provider availability.

## What the AI panel says

- **Available:** new AI-assisted suggestions may be submitted.
- **Degraded:** the provider has recently failed, but a new attempt is still allowed; the panel
  warns that AI-assisted updates are experiencing temporary failures.
- **Temporarily unavailable:** new suggestions are paused, a bounded retry-after is shown when
  available, and the panel says that existing care records, Glance items, tasks, comments, and
  source links remain available.

The `Check availability` action performs one bounded status read. It does not call the provider,
create a job, poll continuously, or replay a failed request. Technical failure codes are kept out
of the primary product surface.

## What is not generated

There is no silent switch to the fixture provider, empty/fake AI card, cached invented summary, or
automatic replay of a failed request. A failed job stores a safe status and error code, but no entry
or highlight is created from a failed provider response. Redaction or provenance failure also stops
the source-creation path.

## Circuit behavior

The external provider circuit is stored per clinic/provider:

1. Three counted transport failures open the circuit for 60 seconds.
2. Open requests fail fast with `provider_circuit_open` and do not call the provider.
3. After cooldown, one database-CAS half-open probe is allowed.
4. A valid result closes and resets the circuit; a failed probe reopens it.

The fixture provider bypasses this external circuit because it is local and deterministic. The
prototype has no durable queue, scheduled retry, or background worker, so a user must explicitly
submit a new request after recovery.

## Safety boundary

Only redacted synthetic text crosses the optional provider boundary. The UI does not expose keys,
base URLs, provider response bodies, raw exception text, patient names, internal comments, or
patient-facing outage details. Provider status is an internal, patient-scoped read and is denied to
the Patient role.
