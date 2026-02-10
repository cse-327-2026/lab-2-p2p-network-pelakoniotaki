import os
import grpc
import pytest
import kv_pb2
import kv_pb2_grpc

HOST = os.getenv("KV_HOST", "kv")
PORT = int(os.getenv("KV_PORT", "50051"))

@pytest.fixture(scope="session", autouse=True)
def wait_ready():
    import subprocess, sys
    subprocess.check_call([sys.executable, "wait_for_port.py", HOST, str(PORT), "20"])

def channel():
    return grpc.insecure_channel(f"{HOST}:{PORT}")

def test_put_get_roundtrip():
    with channel() as ch:
        stub = kv_pb2_grpc.KVStub(ch)
        r = stub.Put(kv_pb2.PutRequest(key="a", value=b"1"))
        assert r.ok is True
        g = stub.Get(kv_pb2.GetRequest(key="a"))
        assert g.found is True
        assert g.value == b"1"

def test_get_missing_is_not_found():
    with channel() as ch:
        stub = kv_pb2_grpc.KVStub(ch)
        g = stub.Get(kv_pb2.GetRequest(key="missing"))
        assert g.found is False

def test_list_keys_sorted():
    with channel() as ch:
        stub = kv_pb2_grpc.KVStub(ch)
        stub.Put(kv_pb2.PutRequest(key="b", value=b"2"))
        stub.Put(kv_pb2.PutRequest(key="a", value=b"1"))
        keys = stub.ListKeys(kv_pb2.ListKeysRequest()).keys
        assert list(keys) == sorted(keys)
        assert "a" in keys and "b" in keys
