from __future__ import annotations

import selectors
import socket
import random
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from node_state import P2PNode, NodeInfo
from logutil import setup_logger
import logging
import protocol


@dataclass
class ConnState:
    sock: socket.socket
    addr: tuple[str, int] | None    # for outgoing, may be None until connected
    direction: str                  # "in" or "out"
    inbuf: bytearray = field(default_factory=bytearray)
    hello_done: bool = False
    peer_info: Optional[NodeInfo] = None
    connecting: bool = False
    created_at: float = field(default_factory=lambda: time.time())

    def key(self) -> Optional[str]:
        return self.peer_info.key() if self.peer_info else None
    

class NodeRuntime:
    """
    Single-threaded event loop:
    - listen socker accepts connections
    - per-connection state buffered in memory
    - JSONL protocol parsing with newline framing

    Step 4 adds outgoing non-blocking connect and maintains target_outgoing peers.
    """

    def __init__(self, node: P2PNode):
        self.node = node
        self.sel = selectors.DefaultSelector()
        self.conns: Dict[socket.socket, ConnState] = {}

        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind((self.node.bind_host, self.node.bind_port))
        self.listen_sock.listen()
        self.listen_sock.setblocking(False)

        self.log = setup_logger(self.node.node_id, logging.INFO)

        self.sel.register(self.listen_sock, selectors.EVENT_READ, data={"kind": "listen"})

        # Maintenance pacing
        self._last_maint = 1.0
        self._maint_interval = 15.0  # seconds

        # Optional: basic connect timeout
        self._connect_timeout = 5.0

        # Heartbeat Ping/Pongs
        self._heartbeat_interval = 10.0
        self._last_heartbeat = 0.0

        # Random Failures
        self._failure_interval = 10.0
        self._last_failure = 0.0
        self._failure_prob = 0.15
    
    def run_forever(self) -> None:
        self.log.info(f"listening on {self.node.bind_host}:{self.node.bind_port}")

        startup_delay = random.uniform(0.5, 5.0)
        self.log.info(f"startup backoff {startup_delay:.2f}s")
        time.sleep(startup_delay)

        # Kick off initial outgoing attempts (seed is already in known_nodes)
        self._maintain_outgoing()

        try:
            while True:
                now = time.time()
                if now - self._last_maint >= self._maint_interval:
                    self._maintenance_tick(now)
                    self._last_maint = now

                events = self.sel.select(timeout=1.0)
                for key, mask in events:
                    data = key.data
                    if data and data.get("kind") == "listen":
                        self._accept_ready()
                    else:
                        sock = key.fileobj
                        if mask & selectors.EVENT_WRITE:
                            self._write_ready(sock)
                        if mask & selectors.EVENT_READ:
                            self._read_ready(sock)
        finally:
            self.close_all()
    

    def close_all(self) -> None:
        # unregister / close all sockets safely
        for sock in list(self.conns.keys()):
            self._close_conn(sock)
        try:
            self.sel.unregister(self.listen_sock)
        except Exception:
            pass
        
        try:
            self.listen_sock.close()
        except Exception:
            pass
        

    def _maintenance_tick(self, now: float) -> None:
        # Finish pending outgoing connects that timed out
        for sock, st in list(self.conns.items()):
            if st.connecting and now - st.created_at > self._connect_timeout:
                self.log.warning("connect timeout")
                self._close_conn(sock)
        

        # heartbeats:
        if now - self._last_heartbeat > self._heartbeat_interval:
            self._send_heartbeat()
            self._last_heartbeat = now

        # random failures
        if now - self._last_failure > self._failure_interval:
            self._inject_random_failure()
            self._last_failure = now
        
        # maintain target outgoing connections
        self._maintain_outgoing()


    def _inject_random_failure(self):
        peers = [
            (sock, st)
            for sock, st in self.conns.items()
            if st.hello_done and not st.connecting
        ]

        if not peers:
            return

        if random.random() < self._failure_prob:
            sock, st = random.choice(peers)
            self.log.info(f"Simulating failure -> closing {st.peer_info.key()}")
            self._close_conn(sock)


    def _maintain_outgoing(self) -> None:
        if self.node.is_seed:
            return
        
        # -------------------------------------------------
        # 1. Trim excess outgoing connections FIRST
        # -------------------------------------------------
        excess = len(self.node.outgoing_peers) - self.node.target_outgoing
        if excess > 0:
            self.log.info(f"should be Trimming  -- {excess}")
            # sort peers by oldest last_seen first
            peers = sorted(
                self.node.outgoing_peers.values(),
                key=lambda pc: pc.info.last_seen
            )

            for pc in peers[:excess]:
                key = pc.info.key()
                self.log.info(f"Trimming outgoing peer {key}")

                # find matching socket
                for sock, st in list(self.conns.items()):
                    if st.peer_info and st.peer_info.key() == key:
                        st.peer_info.retry_after = time.time() + 30
                        self._close_conn(sock)
                        break

        # -------------------------------------------------
        # 2. Maintain minimum outgoing connections
        # -------------------------------------------------
        
        needed = self.node.target_outgoing - len(self.node.outgoing_peers)
        if needed <= 0:
            return

        candidates = self.node.pick_connect_candidates(needed)

        for info in candidates:
            if time.time() > info.retry_after:
                self._start_outgoing_connect(info)
    
    def _start_outgoing_connect(self, info: NodeInfo) -> None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)

            err = sock.connect_ex((info.host, info.port))

            st = ConnState(
                sock=sock,
                addr=(info.host, info.port),
                direction="out",
                connecting=True,
                peer_info=info,
            )

            self.conns[sock] = st

            # Wait for socket writable -> connect completion
            self.sel.register(sock, selectors.EVENT_WRITE | selectors.EVENT_READ,
                              data={"kind": "conn"})
            
            self.log.info(f"connecting to {info.key()}")
        
        except Exception as e:
            self.log.error(f"connect failed immediately: {e}")
            self.log.error(f" Can't reach node {info}")
    
    # -----------------------------
    # Accept / Close
    # -----------------------------

    def _accept_ready(self) -> None:
        while True:
            try:
                conn, addr = self.listen_sock.accept()
            except BlockingIOError:
                return
            
            conn.setblocking(False)

            if not self.node.can_accept_incoming():
                # Politely reject then close:
                try:
                    conn.sendall(protocol.encode_msg(protocol.reject("max_incoming")))
                except Exception:
                    pass
                conn.close()
                continue
                
            st = ConnState(sock=conn, addr=addr, direction="in")
            self.conns[conn] = st
            self.sel.register(conn, selectors.EVENT_READ, data={"kind": "conn"})

            # Symmetric handshake: send HELLO immediately
            self._send_hello(conn)

            self.log.info("ACCEPT incoming %s:%s", addr[0], addr[1])
    
    
    def _close_conn(self, sock: socket.socket) -> None:
        st = self.conns.pop(sock, None)
        # st.peer_info.retry_after = time.time() + random.uniform(3, 8)
        if st.peer_info:
            st.peer_info.retry_after = time.time() + random.uniform(3, 8)
        try:
            self.sel.unregister(sock)
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass
            
        # Remove from node peer map if we already know who it was
        if st and st.peer_info:
            self.node.remove_peer(st.peer_info.key())
            self.log.warning(f"Closed {st.peer_info.key()}")
        elif st:
            self.log.warning(f"Closed unknown peer {st.addr}")

        # Trigger maintenance quickly after disconnect
        self._last_maint = 0
        
    
    # --------------------------
    # IO + Parsing
    # --------------------------

    def _read_ready(self, sock: socket.socket) -> None:
        st = self.conns.get(sock)
        if st is None:
            return

        try:
            chunk = sock.recv(4096)
        except (ConnectionResetError,
                ConnectionAbortedError,
                OSError):
            self._close_conn(sock)
            return
        except BlockingIOError:
            return
        
        
        if not chunk:
            self._close_conn(sock)
            return

        st.inbuf.extend(chunk)

        # Process complete JSON lines
        while True:
            nl = st.inbuf.find(b"\n")
            if nl == -1:
                break
            line = bytes(st.inbuf[:nl])
            del st.inbuf[: nl + 1]

            if not line.strip():
                continue
                
            try:
                msg = protocol.decode_msg(line)
            except Exception as e:
                # Malformed message -> close
                self.log.warning(f"Bad message from {st.addr}: {e}")
                self._close_conn(sock)
                return
            
            self._handle_msg(sock, msg)

    def _write_ready(self, sock: socket.socket) -> None:
        st = self.conns.get(sock)
        if not st or not st.connecting:
            return
        
        # Check connection result
        err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            self.log.error(f"connect error {err}")
            self._close_conn(sock)
            return
        
        # Connected Successfully
        st.connecting = False

        # Switch to read-only monitoring
        try:
            self.sel.modify(sock, selectors.EVENT_READ, data={"kind": "conn"})
        except Exception:
            self._close_conn(sock)
            return
        
        # Register as outgoing peer
        if st.peer_info:
            self.node.add_peer(st.peer_info, direction="out")
        
        self.log.info(f"connected to {st.peer_info.key()}")

        # Symmetric handshake
        self._send_hello(sock)
        
        
    def _send(self, sock: socket.socket, obj: Dict[str, Any]) -> None:
        # For Step 3 we keep writes small and use sendall
        # In a real system you'd buffer + register EVENT_WRITE
        try:
            sock.sendall(protocol.encode_msg(obj))
            self.log.debug(f"<<< Tx {obj.get('type')}")
        except (ConnectionResetError,
                ConnectionAbortedError,
                BrokenPipeError, 
                OSError) as e:
            self.log.error(f"send failed: {e}")
            self._close_conn(sock)
        except Exception:
            self._close_conn(sock)

    
    
    def _send_hello(self, sock: socket.socket) -> None:
        self._send(sock, protocol.hello(
            self.node.node_id, self.node.advertise_host, self.node.advertise_port
        ))

    def _send_heartbeat(self):
        for sock, st in self.conns.items():
            if st.hello_done and not st.connecting:
                self._send(sock, protocol.ping())
                if random.uniform(0,1) > 0.5:
                    self._send(sock, protocol.get_peers())
    
    # --------------------------
    # Message Handling
    # --------------------------

    def _handle_msg(self, sock: socket.socket, msg: Dict[str, Any]) -> None:
        st = self.conns.get(sock)
        if st is None:
            return

        mtype = msg.get("type")
        self.log.debug(f'>>> Rx {mtype}')
        self.log.debug(self.node.debug_state())


        if mtype == "HELLO":    
            node_id = msg.get("node_id")
            host = msg.get("host")
            port = msg.get("port")

            if not isinstance(node_id, str) or not isinstance(host, str) or not isinstance(port, int):
                self._close_conn(sock)
                return

            # Prevent self-connection
            if node_id == self.node.node_id and host == self.node.advertise_host and port == self.node.advertise_port:
                self._close_conn(sock)
                return

            peer_info = NodeInfo(node_id=node_id, host=host, port=port)
            st.peer_info = peer_info
            st.hello_done = True

            # Register as peer
            self.node.add_peer(peer_info, direction=st.direction)

            # After HELLO, immediately ask for peers
            self._send(sock, protocol.get_peers())
            return
        
        if mtype == "GET_PEERS":
            # Send a subset of known odes excluding the requester (and self)
            exclude = set()
            if st.peer_info:
                exclude.add(st.peer_info.key())

            subset = self.node.get_known_subset(k=50, exclude=exclude)
            self._send(sock, protocol.peers(subset))

            # Seed acts only as introducer
            if self.node.is_seed:
                if st.peer_info:
                    st.peer_info.retry_after = time.time() + 3600  # prevent reconnect
                self.log.info("Seed introducer closing connection")
                self._close_conn(sock)

            return
        
        if mtype == "PEERS":
            peers = msg.get("peers")
            if not isinstance(peers, list):
                return
            
            added = 0
            for p in peers:
                if not isinstance(p, dict):
                    continue
                node_id = p.get("node_id")
                host = p.get("host")
                port = p.get("port")
                if isinstance(node_id, str) and isinstance(host, str) and isinstance(port, int):
                    self.node.remember_node(NodeInfo(node_id=node_id, host=host, port=port))
                    added += 1

            self.log.info("learned %d peers (known=%d)", added, len(self.node.known_nodes))
            return

        if mtype == "REJECT":
            reason = msg.get("reason")
            self.log.warning(f"Rejected by peer: {reason}")
            self._close_conn(sock)
            return


        if mtype == "PING":
            self._send(sock, protocol.pong())
            return 

        if mtype == "PONG":
            # update last seen timestamp
            if st.peer_info:
                st.peer_info.last_seen = time.time()
                self.log.debug(f"Updating node {st.peer_info.key()}")
            return
        
        if mtype == "GET_CONNECTIONS":
            peers = [
                pc.info
                for pc in list(self.node.incoming_peers.values())
                + list(self.node.outgoing_peers.values())
            ]
            self._send(sock, protocol.connections(peers))
            return
        
        # unknown message types ignored
        self.log.error(f"Unknown msg type: {mtype}")