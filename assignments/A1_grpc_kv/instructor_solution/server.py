from concurrent import futures
import grpc
import kv_pb2
import kv_pb2_grpc

class KVServicer(kv_pb2_grpc.KVServicer):
    def __init__(self):
        self.store: dict[str, bytes] = {}

    def Put(self, request, context):
        if not request.key:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "key is required")
        self.store[request.key] = bytes(request.value)
        return kv_pb2.PutResponse(ok=True)

    def Get(self, request, context):
        if not request.key:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "key is required")
        if request.key not in self.store:
            return kv_pb2.GetResponse(found=False, value=b"")
        return kv_pb2.GetResponse(found=True, value=self.store[request.key])

    def ListKeys(self, request, context):
        return kv_pb2.ListKeysResponse(keys=sorted(self.store.keys()))

def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    kv_pb2_grpc.add_KVServicer_to_server(KVServicer(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
