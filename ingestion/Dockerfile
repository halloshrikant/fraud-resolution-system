# ingestion/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir --target=/install .

FROM python:3.12-slim AS runtime
RUN useradd --uid 1001 --create-home ingestuser
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.12/site-packages/
COPY pipeline/ ./pipeline/
USER 1001
CMD ["python", "-m", "ingestion.pipeline.main"]