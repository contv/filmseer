import multiprocessing
import os
import signal
import subprocess
from pathlib import Path


def run_command(command):
    p = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    os.kill(p.pid, signal.CTRL_C_EVENT)
    return iter(p.stdout.readline, b"")


def start():

    n_cores = multiprocessing.cpu_count()

    conf_file = str(
        (Path(__file__).resolve().parent.parent / "gunicorn_conf.py").resolve()
    )

    command = (
        'gunicorn -k "uvicorn.workers.UvicornWorker" -c "'
        + conf_file
        + '" -w '
        + str(n_cores)
        + ' "app.main:app"'
    ) if os.name != "nt" else (
        "uvicorn app.main:app --reload --host 0.0.0.0 --port 80 --workers " + str(n_cores)
    )
    print("Running: " + command)

    for line in run_command(command):
        print(line)
