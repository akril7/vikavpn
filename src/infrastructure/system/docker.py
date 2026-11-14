import json
import subprocess

from src.infrastructure.system.subprocess import run_and_check_status


def container_exists(name: str):
    try:
        result = run_and_check_status(["docker", "inspect", "--format", "{{json .State}}", name])
        return result == 0
    except FileNotFoundError:
        return False


def container_is_running(name: str):
    try:
        result = subprocess.run(["docker", "inspect", "--format", "{{json .State}}", name])
        if result.returncode != 0:
            return False
        state = json.loads(result.stdout)
        return state.get("Running", False)
    except FileNotFoundError:
        return False
