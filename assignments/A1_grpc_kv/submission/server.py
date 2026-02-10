"""Student submission entrypoint (A1).

Contract:
- Listen on 0.0.0.0:50051
- Implement Put/Get/ListKeys
- In-memory store is enough
"""

from concurrent import futures
import grpc
import kv_pb2
import kv_pb2_grpc

class KVServicer(kv_pb2_grpc.KVServicer):
    def __init__(self):
        self.store: dict[str, bytes] = {}

    def Put(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Put not implemented")
        return kv_pb2.PutResponse(ok=False)

    def Get(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Get not implemented")
        return kv_pb2.GetResponse(found=False, value=b"")

    def ListKeys(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListKeys not implemented")
        return kv_pb2.ListKeysResponse(keys=[])

def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    kv_pb2_grpc.add_KVServicer_to_server(KVServicer(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
