# syntax=docker/dockerfile:1

############################  BUILD  ############################
FROM python:3.11-slim AS builder
WORKDIR /src

# Pull in YOUR fork as the build context (so no external clone)
COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir . -w /wheels && \
    rm -rf /var/lib/apt/lists/*

##########################  RUNTIME  ###########################
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    SERVER_TRANSPORT=http \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8150

# non-root user so that mounted volumes (token cache) stay writable
RUN adduser --disabled-password --gecos "" mcp

USER mcp
WORKDIR /app

# install only the wheels we built
COPY --from=builder /wheels /tmp/wheels
RUN pip install --no-cache-dir --no-deps /tmp/wheels/*.whl \
 && rm -rf /tmp/wheels

# copy your HTTP‑wrapper script
COPY --chown=mcp:mcp src/main_http.py /app/main_http.py
RUN chmod +x /app/main_http.py

EXPOSE 8150
HEALTHCHECK CMD curl -fs "http://localhost:${SERVER_PORT}/health" || exit 1

# directly launch the HTTP server; all creds & ports from env vars
CMD ["python", "/app/main_http.py"]
