import queue
import shutil
import subprocess
import threading
from dataclasses import dataclass, field

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.cli.console import console


TAIL_LINES = 200          # сколько строк запрашиваем у journalctl при старте
BUFFER_LINES = 500        # сколько строк держим в памяти
RESERVED_ROWS = 4         # рамка (2) + заголовок (1) + subtitle (1)


@dataclass
class _LogBuffer:
    """Кольцевой буфер строк с рендером «хвоста» под высоту терминала."""
    lines: list[str] = field(default_factory=list)

    def append(self, line: str) -> None:
        self.lines.append(line)
        overflow = len(self.lines) - BUFFER_LINES
        if overflow > 0:
            del self.lines[:overflow]

    def _visible_count(self) -> int:
        """Сколько строк влезает в панель при текущем размере терминала."""
        term_height = shutil.get_terminal_size(fallback=(80, 24)).lines
        return max(1, term_height - RESERVED_ROWS)

    def render(self, unit: str) -> Panel:
        visible = self._visible_count()
        tail = self.lines[-visible:]

        if tail:
            body = Text("\n".join(tail))
        else:
            body = Text("Р¶РґС‘Рј Р»РѕРіРёвЂ¦", style="dim")

        return Panel(
            body,
            title=f"[bold cyan]Р›РѕРіРё {unit}[/]",
            subtitle="[dim]Ctrl+C вЂ” РІС‹Р№С‚Рё[/]",
            border_style="cyan",
        )


def _terminate(proc: subprocess.Popen) -> None:
    """Аккуратно гасим journalctl: SIGTERM, потом SIGKILL."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass


def show_logs(unit: str) -> None:
    """Live-tail логов systemd-юнита с отображением последних N строк.

    Ctrl+C — выход. Панель всегда показывает актуальный хвост,
    не «уплывает» вверх и не обрезается, как при рендере всего буфера.
    """
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
            # Отдельная группа процессов, чтобы Ctrl+C в терминале
            # не убивал родителя (нас) напрямую, а мы сами решали,
            # что делать. См. обработку KeyboardInterrupt ниже.
            start_new_session=True,
        )
    except FileNotFoundError:
        console.print("[red]journalctl РЅРµ РЅР°Р№РґРµРЅ[/]")
        return

    q: "queue.Queue[str | None]" = queue.Queue()

    def _reader() -> None:
        assert proc.stdout is not None
        try:
            for raw in proc.stdout:
                q.put(raw.rstrip("\n"))
        finally:
            q.put(None)

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()

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
                    live.update(buffer.render(unit))
                    break

                buffer.append(line)
                live.update(buffer.render(unit))
    except KeyboardInterrupt:
        pass
    finally:
        _terminate(proc)
        reader.join(timeout=1)
