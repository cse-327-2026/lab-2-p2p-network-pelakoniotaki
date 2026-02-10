import asyncio
import json
import os
import socket
import time
from typing import Dict, Set, Tuple

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

PORT = int(os.environ.get("PEER_PORT", "9000"))
TIMEOUT = float(os.environ.get("TIMEOUT", "1.0"))
REFRESH_SECONDS = float(os.environ.get("REFRESH_SECONDS", "2.0"))
MAX_NODES = int(os.environ.get("MAX_NODES", "100"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="viz/static"), name="static")

TOPOLOGY = {
    "nodes": [],
    "edges": [],
    "updated_at": 0.0,
}


def discover_peers():
    try:
        infos = socket.getaddrinfo("peer", PORT, type=socket.SOCK_STREAM)
        ips = {info[4][0] for info in infos}

        my_ip = socket.gethostbyname(socket.gethostname())
        ips.discard(my_ip)

        return ips
    except Exception:
        return set()


def enc(obj: dict) -> bytes:
    return (json.dumps(obj) + "\n").encode("utf-8")


async def query_node(host: str, port: int):
    peers = []
    active_edges = []
    known_edges = []

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=TIMEOUT
        )

        writer.write(
            enc(
                {
                    "type": "HELLO",
                    "node_id": "viz",
                    "host": "viz",
                    "port": 0,
                }
            )
        )

        writer.write(enc({"type": "GET_PEERS"}))
        writer.write(enc({"type": "GET_CONNECTIONS"}))
        await writer.drain()

        start = time.time()

        while time.time() - start < TIMEOUT:
            line = await asyncio.wait_for(reader.readline(), timeout=TIMEOUT)
            if not line:
                break

            msg = json.loads(line.decode())
            t = msg.get("type")

            if t == "PEERS":
                peers = msg.get("peers") or []
                for p in peers:
                    h = p.get("host")
                    pt = p.get("port")
                    if isinstance(h, str) and isinstance(pt, int):
                        known_edges.append((f"{host}:{port}", f"{h}:{pt}"))

            if t == "CONNECTIONS":
                for p in msg.get("peers", []):
                    h = p.get("host")
                    pt = p.get("port")
                    if isinstance(h, str) and isinstance(pt, int):
                        active_edges.append((f"{host}:{port}", f"{h}:{pt}"))


        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

    except Exception:
        pass

    return peers, active_edges, known_edges


async def refresh_topology():
    nodes: Dict[str, dict] = {}
    active_edges: Set[Tuple[str, str]] = set()
    known_edges: Set[Tuple[str, str]] = set()

    ips = discover_peers()
    tasks = [query_node(ip, PORT) for ip in ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for ip, result in zip(ips, results):
        if isinstance(result, Exception):
            continue

        peers, a_edges, k_edges = result

        node_key = f"{ip}:{PORT}"
        nodes[node_key] = {"id": node_key, "label": node_key}

        active_edges.update(a_edges)
        known_edges.update(k_edges)

    TOPOLOGY["nodes"] = list(nodes.values())
    TOPOLOGY["edges"] = [
        {"from": a, "to": b, "type": "active"}
        for a, b in active_edges
    ] + [
        {"from": a, "to": b, "type": "known"}
        for a, b in known_edges
    ]

    TOPOLOGY["updated_at"] = time.time()



@app.on_event("startup")
async def startup():
    asyncio.create_task(refresh_loop())


async def refresh_loop():
    while True:
        await refresh_topology()
        await asyncio.sleep(REFRESH_SECONDS)


@app.get("/", response_class=HTMLResponse)
def index():
    with open("viz/static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/topology")
def api_topology():
    return TOPOLOGY
