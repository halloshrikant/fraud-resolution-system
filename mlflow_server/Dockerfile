# mlflow_server/Dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir "mlflow>=2.17" "boto3>=1.35"
RUN useradd --uid 1001 --create-home mlflowuser
USER 1001
EXPOSE 5000
ENTRYPOINT ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]