from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)
LOG = "/var/log/app/access.log"
os.makedirs(os.path.dirname(LOG), exist_ok=True)

@app.get("/")
def hello():
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z path={request.path} ua={request.headers.get('User-Agent','')}
")
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
