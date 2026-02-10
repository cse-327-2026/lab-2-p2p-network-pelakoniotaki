FROM python:3.11-slim
WORKDIR /tests
COPY requirements.txt /tests/requirements.txt
RUN pip install --no-cache-dir -r /tests/requirements.txt
COPY ../../shared/proto/kv.proto /tests/kv.proto
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. kv.proto
COPY test_kv_blackbox.py /tests/test_kv_blackbox.py
COPY ../../shared/scripts/wait_for_port.py /tests/wait_for_port.py
CMD ["pytest", "-q"]
