import subprocess

from src.cli.console import muted


# Юниты, которые нам интересны: наши и используемые извне.
PREFIXES = ("vikavpn-",)
EXTRA_UNITS = ("mita", "mtproxyl", "nginx", "docker")


def list_units() -> list[str]:
    """Возвращает список systemd-юнитов, установленных на машине.

    Ищет все *.service, у которых имя начинается с одного из PREFIXES
    или равно одному из EXTRA_UNITS.
    """
    try:
        result = subprocess.run(
            ["systemctl", "list-unit-files", "--type=service",
             "--no-legend", "--no-pager", "--plain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        muted("systemctl не найден — journalctl недоступен")
        return []

    if result.returncode != 0:
        muted(f"systemctl вернул код {result.returncode}")
        return []

    units: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        if not name.endswith(".service"):
            continue
        short = name[: -len(".service")]

        if short.startswith(PREFIXES) or short in EXTRA_UNITS:
            units.append(short)

    return sorted(set(units))
