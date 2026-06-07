# agents/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir --target=/install .

FROM python:3.12-slim AS runtime
RUN useradd --uid 1001 --create-home agentuser
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.12/site-packages/
COPY orchestrator/       ./orchestrator/
COPY rag_agent/          ./rag_agent/
COPY transaction_analyst/ ./transaction_analyst/
COPY fraud_investigator/  ./fraud_investigator/
COPY shared/             ./shared/
USER 1001
EXPOSE 8001
CMD ["uvicorn", "shared.server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]