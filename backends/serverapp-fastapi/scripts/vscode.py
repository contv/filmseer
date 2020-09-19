#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path


def setup():
    venv_path = subprocess.check_output(
        "poetry env info --path".split(),
        cwd=Path(__file__).resolve().parent.parent,
        shell=True,
    )
    venv_path = venv_path.decode("UTF-8").strip("\r\n")

    vscode_settings = Path(".vscode/settings.json")

    settings = dict()

    vscode_settings.parent.mkdir(parents=True, exist_ok=True)
    vscode_settings.touch()

    with open(vscode_settings, "r") as f:
        settings = json.loads(f.read() or "{}")
        settings["python.pythonPath"] = venv_path

    with open(vscode_settings, "w") as f:
        json.dump(settings, f, sort_keys=True, indent=4)

    print("\nSuccessfully configured VSCode!")
    print("python.pythonPath: " + venv_path)
