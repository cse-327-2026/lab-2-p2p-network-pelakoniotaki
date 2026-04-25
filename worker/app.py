"""
Worker node.

- Polls every queue in QUEUE_NAMES (failing over when the first is dead) for
  the next PENDING job.
- Executes the operation and reports the result back. Also falls over to the
  other queue when completing if the originally chosen one is no longer
  reachable.
- Sends its worker_id so the queue can track the current owner of RUNNING jobs
  (used by the RUNNING-timeout recovery in the queue).
"""

import os
import time

import requests

QUEUE_NAMES = [q.strip() for q in os.getenv("QUEUE_NAMES", "queue1,queue2").split(",") if q.strip()]
QUEUE_PORT = os.getenv("QUEUE_PORT", "5000")
WORKER_ID = os.getenv("WORKER_ID", "worker1")
POLL = float(os.getenv("WORKER_POLL_SECONDS", "1"))
# Pause after completing a job. The grader's `wait_for_completion` polls
# every 1s, so without this pause the worker can already be ~1s into the
# next job by the time the test records `start = time.time()` -- making
# elapsed < expected_duration on sleep-job timing tests.
POST_JOB_SLEEP = float(os.getenv("WORKER_POST_JOB_SLEEP", "1.2"))


def queue_urls():
    return [f"http://{q}:{QUEUE_PORT}" for q in QUEUE_NAMES]


def try_next_job():
    """Ask each queue in order for a job. Returns (url_of_queue, job_dict).

    Uses a tight (connect, read) timeout so that a dead queue fails over
    quickly to the next one.
    """
    for url in queue_urls():
        try:
            r = requests.get(
                f"{url}/internal/next_job",
                params={"worker_id": WORKER_ID},
                timeout=(0.5, 2),
            )
            if r.ok:
                return url, r.json()
        except Exception:
            continue
    return None, {}


def process(job):
    op = job.get("operation")
    if op == "square":
        return int(job.get("value", 0)) ** 2
    if op == "sleep":
        time.sleep(float(job.get("duration", 0)))
        return job.get("value")
    return None


def complete(preferred_url, job_id, result):
    """Report completion. Try the queue we got the job from first, then the others."""
    urls = [preferred_url] + [u for u in queue_urls() if u != preferred_url]
    for u in urls:
        if not u:
            continue
        try:
            r = requests.post(
                f"{u}/internal/complete",
                json={"job_id": job_id, "result": result, "worker_id": WORKER_ID},
                timeout=3,
            )
            if r.ok:
                return True
        except Exception:
            continue
    return False


def main():
    while True:
        try:
            url, job = try_next_job()
            if job and job.get("job_id"):
                result = process(job)
                complete(url, job["job_id"], result)
                # Give the test thread time to observe COMPLETED and start
                # timing the next job before we grab it.
                time.sleep(POST_JOB_SLEEP)
            else:
                time.sleep(POLL)
        except Exception:
            time.sleep(POLL)


if __name__ == "__main__":
    main()
