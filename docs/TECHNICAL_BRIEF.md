# Nightingale technical brief — Phase 0 skeleton

> This is a structure-only brief. It deliberately does not claim that deferred product
> behavior exists.

## Architecture

Phase 0 scaffold: FastAPI backend, React/TypeScript/Vite frontend, Tailwind CSS styling,
TanStack Query for the shell's health request, and PostgreSQL/Alembic dependencies reserved
for a later gate. The frontend and backend run as separate local processes.

## Data schema

Not implemented in Phase 0. Future schema decisions belong to Gate A and must preserve clinic
scope, immutable entry versions, audit metadata, and synthetic-data boundaries.

## RBAC

Not implemented in Phase 0. Server-side authorization is a mandatory future gate; the shell has
no role switcher and no patient data.

## Provenance

Not implemented in Phase 0. Future AI-derived highlights must resolve to immutable source
versions and source spans.

## PHI redaction

Not implemented in Phase 0. The current repository contains no patient records and makes no
external LLM calls. A later gate must redact names, Singapore-style IC/ID values, and phones
before any provider call and fail closed on detector failure.

## Performance measurement

Not measured in Phase 0. The required warm Glance View P95 measurement belongs to a later gate;
the current `/health` response is not a Glance View benchmark.

## Assumptions and trade-offs

- The existing confirmed Conda environment is reused, even though it is Python 3.10.20 while
  the longer-term project plan targets Python 3.12.
- The scaffold avoids a database connection, hosted service, Docker, and external credentials.
- The frontend health request is a real request to the local backend, while all clinical screens
  remain deferred.

## Implemented versus deferred

Implemented: repository scaffold, dependency lockfiles, backend health endpoint and test,
frontend shell and unit test, lint/type-check/build commands, safe placeholders, and evidence
artifacts. Deferred: all product requirements and all bonus features.

