import json

def encode_msg(obj: dict) -> bytes:
    return (json.dumps(obj) + "\n").encode("utf-8")

def decode_msg(line: bytes) -> dict:
    return json.loads(line.decode("utf-8"))

def hello(node_id, host, port):
    return {
        "type": "HELLO",
        "node_id": node_id,
        "host": host,
        "port": port
    }

def get_peers():
    return {"type":"GET_PEERS"}


def peers(peer_list):
    return {
        "type": "PEERS",
        "peers": [
            {
                "node_id": p.node_id,
                "host": p.host,
                "port": p.port,
            }
            for p in peer_list
        ],
    }

def reject(reason):
    return {
        "type": "REJECT",
        "reason": reason
    }

def ping():
    return {"type": "PING"}

def pong():
    return {"type": "PONG"}


def get_connections():
    return {"type": "GET_CONNECTIONS"}


def connections(peer_list):
    return {
        "type": "CONNECTIONS",
        "peers": [
            {
                "node_id": p.node_id,
                "host": p.host,
                "port": p.port,
            }
            for p in peer_list
        ],
    }