FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir build && \
    python -m build --wheel

FROM python:3.11-slim

RUN groupadd -r flywire && useradd -r -g flywire -d /app -s /sbin/nologin flywire

WORKDIR /app

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

COPY frontend/ frontend/
COPY data/ data/

RUN mkdir -p data && chown -R flywire:flywire /app

USER flywire

EXPOSE 8000

VOLUME ["/app/data"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/topology')" || exit 1

ENTRYPOINT ["python", "-m", "flywire_lsm.server"]
