import sys
from pathlib import Path
import click
import networkx as nx
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()


@click.group()
def main():
    """Comeback Helper - Math Knowledge Graph & Study Assistant"""
    pass


@main.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Path to PDF course document")
@click.option("--course", "-c", required=True, help="Course Name (e.g. 'Machine Learning' or 'Linear Algebra')")
@click.option("--output-name", "-o", default=None, help="Custom target Markdown file name in Obsidian Vault")
def ingest(file: str, course: str, output_name: str | None):
    """Ingest a PDF course document, run OCR, sanitize LaTeX, and save to Obsidian Vault."""
    console.print(f"[bold cyan]Starting document ingestion for:[/bold cyan] {file}")
    try:
        from src.ingestion.pipeline import IngestionPipeline
        pipeline = IngestionPipeline()
        target_path = pipeline.process_pdf(file, course_name=course, output_filename=output_name)
        console.print(Panel(f"[bold green]Successfully ingested![/bold green]\nNote saved at: [yellow]{target_path}[/yellow]", title="Ingestion Complete"))
    except Exception as e:
        console.print(f"[bold red]Ingestion Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option("--prompt", "-p", required=True, help="Your mathematical query or question")
@click.option("--course", "-c", default=None, help="Filter search to specific course name")
def query(prompt: str, course: str | None):
    """Query your math knowledge graph for conceptual explanations and derivations."""
    console.print(f"[bold cyan]Querying Math Knowledge Base:[/bold cyan] '{prompt}'")
    try:
        from src.retrieval.engine import MathQueryEngine
        engine = MathQueryEngine()
        response = engine.query(prompt, course=course)
        console.print(Panel(Markdown(response), title="Explanation & Derivation"))
    except Exception as e:
        console.print(f"[bold red]Query Error:[/bold red] {e}")
        sys.exit(1)


@main.command(name="atlas-stats")
def atlas_stats():
    """Show atlas telemetry: lattice size, statements per context, validation state."""
    try:
        from src.atlas.store import AtlasStore
        from src.atlas import validate

        store = AtlasStore()
        s = store.stats()

        table = Table(title="Atlas Telemetry")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold green")
        table.add_row("Contexts (lattice)", str(s["contexts"]))
        table.add_row("Contexts populated", f"{s['contexts_used']} / {s['contexts']}")
        table.add_row("Statements", str(s["statements"]))
        table.add_row("Terms", str(s["terms"]))
        table.add_row("Witnesses", str(s["witnesses"]))
        table.add_row("By status", ", ".join(f"{k}({v})" for k, v in s["by_status"].items()) or "-")

        findings = validate.check(store)
        v = validate.summarise(findings)
        table.add_row("Validation", f"{v['errors']} errors, {v['warnings']} warnings")
        console.print(table)

        if s["top_contexts"]:
            busiest = Table(title="Busiest contexts")
            busiest.add_column("Context", style="cyan")
            busiest.add_column("Statements", style="bold green")
            for cid, n in s["top_contexts"]:
                busiest.add_row(cid, str(n))
            console.print(busiest)
    except Exception as e:
        console.print(f"[bold red]Atlas Stats Error:[/bold red] {e}")
        sys.exit(1)


@main.command(name="atlas-index")
@click.option("--note", "-n", type=click.Path(exists=True), help="Index a single note")
@click.option("--rebuild", is_flag=True, help="Discard the atlas and re-extract everything")
def atlas_index(note: str | None, rebuild: bool):
    """Extract statements from vault notes and index them against the context lattice."""
    try:
        from src.atlas.index import index_vault, _print
        _print(index_vault(note=Path(note) if note else None, rebuild=rebuild))
    except Exception as e:
        console.print(f"[bold red]Atlas Index Error:[/bold red] {e}")
        sys.exit(1)


@main.command(name="ladder")
@click.argument("slogan")
def ladder(slogan: str):
    """Show a generalisation ladder: one result across the context lattice."""
    try:
        from src.atlas.store import AtlasStore
        store = AtlasStore()
        rungs = store.ladder(slogan)
        if not rungs:
            console.print(f"[yellow]No statements matching '{slogan}'.[/yellow]")
            return
        table = Table(title=f"Ladder — '{slogan}'")
        table.add_column("Depth", style="dim", justify="right")
        table.add_column("Context", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Slogan")
        for st in rungs:
            colour = {"THEOREM": "green", "FALSE": "red"}.get(st.status.value, "yellow")
            table.add_row(str(store.depth(st.context)), st.context,
                          f"[{colour}]{st.status.value}[/{colour}]", st.slogan[:70])
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Ladder Error:[/bold red] {e}")
        sys.exit(1)


@main.command(name="atlas-check")
def atlas_check():
    """Run the validation gates and list every finding."""
    try:
        from src.atlas.store import AtlasStore
        from src.atlas import validate
        store = AtlasStore()
        findings = validate.check(store)
        if not findings:
            console.print("[bold green]All gates passed.[/bold green]")
            return
        table = Table(title="Validation findings")
        table.add_column("Gate", style="cyan")
        table.add_column("Sev")
        table.add_column("Statement", style="dim")
        table.add_column("Detail")
        for f in findings[:60]:
            colour = "red" if f["severity"] == "error" else "yellow"
            table.add_row(f["gate"], f"[{colour}]{f['severity']}[/{colour}]",
                          f["statement"][:34], f["detail"][:70])
        console.print(table)
        console.print(validate.summarise(findings))
    except Exception as e:
        console.print(f"[bold red]Atlas Check Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
