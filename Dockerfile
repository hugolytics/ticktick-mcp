# syntax=docker/dockerfile:1

################## build stage ##################
FROM python:3.11-slim AS builder
WORKDIR /wheels
ARG MCP_REF=main
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
 && pip install --upgrade pip wheel \
 && pip wheel --no-cache-dir \
        git+https://github.com/your‑org/ticktick-mcp.git@${MCP_REF}

################ runtime stage ################
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    SERVER_TRANSPORT=http \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8150

# create non‑root user for token persistence
RUN adduser --disabled-password --gecos "" mcp
USER mcp
WORKDIR /app

# install the wheels only
COPY --from=builder /wheels /tmp/wheels
RUN pip install --no-cache-dir --no-deps /tmp/wheels/*.whl \
 && rm -rf /tmp/wheels

# copy the HTTP wrapper
COPY --chown=mcp:mcp main_http.py /app/main_http.py
RUN chmod +x /app/main_http.py

EXPOSE ${SERVER_PORT}
HEALTHCHECK CMD curl -fs http://localhost:${SERVER_PORT}/health || exit 1

ENTRYPOINT ["/app/main_http.py"]
