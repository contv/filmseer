import importlib
import json
import os
import platform
import sys
from multiprocessing import Process, cpu_count
from pathlib import Path

from dotenv import dotenv_values, find_dotenv


def start():
    os.chdir(Path(__file__).resolve().parent.parent)
    if find_dotenv(filename=".env") == "":
        print(
            "ERROR: Unable to locate `.env` in the root directory of the server app.",
            file=sys.stderr,
        )
        sys.exit(1)
    env_dict = dotenv_values(find_dotenv(filename=".env"))

    dev_mode = (
        True
        if (env_dict.get("DEV_MODE", "True").lower().strip())
        in ["y", "yes", "1", "true"]
        else False
    )

    # Load server configurations
    server_host = env_dict.get("SERVER_HOST", "127.0.0.1").strip() or "127.0.0.1"

    server_ports = []
    # Multiple ports
    try:
        server_ports = (
            [
                int(x)
                for x in list(json.loads(env_dict.get("SERVER_PORTS") or "8000"))
                if str(x).isdigit() and (0 < int(x) < 65535)
            ]
            if not isinstance(
                json.loads(env_dict.get("SERVER_PORTS") or "8000"), (int, float)
            )
            else [int(json.loads(env_dict.get("SERVER_PORTS") or "8000"))]
        )
    except json.decoder.JSONDecodeError:
        print(
            "ERROR: SERVER_PORTS can only be either an int (0 - 65535) or a json array of ints.",
            file=sys.stderr,
        )
        sys.exit(1)

    server_workers = round(
        min(
            float(
                env_dict.get("SERVER_WORKERS_PER_CORE", "1")
                if env_dict.get("SERVER_WORKERS_PER_CORE", "1")
                .replace(".", "", 1)
                .isdigit()
                else "1"
            )
            * cpu_count(),
            int(
                env_dict.get("SERVER_MAX_WORKERS", "0")
                if env_dict.get("SERVER_MAX_WORKERS", "0").isdigit()
                else "0"
            )
            or float("inf"),
        )
    )

    server_worker_max_requests = int(
        env_dict.get("SERVER_WORKER_MAX_REQUESTS", "0")
        if env_dict.get("SERVER_WORKER_MAX_REQUESTS", "0").isdigit()
        else "0"
    )

    server_max_backlog_connections = int(
        env_dict.get("SERVER_MAX_BACKLOG_CONNECTIONS", "0")
        if env_dict.get("SERVER_MAX_BACKLOG_CONNECTIONS", "0").isdigit()
        else "0"
    )

    server_keepalive_seconds = int(
        env_dict.get("SERVER_KEEPALIVE_SECONDS", "0")
        if env_dict.get("SERVER_KEEPALIVE_SECONDS", "0").isdigit()
        else "0"
    )

    server_log_level = (
        (
            env_dict.get("SERVER_LOG_LEVEL", "info")
            if env_dict.get("SERVER_LOG_LEVEL", "info").lower().strip()
            in ["critical", "error", "warning", "info", "debug", "trace"]
            else "info"
        )
        .lower()
        .strip()
    )

    server_container = (
        (
            env_dict.get("SERVER_CONTAINER", "uvicorn")
            if env_dict.get("SERVER_CONTAINER", "uvicorn").lower().strip()
            in ["uvicorn", "gunicorn"]
            else "info"
        )
        .lower()
        .strip()
    )

    server_conf_options = {}
    server_conf_script = env_dict.get("SERVER_CONTAINER", "")
    if server_conf_script != "":
        if server_conf_script.startswith("python:"):
            server_conf_options = vars(
                importlib.import_module(server_conf_script[len("python:") :])
            ).get("options", {})
        elif server_conf_script.startswith("file:"):
            filename = server_conf_script[len("file:") :]
            if not os.path.exists(filename):
                print("ERROR: " + filename + " doesn't exist.", file=sys.stderr)
                sys.exit(1)

            try:
                module_name = "__config__"
                if os.path.splitext(filename)[1] in [".py", ".pyc"]:
                    spec = importlib.util.spec_from_file_location(module_name, filename)
                else:
                    print(
                        "WARNING: Configuration file should have a valid Python extension."
                    )
                    loader_ = importlib.machinery.SourceFileLoader(
                        module_name, filename
                    )
                    spec = importlib.util.spec_from_file_location(
                        module_name, filename, loader=loader_
                    )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            except Exception:
                print("Failed to read config file: %s" % filename, file=sys.stderr)
                sys.exit(1)
            server_conf_options = vars(mod).get("options", {})
    del server_conf_script

    # Load SSL configurations
    ssl_key_file = (
        env_dict.get("SSL_KEY_FILE", "")
        if not env_dict.get("SSL_KEY_FILE", "")
        or not os.path.exists(env_dict.get("SSL_KEY_FILE", ""))
        else ""
    ) or None

    ssl_cert_file = (
        env_dict.get("SSL_CERT_FILE", "")
        if not env_dict.get("SSL_CERT_FILE", "")
        or not os.path.exists(env_dict.get("SSL_CERT_FILE", ""))
        else ""
    ) or None

    ssl_ca_cert_file = (
        env_dict.get("SSL_CA_CERT_FILE", "")
        if not env_dict.get("SSL_CA_CERT_FILE", "")
        or not os.path.exists(env_dict.get("SSL_CA_CERT_FILE", ""))
        else ""
    ) or None

    ssl_version = (
        env_dict.get("SSL_VERSION", "")
        if env_dict.get("SSL_VERSION", "").startswith("PROTOCOL_")
        and vars(importlib.import_module("ssl")).get(env_dict.get("SSL_VERSION", ""))
        is not None
        else ""
    ) or "PROTOCOL_TLS_SERVER"

    ssl_cert_requirement = (
        env_dict.get("SSL_CERT_REQUIREMENT", "")
        if env_dict.get("SSL_CERT_REQUIREMENT", "").startswith("CERT_")
        and vars(importlib.import_module("ssl")).get(
            env_dict.get("SSL_CERT_REQUIREMENT", "")
        )
        is not None
        else ""
    ) or "CERT_OPTIONAL"

    ssl_ciphers = (env_dict.get("SSL_CIPHERS", "")) or "TLSv1"

    # Start Server Container
    if server_container == "uvicorn":
        # Start Uvicorn
        import uvicorn

        uvicorn_instances = {}
        uvicorn_config = {
            "app": "app.main:app",
            "host": server_host,
            "workers": server_workers,
            "limit_max_requests": server_worker_max_requests or None,
            "backlog": server_max_backlog_connections,
            "timeout_keep_alive": server_keepalive_seconds,
            "log_level": server_log_level,
        }

        if ssl_key_file and ssl_cert_file and ssl_ca_cert_file:
            ssl_mod = vars(importlib.import_module("ssl"))
            uvicorn_config.update(
                {
                    "ssl_keyfile": ssl_key_file,
                    "ssl_certfile": ssl_cert_file,
                    "ssl_ca_certs": ssl_ca_cert_file,
                    "ssl_version": ssl_mod.get(ssl_version),
                    "ssl_cert_reqs": ssl_mod.get(ssl_cert_requirement),
                    "ssl_ciphers": ssl_ciphers,
                }
            )
            del ssl_mod

        if dev_mode:
            uvicorn_config.update(
                {
                    "reload": True,
                }
            )

        uvicorn_config.update(server_conf_options)
        print("here", dev_mode, server_ports)

        for server_port in server_ports:
            if dev_mode:
                print(
                    "DEBUG: Starting Param:",
                    {
                        **uvicorn_config,
                        **{
                            "port": server_port,
                        },
                    },
                )
            uvicorn_instances[server_port] = Process(
                target=uvicorn.run,
                kwargs={
                    **uvicorn_config,
                    **{
                        "port": server_port,
                    },
                },
            )
            uvicorn_instances[server_port].daemon = False
            uvicorn_instances[server_port].start()
        try:
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("INFO: Shutting down uvicorn instances...")
            for server_port, instance in uvicorn_instances.items():
                print("INFO: Stopping the instance on port " + str(server_port))
                instance.terminate()
            print("INFO: Shutting down the main thread...")
            sys.exit(0)
    elif server_container == "gunicorn":
        if platform.system() == "Windows":
            # Gunicorn does not support Windows, and Waitress is incomplete.
            # The only option here is to use Uvicorn directly.
            print(
                "ERROR: gunicorn does not support Windows, try uvicorn instead.",
                file=sys.stderr,
            )
            sys.exit(1)
        # Create custom instances of gunicorn
        print("ERROR: UNFINISHED")
        sys.exit(1)
