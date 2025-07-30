# syntax=docker/dockerfile:1

############################  BUILD  ############################
FROM python:3.12-slim AS builder
WORKDIR /src

# Pull in YOUR fork as the build context (so no external clone)
COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir . -w /wheels && \
    rm -rf /var/lib/apt/lists/*

##########################  RUNTIME  ###########################
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

# non-root user so that mounted volumes (token cache) stay writable
RUN adduser --disabled-password --gecos "" mcp

USER mcp
WORKDIR /app

# install only the wheels we built
COPY --from=builder --chown=mcp:mcp /wheels /tmp/wheels
RUN pip install --no-cache-dir --no-deps /tmp/wheels/*.whl \
    && rm -rf /tmp/wheels

COPY --chown=mcp:mcp src/main.py /app/main.py
RUN chmod +x /app/main.py

EXPOSE 8150
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${SERVER_PORT}/health')" || exit 1

# directly launch the main server; all creds & ports from env vars
CMD ["python", "/app/main.py"]
