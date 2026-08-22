import time
import torch
from rich.console import Console
from rich.panel import Panel

console = Console(highlight=False)

class GranularProgressLogger:
    """
    Rich terminal progress logger providing granular step-by-step visibility
    into every stage of the handwritten OCR ingestion pipeline.
    Uses ASCII symbols to ensure 100% compatibility with Windows legacy consoles.
    """

    def __init__(self):
        self.start_time = time.time()

    @staticmethod
    def get_vram_info() -> str:
        if torch.cuda.is_available():
            allocated = round(torch.cuda.memory_allocated(0) / 1e9, 2)
            reserved = round(torch.cuda.memory_reserved(0) / 1e9, 2)
            total = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
            return f"{allocated} GB / {total} GB (Reserved: {reserved} GB)"
        return "N/A (CPU Mode)"

    def log_station(self, station_num: int, total_stations: int, title: str, details: str = ""):
        header = f"[STATION {station_num}/{total_stations}] {title}"
        vram = self.get_vram_info()
        body = f"{details}\nGPU VRAM Usage: {vram}" if details else f"GPU VRAM Usage: {vram}"
        console.print(Panel(body, title=header, style="bold cyan", border_style="cyan"))

    def log_step(self, step_msg: str, status: str = "INFO"):
        elapsed = round(time.time() - self.start_time, 2)
        prefix = f"[{elapsed}s]"
        if status == "SUCCESS":
            console.print(f"[bold green]{prefix} [OK] {step_msg}[/bold green]")
        elif status == "WARNING":
            console.print(f"[bold yellow]{prefix} [WARN] {step_msg}[/bold yellow]")
        elif status == "ERROR":
            console.print(f"[bold red]{prefix} [ERROR] {step_msg}[/bold red]")
        else:
            console.print(f"[bold blue]{prefix} -> {step_msg}[/bold blue]")
