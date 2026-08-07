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


@main.command(name="graph-stats")
def graph_stats():
    """Display comprehensive health telemetry and statistics for the Knowledge Graph."""
    try:
        from src.graph.indexer import MathGraphIndexer
        indexer = MathGraphIndexer()
        G = indexer.graph

        table = Table(title="Math Knowledge Graph Telemetry")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold green")

        table.add_row("Total Nodes", str(G.number_of_nodes()))
        table.add_row("Total Edges", str(G.number_of_edges()))

        if G.number_of_nodes() > 0:
            undirected = G.to_undirected()
            num_cc = nx.number_connected_components(undirected)
            isolates = len(list(nx.isolates(G)))
            table.add_row("Connected Components", f"{num_cc} [Warning]" if num_cc > 1 else f"{num_cc} [OK]")
            table.add_row("Isolated Nodes", f"{isolates} [Warning]" if isolates > 0 else f"{isolates} [OK]")

            # Entity type distribution
            types_count = {}
            for _, data in G.nodes(data=True):
                etype = data.get("entity_type", "Concept")
                types_count[etype] = types_count.get(etype, 0) + 1
            types_str = ", ".join([f"{k}({v})" for k, v in types_count.items()])
            table.add_row("Entity Types", types_str)

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Graph Stats Error:[/bold red] {e}")
        sys.exit(1)


@main.command(name="graph-preview")
@click.option("--note", "-n", required=True, type=click.Path(exists=True), help="Path to markdown note")
def graph_preview(note: str):
    """Dry-run 3-tier entity extraction on a single Markdown note without modifying index."""
    note_path = Path(note)
    console.print(f"[bold cyan]Running dry-run extraction on:[/bold cyan] {note_path.name}")
    try:
        from src.graph.indexer import MathGraphIndexer
        indexer = MathGraphIndexer()
        content = note_path.read_text(encoding="utf-8")
        extraction = indexer.extract_from_text(content, use_llm=True, course_domain="Differential Equations")

        console.print(f"[bold green]Extracted {len(extraction.nodes)} Nodes:[/bold green]")
        for n in extraction.nodes:
            console.print(f" • [{n.entity_type}] [bold]{n.name}[/bold] — {n.description[:80]}")

        console.print(f"\n[bold green]Extracted {len(extraction.edges)} Edges:[/bold green]")
        for e in extraction.edges:
            console.print(f" • {e.source} --[{e.relation}]--> {e.target}")
    except Exception as e:
        console.print(f"[bold red]Graph Preview Error:[/bold red] {e}")
        sys.exit(1)


@main.command(name="rebuild-graph")
@click.option("--use-llm/--no-llm", default=True, help="Whether to use LLM for extraction (default: True)")
def rebuild_graph(use_llm: bool):
    """Rebuild knowledge graph index for all Markdown notes in Obsidian vault."""
    console.print(f"[bold cyan]Rebuilding Knowledge Graph (use_llm={use_llm})...[/bold cyan]")
    try:
        from src.graph.indexer import MathGraphIndexer
        indexer = MathGraphIndexer()
        G = indexer.build_or_update_index(use_llm=use_llm, force=True)
        console.print(Panel(f"[bold green]Graph Rebuild Complete![/bold green]\nTotal Nodes: {G.number_of_nodes()}\nTotal Edges: {G.number_of_edges()}", title="Rebuild Success"))
    except Exception as e:
        console.print(f"[bold red]Rebuild Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
