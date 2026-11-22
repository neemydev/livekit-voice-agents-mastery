# syntax=docker/dockerfile:1
# Container image for the Bright Smile Dental receptionist agent.
# Spec: specs/dental_receptionist/001-first-agent/
# Based on LiveKit's uv template: https://docs.livekit.io/deploy/agents/builds.md
#
# Build it from the REPO ROOT, because the uv workspace (pyproject.toml + uv.lock) lives there.
# Docker Compose does that for us:   docker compose build dental_receptionist

ARG PYTHON_VERSION=3.13

# ---- base: Python 3.13 + uv, on Debian "bookworm" (LiveKit needs glibc, so not Alpine) ----
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base
# Print logs right away (no buffering), so a crash never hides its last words.
ENV PYTHONUNBUFFERED=1
# Pre-compile Python files during the build -> the agent starts faster.
ENV UV_COMPILE_BYTECODE=1
# Copy files into the virtual environment instead of linking (works across build stages).
ENV UV_LINK_MODE=copy

# ---- build stage: install the packages ----
FROM base AS build

# Compilers, in case a package must be built from source. They are NOT in the final image.
RUN apt-get update && apt-get install -y gcc g++ python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# First copy ONLY the package lists, then install. Docker caches this step, so changing
# agent.py later does not re-download every package.
COPY pyproject.toml uv.lock ./
COPY agents/dental_receptionist/pyproject.toml agents/dental_receptionist/pyproject.toml
# --locked: use exactly the versions in uv.lock.  --no-dev: no test tools.
# --package: only what THIS agent needs.  --no-install-workspace: not our own code yet.
RUN uv sync --locked --no-dev --package dental-receptionist --no-install-workspace

# Now copy our own code and install it too. --no-editable = a real copy inside .venv,
# so the final image only needs the .venv folder.
COPY agents/dental_receptionist agents/dental_receptionist
RUN uv sync --locked --no-dev --package dental-receptionist --no-editable

# ---- final stage: small image, no compilers, not running as root ----
FROM base

# A normal user without special rights runs the agent (safer than root).
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/app" --shell "/sbin/nologin" \
    --uid "${UID}" appuser

WORKDIR /app
COPY --from=build --chown=appuser:appuser /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER appuser

# "start" = production mode: connect to LiveKit and wait for calls (jobs).
# LIVEKIT_URL / _API_KEY / _API_SECRET and the AI keys come from docker-compose.yml.
CMD ["python", "-m", "dental_receptionist.agent", "start"]
