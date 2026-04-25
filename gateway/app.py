"""
HTTP Gateway.

Responsibilities:
- Expose the public API (/health, /jobs, /jobs/<id>, /cluster, /admin/reset).
- Fail over across all queue nodes listed in QUEUE_NAMES so the system keeps
  working when the leader queue is down.
"""

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

QUEUE_NAMES = [q.strip() for q in os.getenv("QUEUE_NAMES", "queue1,queue2").split(",") if q.strip()]
QUEUE_PORT = os.getenv("QUEUE_PORT", "5000")
WORKER_NODES = [w.strip() for w in os.getenv("WORKER_NODES", "worker1").split(",") if w.strip()]


def _queue_urls():
    return [f"http://{q}:{QUEUE_PORT}" for q in QUEUE_NAMES]


def _forward(method, path, **kwargs):
    """Try each queue in order until one answers successfully."""
    last_err = None
    for url in _queue_urls():
        try:
            r = requests.request(method, f"{url}{path}", timeout=5, **kwargs)
            if r.ok:
                try:
                    return r.json(), 200
                except ValueError:
                    return {"raw": r.text}, 200
            last_err = r.text
        except Exception as e:
            last_err = str(e)
            continue
    return {"error": "all queues unavailable", "detail": last_err}, 503


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/jobs", methods=["POST"])
def submit_job():
    data, status = _forward("POST", "/internal/jobs", json=request.json)
    return jsonify(data), status


@app.route("/jobs/<job_id>")
def get_job(job_id):
    data, status = _forward("GET", f"/internal/jobs/{job_id}")
    return jsonify(data), status


@app.route("/admin/reset", methods=["POST"])
def reset():
    # Try to reset every queue so state on both leader and follower is cleared.
    for url in _queue_urls():
        try:
            requests.post(f"{url}/internal/reset", timeout=3)
        except Exception:
            pass
    return {"status": "reset"}


@app.route("/cluster")
def cluster():
    leader = None
    for q in QUEUE_NAMES:
        try:
            r = requests.get(f"http://{q}:{QUEUE_PORT}/internal/cluster", timeout=2)
            if r.ok:
                leader = r.json().get("leader", q)
                break
        except Exception:
            continue
    if leader is None:
        leader = QUEUE_NAMES[0] if QUEUE_NAMES else "queue1"
    return {
        "leader": leader,
        "nodes": QUEUE_NAMES,
        "workers": WORKER_NODES,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
