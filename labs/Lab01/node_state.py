import time
import random
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set

def now_ts() -> float:
    return time.time()


@dataclass
class NodeInfo:
    node_id: str
    host: str
    port: int
    last_seen: float = field(default_factory=now_ts)
    last_attempt: Optional[float] = None
    retry_after: float = 0.0

    @property
    def addr(self) -> str:
        return f"{self.host}:{self.port}"
    
    def key(self) -> str:
        return f"{self.node_id}@{self.addr}"
    

@dataclass
class PeerConn:
    info: NodeInfo
    direction: str  # "in" or "out"
    connected_at: float = field(default_factory=now_ts)


class P2PNode:
    def __init__(
            self, 
            node_id:str,
            bind_host: str, 
            bind_port: int, 
            seed_host: str,
            seed_port: int,
            max_incoming: int = 10, 
            target_outgoing: int = 5,
            known_nodes_limit: int = 50,
            advertise_host: str = None,
            advertise_port: str = None,
            is_seed: bool = False
    ):
        
        self.node_id = node_id
        self.bind_host = bind_host
        self.bind_port = bind_port

        self.max_incoming = max_incoming
        self.target_outgoing = target_outgoing
        self.known_nodes_limit = known_nodes_limit

        self.known_nodes: Dict[str, NodeInfo] = {}
        self.incoming_peers: Dict[str, PeerConn] = {}
        self.outgoing_peers: Dict[str, PeerConn] = {}

        self.advertise_host = advertise_host if advertise_host is not None else bind_host
        self.advertise_port = advertise_port if advertise_port is not None else bind_port

        self.is_seed = is_seed

        # Add self to known nodes
        # self.remember_node(NodeInfo(node_id, bind_host, bind_port))

        # Remember seed
        if not (seed_host == bind_host and seed_port == bind_port):
            self.seed = NodeInfo("seed", seed_host, seed_port)
            self.remember_node(self.seed)
        else:
            self.seed = None
        



    # -------------------------
    # Known Nodes Management
    # ------------------------- 

    def remember_node(self, info: NodeInfo) -> None:
        key = info.key()

        if key in self.known_nodes:
            self.known_nodes[key].last_seen = now_ts()

        # Enforce size limit (LRU eviction)
        if len(self.known_nodes) >= self.known_nodes_limit:
            oldest_key = min(
                self.known_nodes.items(),
                key=lambda kv: kv[1].last_seen
            )[0]
            self.known_nodes.pop(oldest_key, None)
        
        self.known_nodes[key] = info

        
    def forget_node(self, key: str) -> None:
        self.known_nodes.pop(key, None)

    # -------------------------
    # Peer Management
    # -------------------------
    
    def is_connected_to(self, key: str) -> bool:
        return key in self.incoming_peers or key in self.outgoing_peers
    
    def pick_connect_candidates(self, n: int) -> List[NodeInfo]:
        """
        Return up to n NodeInfo entries to connect to, preferring most recently seen.
        Excdludes self and already-connected peers
        """
        items = list(self.known_nodes.values())

        # sort by last_seen descending
        items.sort(key= lambda x: x.last_seen, reverse=True)
        out: List[NodeInfo] = []
        for info in items:
            if info.node_id == self.node_id and info.host == self.bind_host and info.port == self.bind_port:
                continue
            if info.host == self.bind_host and info.port == self.bind_port:
                continue
            if self.is_connected_to(info.key()):
                continue
            out.append(info)
            if len(out) >= n:
                break
        return out


    def can_accept_incoming(self) -> bool:
        return len(self.incoming_peers) < self.max_incoming

    def needs_more_outgoing(self) -> bool:
        return len(self.outgoing_peers) < self.target_outgoing

    def add_peer(self, info: NodeInfo, direction: str) -> None:
        peer = PeerConn(info=info, direction=direction)
        key = info.key()

        if direction == "in":
            self.incoming_peers[key] = peer
        else:
            self.outgoing_peers[key] = peer
        
        self.remember_node(info)
    
    def remove_peer(self, key: str) -> None:
        self.incoming_peers.pop(key, None)
        self.outgoing_peers.pop(key, None)
    

    # -------------------------
    # Discovery Helpers
    # -------------------------

    
    def get_known_subset(self, k: int, exclude: Set[str] | None = None) -> List[NodeInfo]:
        exclude = exclude or set()
        candidates = [
            n for k, n in self.known_nodes.items()
            if k not in exclude
            and n.port != self.bind_port
        ]

        if not candidates:
            return []
        
        if len(candidates) <= k:
            random.shuffle(candidates)
            return candidates
        
        return random.sample(candidates, k)
    
    def debug_state(self) -> None:
        print("=== NODE STATE ===")
        print(f"ID: {self.node_id}")
        print(f"Listening: {self.bind_host}:{self.bind_port}")
        print(f"Known nodes: {len(self.known_nodes)}")
        for node in self.known_nodes: 
            if node in self.incoming_peers:
                print(f"\t\t\t > {node}")
            elif node in self.outgoing_peers:
                print(f"\t\t\t < {node}")
            else:
                print(f"\t\t\t - {node}")
        print(f"Incoming peers: {len(self.incoming_peers)}")
        print(f"Outgoing peers: {len(self.outgoing_peers)}")
        print("==================")

    