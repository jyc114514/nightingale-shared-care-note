# Production image: build the React SPA, then serve it from the FastAPI service.
FROM node:24-bookworm-slim AS frontend-build

WORKDIR /workspace/frontend
RUN corepack enable && corepack prepare pnpm@11.22.0 --activate
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY backend/requirements.lock ./backend/requirements.lock
RUN python -m pip install --no-cache-dir --requirement ./backend/requirements.lock
COPY backend/ ./backend/
COPY scripts/render_entrypoint.sh ./scripts/render_entrypoint.sh
COPY --from=frontend-build /workspace/frontend/dist ./backend/app/static/
RUN chmod +x ./scripts/render_entrypoint.sh

WORKDIR /app/backend
EXPOSE 10000
ENTRYPOINT ["/app/scripts/render_entrypoint.sh"]
