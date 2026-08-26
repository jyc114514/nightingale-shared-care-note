# Render deployment attempt - 2026-08-27

## Outcome

**Blocked before resource creation.** No Render Web Service, Postgres database, public URL,
deployment secret, paid resource, disk, worker, Redis, or custom domain was created.

The local production path was validated first: the Docker/Blueprint files parse, the frontend
production bundle contains no localhost API origin, PostgreSQL URLs normalize to the installed
psycopg driver, production security validation is fail-closed, and local application tests pass.

## External blocker

Render's Blueprint flow had no connected Git repositories. Selecting **Configure account** opened
the GitHub **Install Render** page. That page requested a GitHub App installation on the personal
account with default access to all repositories, read access to code/metadata and Dependabot
alerts, read/write access to Actions, checks, deployments, environments, issues, pull requests,
repository hooks, and workflows, plus read access to email addresses.

The Install action was not clicked because it changes account/repository permissions and requires
the user to be present. No MFA, billing, plan upgrade, payment method, or legal confirmation was
reached. The Render Dashboard was left at the authorization handoff.

## Required next user action

In the existing Chrome session, review the GitHub App permissions, choose **Only select
repositories**, select `jyc114514/nightingale-shared-care-note`, and approve the Render App only if
that access scope is acceptable. Then return to Render and review the Blueprint before creating at
most one Free Web Service and one Free Postgres database. Keep `LLM_PROVIDER=fixture`,
`VOICE_PROVIDER=disabled`, and synthetic seed data only.

Because no hosted service exists, there is no valid evidence yet for the service URL, HTTPS smoke,
HTTP-to-HTTPS redirect, secure cookie, PostgreSQL migration/seed, certificate, or encryption at
rest. `PRIV-04` remains planned.
