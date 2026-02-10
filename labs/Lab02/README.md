# Lab 02 — RPC fundamentals with gRPC (Python + Go)

## Learning goals
- Define service contracts with Protocol Buffers (IDL).
- Generate stubs and use unary vs streaming RPCs.
- Apply deadlines/timeouts and basic retry behavior.
- Practice backward-compatible API evolution.

## In-class walkthrough
1. **Define the API**
   - Create `kv.proto` with `Ping`, `Get`, `Put`, and `ListKeys`.
   - Add comments to fields and services.
2. **Generate code**
   - Python: `python -m grpc_tools.protoc`.
   - Go: `protoc --go_out` and `--go-grpc_out`.
3. **Implement server + client**
   - Python server handles KV map and logs requests.
   - Go client performs calls with deadlines.
4. **Show streaming**
   - Implement `ListKeys` as server-streaming.
5. **Schema evolution demo**
   - Add a new optional field and show older clients still work.

## Student deliverable
- `kv.proto` plus a working server (Python) and client (Go or Python).
- A load-test script that sends N concurrent puts/gets and reports latency.

## Instructor notes
- Teach the difference between API compatibility and implementation compatibility.
- Highlight gRPC status codes and how to map errors.
- Emphasize deadlines over client-side timeouts alone.

## Tools (free + open source)
- Protocol Buffers compiler (`protoc`).
- gRPC Python (`grpcio`, `grpcio-tools`).
- gRPC Go (`google.golang.org/grpc`).
- hey or vegeta for simple load testing (optional).

## Suggested reading & sources
- gRPC overview: https://grpc.io/docs/what-is-grpc/
- gRPC Python quickstart: https://grpc.io/docs/languages/python/quickstart/
- gRPC Go quickstart: https://grpc.io/docs/languages/go/quickstart/
- Protocol Buffers style guide: https://protobuf.dev/programming-guides/style/

### Pattern spotlight materials
- `patterns/grpc_interceptors/`
- `patterns/sidecar_log_shipper/`
