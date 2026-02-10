import time
import uuid
import grpc

REQUEST_ID_HEADER = "x-request-id"

class RequestIdServerInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)
        if handler is None or handler.unary_unary is None:
            return handler

        def wrapped(request, context):
            rid = None
            for k, v in context.invocation_metadata():
                if k.lower() == REQUEST_ID_HEADER:
                    rid = v
                    break
            if rid is None:
                rid = str(uuid.uuid4())

            context.set_trailing_metadata(((REQUEST_ID_HEADER, rid),))
            start = time.time()
            try:
                return handler.unary_unary(request, context)
            finally:
                dur_ms = int((time.time() - start) * 1000)
                print(f"grpc rid={rid} method={handler_call_details.method} dur_ms={dur_ms} remaining={context.time_remaining():.3f}s")

        return grpc.unary_unary_rpc_method_handler(
            wrapped,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )

class RequestIdClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, request_id: str | None = None):
        self.request_id = request_id or str(uuid.uuid4())

    def intercept_unary_unary(self, continuation, client_call_details, request):
        md = []
        if client_call_details.metadata is not None:
            md.extend(list(client_call_details.metadata))
        md.append((REQUEST_ID_HEADER, self.request_id))
        client_call_details = client_call_details._replace(metadata=tuple(md))
        return continuation(client_call_details, request)
