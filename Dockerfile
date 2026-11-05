# syntax=docker/dockerfile:1.7
# One image, four entry points: cellpulse-agent | -collector | -detector | -cli

FROM python:3.12-slim AS build
WORKDIR /src
RUN pip install --no-cache-dir "grpcio-tools>=1.66" build
COPY pyproject.toml README.md LICENSE ./
COPY proto ./proto
COPY src ./src
RUN python -m grpc_tools.protoc -I proto \
      --python_out=src --pyi_out=src --grpc_python_out=src \
      proto/cellpulse/v1/telemetry.proto \
 && python -m build --wheel --outdir /wheels

FROM python:3.12-slim AS runtime
LABEL org.opencontainers.image.source="https://github.com/not-clover/distributed-telemetry" \
      org.opencontainers.image.description="CellPulse: distributed 5G cell telemetry" \
      org.opencontainers.image.licenses="MIT"
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels \
 && useradd --create-home --uid 10001 cellpulse
USER cellpulse
EXPOSE 50051 9100
CMD ["cellpulse-collector"]
