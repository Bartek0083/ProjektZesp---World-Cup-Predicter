from __future__ import annotations

import uvicorn


HOST = "127.0.0.1"
PORT = 8011


if __name__ == "__main__":
    uvicorn.run("api:app", host=HOST, port=PORT, access_log=False, log_config=None)
