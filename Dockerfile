FROM python:3.11-slim AS base

RUN export DEBIAN_FRONTEND=noninteractive
# CẬP NHẬT DÒNG NÀY: Thêm ffmpeg và nodejs vào danh sách cài đặt
RUN --mount=type=cache,id=api-dev-base-install,target=/var/cache/apt apt-get update -yq && \
    apt-get install -yq --no-install-recommends curl \
    ca-certificates libcurl4-openssl-dev libssl-dev \
    iputils-ping netcat-traditional \
    ffmpeg nodejs && \ 
    rm -rf /var/lib/apt/lists/*

# Allow legacy SSL renegotiation
RUN mkdir -p /etc/ssl && \
    echo 'openssl_conf = openssl_init\n\
    \n\
    [openssl_init]\n\
    ssl_conf = ssl_sect\n\
    \n\
    [ssl_sect]\n\
    system_default = system_default_sect\n\
    \n\
    [system_default_sect]\n\
    Options = UnsafeLegacyRenegotiation\n\
    CipherString = DEFAULT:@SECLEVEL=0\n' \
    > /etc/ssl/openssl.cnf

ENV OPENSSL_CONF=/etc/ssl/openssl.cnf

# https://github.com/orgs/python-poetry/discussions/1879#discussioncomment-216865
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # uv
    # Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
    UV_COMPILE_BYTECODE=1 \
    # Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
    UV_LINK_MODE=copy \
    UV_PYTHON=3.11 \
    # UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Place executables in the environment at the front of the path
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

FROM base AS builder

RUN export DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,id=api-dev-build-install,target=/var/cache/apt apt-get update -yq && \
    apt-get install -yq --no-install-recommends build-essential clang && \
    rm -rf /var/lib/apt/lists/*

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /uvx /bin/

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,id=api-dev-uv-install,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

COPY ./main.py /app

FROM base AS runtime

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/ /app/
