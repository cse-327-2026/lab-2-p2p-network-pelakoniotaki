FROM python:3.11-slim
WORKDIR /app
COPY ../../shared/proto/kv.proto /app/kv.proto
RUN pip install --no-cache-dir grpcio grpcio-tools protobuf \
 && python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. kv.proto
COPY submission/server.py /app/server.py
EXPOSE 50051
CMD ["python", "server.py"]
