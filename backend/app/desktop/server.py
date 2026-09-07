"""The local API server the desktop window talks to."""

import logging
import socket
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

import uvicorn
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# The server is only ever reached from this machine. Binding the loopback
# interface is the whole security model of the desktop application: with
# authentication gone, listening on 0.0.0.0 would hand the school's network
# write access to the timetable.
HOST = "127.0.0.1"

STARTUP_TIMEOUT_SECONDS = 30.0
_POLL_INTERVAL_SECONDS = 0.1


def find_free_port() -> int:
    """Ask the operating system for a free port on the loopback interface.

    A fixed port would collide with whatever else the teacher happens to be
    running, and that failure would look like "the program does not open".
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((HOST, 0))
        return int(probe.getsockname()[1])


@dataclass
class LocalServer:
    """A uvicorn server running on a background thread."""

    port: int
    _server: uvicorn.Server
    _thread: threading.Thread

    @property
    def base_url(self) -> str:
        return f"http://{HOST}:{self.port}"

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)


def start(app: FastAPI, port: int | None = None) -> LocalServer:
    """Start the API in the background and return once it answers."""
    port = port or find_free_port()
    config = uvicorn.Config(app, host=HOST, port=port, log_level="warning", access_log=False)
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="horarios-api", daemon=True)
    thread.start()

    local = LocalServer(port=port, _server=server, _thread=thread)
    wait_until_ready(local.base_url)
    return local


def wait_until_ready(base_url: str, timeout: float = STARTUP_TIMEOUT_SECONDS) -> None:
    """Block until ``/health`` answers, or raise once the timeout is spent."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=1) as response:
                if response.status == 200:
                    logger.info("API ready on %s", base_url)
                    return
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(_POLL_INTERVAL_SECONDS)
    raise RuntimeError(f"The local server did not start within {timeout:.0f} seconds")
