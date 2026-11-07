import subprocess

from .subprocess import check_result, run_with_check, deb_is_installed


def is_docker_install() -> bool:
    return bool(deb_is_installed("docker"))


@check_result
def check_docker_install() -> bool:
    return is_docker_install()


def is_container_running(container_name: str) -> bool:
    result = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                            capture_output=True,
                            text=True)

    if result.returncode != 0:
        return False

    return result.stdout.strip() == "true"


@check_result
def check_is_container_running(container_name: str) -> bool:
    return is_container_running(container_name)


def is_container_exists(container_name: str) -> bool:
    return subprocess.run(["docker", "inspect", container_name],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


@check_result
def check_container_exists(container_name: str) -> bool:
    return is_container_exists(container_name)


def stop_container(container_name: str):
    run_with_check(["docker", "stop", container_name])


def start_container(container_name: str):
    run_with_check(["docker", "start", container_name])


def restart_container(container_name: str):
    run_with_check(["docker", "restart", container_name])


def create_container(container_name: str, image_name: str, args: list[str]):
    run_with_check(["docker", "create",
                    "--restart", "always",
                    "--name", container_name,
                    *args, image_name])


def remove_container(container_name: str):
    run_with_check(["docker", "rm", "-f", container_name])


def remove_image(image_name: str) -> subprocess.CompletedProcess:
    return run_with_check(["docker", "rmi", image_name])


def pull_image(image: str) -> subprocess.CompletedProcess:
    return run_with_check(["docker", "pull", image])
