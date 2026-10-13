import queue
import subprocess
import threading
from dataclasses import dataclass, field

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.cli.console import console


TAIL_LINES = 200
BUFFER_LINES = 500


@dataclass
class _LogBuffer:
    lines: list[str] = field(default_factory=list)

    def append(self, line: str) -> None:
        self.lines.append(line)
        overflow = len(self.lines) - BUFFER_LINES
        if overflow > 0:
            del self.lines[:overflow]

    def render(self, unit: str) -> Panel:
        body = Text("\n".join(self.lines) if self.lines else "[dim]ожидание логов…[/]")
        return Panel(
            body,
            title=f"[bold cyan]Логи {unit}[/]",
            subtitle="[dim]Ctrl+C — выход[/]",
            border_style="cyan",
        )


def show_logs(unit: str) -> None:
    """Открывает live-просмотр логов systemd-юнита. Выход — Ctrl+C."""
    cmd = [
        "journalctl",
        "-u", unit,
        "-f",
        "-n", str(TAIL_LINES),
        "--no-pager",
        "-o", "short-iso",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        console.print("[red]journalctl не найден[/]")
        return

    q: "queue.Queue[str | None]" = queue.Queue()

    def _reader() -> None:
        assert proc.stdout is not None
        try:
            for i in proc.stdout:
                q.put(i.rstrip("\n"))
        finally:
            q.put(None)

    threading.Thread(target=_reader, daemon=True).start()

    buffer = _LogBuffer()

    try:
        with Live(
            buffer.render(unit),
            console=console,
            refresh_per_second=10,
            screen=True,
            transient=False,
        ) as live:
            while True:
                try:
                    line = q.get(timeout=0.1)
                except queue.Empty:
                    live.update(buffer.render(unit))
                    continue

                if line is None:
                    # journalctl завершился — ждём Ctrl+C
                    live.update(buffer.render(unit))
                    continue

                buffer.append(line)
                live.update(buffer.render(unit))
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
