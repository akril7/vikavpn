import shutil
import subprocess
from functools import wraps


class CommandExecuteError(Exception):
    pass


def check_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if not result:
            raise CommandExecuteError(f"{func.__name__} return False")

        return result

    return wrapper


def run_without_out(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.DEVNULL, **kwargs)


def run_with_check(args: list[str]) -> subprocess.CompletedProcess:
    return run_without_out(args, check=True)


def run_and_check_status(args: list[str]) -> bool:
    return run_without_out(args).returncode == 0


def run_and_get_text(args: list[str]) -> str:
    result = subprocess.run(args,
                            capture_output=True,
                            text=True)
    return result.stdout.strip()


def install_deb(deb_path: str) -> subprocess.CompletedProcess:
    return run_with_check(["sudo", "dpkg", "-i", deb_path])


def uninstall_deb(deb_name: str) -> subprocess.CompletedProcess:
    return run_with_check(["sudo", "dpkg", "-r", deb_name])


def add_user_to_group(user: str, group: str) -> subprocess.CompletedProcess:
    return run_without_out(["sudo", "usermod", "-a", "-G", group, user],
                           check=True)


def delete_group(group: str) -> subprocess.CompletedProcess:
    return run_with_check(["sudo", "groupdel", group])


def is_installed(package: str) -> bool:
    return shutil.which(package) is not None


def install(package: str) -> subprocess.CompletedProcess:
    return run_with_check(["apt", "install", "-y", package])
