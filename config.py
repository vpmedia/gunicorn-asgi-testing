from __future__ import annotations

from multiprocessing import cpu_count
from typing import Any
import logging


def max_workers() -> int:
    """Auto detect max worker count."""
    return min(cpu_count(), 2)


def on_starting(server: Any) -> None:
    """
    Attach a set of IDs that can be temporarily re-used.

    Used on reloads when each worker exists twice.
    """
    server._worker_id_overload = set()


def nworkers_changed(server: Any, new_value: int, old_value: int) -> None:
    """
    Get called on startup too.

    Set the current number of workers.  Required if we raise the worker count
    temporarily using TTIN because server.cfg.workers won't be updated and if
    one of those workers dies, we wouldn't know the ids go that far.
    """
    server._worker_id_current_workers = new_value


def _next_worker_id(server: Any) -> int:
    """If there are IDs open for re-use, take one.  Else look for a free one."""
    if server._worker_id_overload:
        return server._worker_id_overload.pop()  # type: ignore[no-any-return]

    in_use = {w._worker_id for w in tuple(server.WORKERS.values()) if w.alive}
    free = set(range(1, server._worker_id_current_workers + 1)) - in_use

    return free.pop()


def on_reload(server: Any) -> None:
    """Add a full set of ids into overload so it can be re-used once."""
    server._worker_id_overload = set(range(1, server.cfg.workers + 1))


def pre_fork(server: Any, worker: Any) -> None:
    """Attach the next free worker_id before forking off."""
    worker._worker_id = _next_worker_id(server)


def post_fork(server: Any, worker: Any) -> None:
    """Post-fork handler."""
    worker_id = worker._worker_id
    server.log.info("Worker spawned", extra={"pid": worker.pid, "worker_id": worker_id})


bind = "0.0.0.0:8000"
worker_class = "asgi"
asgi_loop = "uvloop"
asgi_lifespan = "on"
# worker_class = "uvicorn.workers.UvicornWorker"
workers = max_workers()
keepalive = 30
forwarded_allow_ips = "*"
enable_stdio_inheritance = True
log_level = "debug"
access_logfile = None
error_logfile = None
disable_redirect_access_to_syslog = True
no_sendfile = True
statsd_host = "127.0.0.1:8125"
statsd_prefix = ""
dogstatsd_tags = "service_name:gunicorn_asgi_test"

logging.basicConfig(level=logging.DEBUG)
logging.info("config loaded")
