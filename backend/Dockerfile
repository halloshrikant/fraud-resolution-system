FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir --target=/install .

FROM python:3.12-slim AS runtime
# Non-root user — OWASP security hardening
RUN useradd --uid 1001 --create-home appuser
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.12/site-packages/
COPY app/ ./app/
USER 1001
EXPOSE 8000
# Gunicorn + Uvicorn workers for production concurrency
CMD ["gunicorn", "app.main:app",
     "-k", "uvicorn.workers.UvicornWorker",
     "--workers", "4",
     "--bind", "0.0.0.0:8000",
     "--timeout", "120",
     "--access-logfile", "-",
     "--error-logfile", "-",
     "--log-level", "warning"]