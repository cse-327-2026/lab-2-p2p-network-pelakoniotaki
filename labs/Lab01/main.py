import argparse
import socket

from node_state import P2PNode
from node_runtime import NodeRuntime
import socket

def detect_container_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=False, help="node id (default: container hostname)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--seed-host", default="127.0.0.1")
    ap.add_argument("--seed-port", type=int, required=False)

    # new here in hot-fix-docker1
    ap.add_argument("--bind-host", required=True, help="(default 0.0.0.0 in docker, 127.0.0.1 locally)")
    ap.add_argument("--advertise-host", required=False, help="(optional override)")
    ap.add_argument("--advertise-port", type=int, required=False, help="(optional override)")
    
    ap.add_argument("--docker-auto-ip", action="store_true", help="flag → compute container IP automatically")
    ap.add_argument("--is-seed", action="store_true", help="flag → is this node a seed node?")
        
    args = ap.parse_args()


    bind_host = args.bind_host
    advertise_host = (
        args.advertise_host
        or (detect_container_ip() if args.docker_auto_ip else bind_host)
    )

    advertise_port = args.advertise_port or args.port

    print(f"Got my IP ===> {detect_container_ip()}")

    if args.seed_port is None:
        seed_host = None
        seed_port = None
    else:
        seed_host = args.seed_host
        seed_port = args.seed_port

    node = P2PNode(
        # node_id=args.id,
        node_id = args.id or socket.gethostname(),
        bind_host=args.bind_host,
        bind_port=args.port,
        seed_host=args.seed_host,
        seed_port=args.seed_port,
        max_incoming=12,
        target_outgoing=10,
        known_nodes_limit=50,
        advertise_host= advertise_host,
        advertise_port= advertise_port,
        is_seed = args.is_seed
    )
    
    rt = NodeRuntime(node)
    rt.run_forever()


if __name__ == "__main__":
    main()