import json
import sys
from pathlib import Path
import click
import networkx as nx
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()


# ---------------------------------------------------------------------------
# Machine-readable output
#
# Every command takes --json. When set, the command prints exactly one JSON
# object on stdout and nothing else, so a caller (the skill, a script) can
# parse it without scraping Rich's formatting. Without the flag the human
# output is unchanged. Errors emit {"status": "error", ...} under --json
# rather than a Rich panel, so a failure is still parseable.
# ---------------------------------------------------------------------------

def _json_mode(ctx, param, value):
    """Moves log output to stderr as soon as --json is parsed.

    Loguru's console sink writes to stdout, so without this the JSON object
    would be interleaved with log lines and fail to parse. Runs as a click
    callback rather than in each command body so it cannot be forgotten.
    """
    if value:
        from shared.logger import use_stderr_console
        use_stderr_console()
    return value


_JSON = click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    callback=_json_mode,
    help="Emit a single machine-readable JSON object on stdout (logs go to stderr).",
)


def _emit(payload: dict):
    """Prints one JSON object on stdout, bypassing Rich."""
    click.echo(json.dumps(payload, ensure_ascii=False))


def _fail(as_json: bool, label: str, error: Exception):
    if as_json:
        _emit({"status": "error", "command": label, "error": str(error)})
    else:
        console.print(f"[bold red]{label} Error:[/bold red] {error}")
    sys.exit(1)


@click.group()
def main():
    """Comeback Helper - Math Knowledge Graph & Study Assistant"""
    pass


@main.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Path to PDF course document")
@click.option("--course", "-c", required=True, help="Course Name (e.g. 'Machine Learning' or 'Linear Algebra')")
@click.option("--output-name", "-o", default=None, help="Custom target Markdown file name in Obsidian Vault")
@_JSON
def ingest(file: str, course: str, output_name: str | None, as_json: bool):
    """Ingest a PDF course document, run OCR, sanitize LaTeX, and save to Obsidian Vault.

    Writes the vault note only. It does NOT update the graph or vector store —
    run `rebuild-graph --no-force` afterwards to index just the new note.
    """
    if not as_json:
        console.print(f"[bold cyan]Starting document ingestion for:[/bold cyan] {file}")
    try:
        from ingestion.app.pipeline import IngestionPipeline
        pipeline = IngestionPipeline()
        target_path = pipeline.process_pdf(file, course_name=course, output_filename=output_name)

        if as_json:
            _emit({
                "status": "success",
                "command": "ingest",
                "note_path": str(target_path),
                "course": course,
                "indexed": False,
            })
        else:
            console.print(Panel(f"[bold green]Successfully ingested![/bold green]\nNote saved at: [yellow]{target_path}[/yellow]", title="Ingestion Complete"))
    except Exception as e:
        _fail(as_json, "Ingestion", e)


@main.command()
@click.option("--prompt", "-p", required=True, help="Your mathematical query or question")
@click.option("--course", "-c", default=None, help="Filter search to specific course name")
@_JSON
def query(prompt: str, course: str | None, as_json: bool):
    """Query your math knowledge graph for conceptual explanations and derivations."""
    if not as_json:
        console.print(f"[bold cyan]Querying Math Knowledge Base:[/bold cyan] '{prompt}'")
    try:
        from src.wiring import build_stack
        _, _, engine = build_stack()
        response = engine.query(prompt, course=course)

        if as_json:
            _emit({
                "status": "success",
                "command": "query",
                "prompt": prompt,
                "course": course,
                "answer": response,
            })
        else:
            console.print(Panel(Markdown(response), title="Explanation & Derivation"))
    except Exception as e:
        _fail(as_json, "Query", e)


@main.command(name="graph-stats")
@_JSON
def graph_stats(as_json: bool):
    """Display comprehensive health telemetry and statistics for the Knowledge Graph."""
    try:
        from src.wiring import build_indexer
        indexer = build_indexer()
        G = indexer.graph

        components = 0
        isolates = 0
        types_count: dict[str, int] = {}
        if G.number_of_nodes() > 0:
            components = nx.number_connected_components(G.to_undirected())
            isolates = len(list(nx.isolates(G)))
            for _, data in G.nodes(data=True):
                etype = data.get("entity_type", "Concept")
                types_count[etype] = types_count.get(etype, 0) + 1

        if as_json:
            _emit({
                "status": "success",
                "command": "graph-stats",
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "connected_components": components,
                "isolated_nodes": isolates,
                "entity_types": types_count,
            })
            return

        table = Table(title="Math Knowledge Graph Telemetry")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold green")

        table.add_row("Total Nodes", str(G.number_of_nodes()))
        table.add_row("Total Edges", str(G.number_of_edges()))

        if G.number_of_nodes() > 0:
            table.add_row("Connected Components", f"{components} [Warning]" if components > 1 else f"{components} [OK]")
            table.add_row("Isolated Nodes", f"{isolates} [Warning]" if isolates > 0 else f"{isolates} [OK]")
            types_str = ", ".join([f"{k}({v})" for k, v in types_count.items()])
            table.add_row("Entity Types", types_str)

        console.print(table)
    except Exception as e:
        _fail(as_json, "Graph Stats", e)


@main.command(name="graph-preview")
@click.option("--note", "-n", required=True, type=click.Path(exists=True), help="Path to markdown note")
@_JSON
def graph_preview(note: str, as_json: bool):
    """Dry-run entity extraction on a single Markdown note without modifying the index."""
    note_path = Path(note)
    if not as_json:
        console.print(f"[bold cyan]Running dry-run extraction on:[/bold cyan] {note_path.name}")
    try:
        from src.wiring import build_indexer
        indexer = build_indexer()
        content = note_path.read_text(encoding="utf-8")
        extraction = indexer.extract_from_text(content, use_llm=True, course_domain="Differential Equations")

        if as_json:
            _emit({
                "status": "success",
                "command": "graph-preview",
                "note": str(note_path),
                "nodes": [
                    {
                        "name": n.name,
                        "entity_type": str(getattr(n.entity_type, "value", n.entity_type)),
                        "description": n.description,
                        "taxonomy": n.taxonomy.model_dump() if hasattr(n.taxonomy, "model_dump") else {},
                    }
                    for n in extraction.nodes
                ],
                "edges": [
                    {
                        "source": e.source,
                        "target": e.target,
                        "relation": str(getattr(e.relation, "value", e.relation)),
                    }
                    for e in extraction.edges
                ],
            })
            return

        console.print(f"[bold green]Extracted {len(extraction.nodes)} Nodes:[/bold green]")
        for n in extraction.nodes:
            console.print(f" • [{n.entity_type}] [bold]{n.name}[/bold] — {n.description[:80]}")

        console.print(f"\n[bold green]Extracted {len(extraction.edges)} Edges:[/bold green]")
        for e in extraction.edges:
            console.print(f" • {e.source} --[{e.relation}]--> {e.target}")
    except Exception as e:
        _fail(as_json, "Graph Preview", e)


@main.command(name="rebuild-graph")
@click.option("--use-llm/--no-llm", default=True, help="Whether to use LLM for extraction (default: True)")
@click.option(
    "--force/--no-force",
    default=True,
    help="Re-extract every note (default). --no-force indexes only notes whose "
         "SHA-256 changed, which is what you want after ingesting a single PDF.",
)
@_JSON
def rebuild_graph(use_llm: bool, force: bool, as_json: bool):
    """Rebuild the knowledge graph index for Markdown notes in the Obsidian vault."""
    if not as_json:
        console.print(f"[bold cyan]Rebuilding Knowledge Graph (use_llm={use_llm}, force={force})...[/bold cyan]")
    try:
        from src.wiring import build_indexer
        from vector.app.store import LocalVectorStore
        # Without a vector store, _resolve_entity() short-circuits and never
        # merges anything — this was silently disabling entity resolution on
        # every CLI rebuild (e.g. "Wronskian" / "wronskian" staying separate
        # nodes), even though the server path always wires one in.
        indexer = build_indexer(vector_store=LocalVectorStore())
        G = indexer.build_or_update_index(use_llm=use_llm, force=force)

        if as_json:
            _emit({
                "status": "success",
                "command": "rebuild-graph",
                "use_llm": use_llm,
                "force": force,
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
            })
        else:
            console.print(Panel(f"[bold green]Graph Rebuild Complete![/bold green]\nTotal Nodes: {G.number_of_nodes()}\nTotal Edges: {G.number_of_edges()}", title="Rebuild Success"))
    except Exception as e:
        _fail(as_json, "Rebuild", e)


@main.command(name="authority-seed-msc")
@click.option("--csv", "csv_path", default=None, type=click.Path(exists=True), help="Local MSC2020 CSV; downloads from msc2020.org if omitted and not already cached")
@_JSON
def authority_seed_msc(csv_path: str | None, as_json: bool):
    """Load MSC2020 taxonomy codes into .storage/concepts.db. Idempotent."""
    try:
        from graph.app.authority import seed_msc2020
        result = seed_msc2020(csv_path=Path(csv_path) if csv_path else None)
        if as_json:
            _emit({"status": "success", "command": "authority-seed-msc", **result})
        else:
            console.print(Panel(
                f"[bold green]MSC2020 loaded.[/bold green]\nRows: {result['rows_loaded']}\n"
                f"Source: {result['csv_path']}{' (freshly downloaded)' if result['fetched'] else ''}",
                title="Authority Seed",
            ))
    except Exception as e:
        _fail(as_json, "Authority Seed", e)


@main.command(name="authority-resolve")
@click.option("--label", "-l", required=True, help="Surface form to resolve, e.g. 'lipschitz-condition'")
@_JSON
def authority_resolve(label: str, as_json: bool):
    """Resolve one surface form to a concept id (alias table -> Wikidata -> mint CUST_).

    Read/write against .storage/concepts.db only — never touches graph.json.
    """
    try:
        from graph.app.authority import get_or_create_concept
        concept_id = get_or_create_concept(label)
        if as_json:
            _emit({
                "status": "success",
                "command": "authority-resolve",
                "label": label,
                "concept_id": concept_id,
                "minted": concept_id.startswith("CUST_"),
            })
        else:
            kind = "minted (no Wikidata match)" if concept_id.startswith("CUST_") else "Wikidata"
            console.print(f"[bold]{label}[/bold] -> [cyan]{concept_id}[/cyan] ({kind})")
    except Exception as e:
        _fail(as_json, "Authority Resolve", e)


@main.command(name="authority-stats")
@_JSON
def authority_stats(as_json: bool):
    """Report concepts.db counts: MSC codes, concepts by authority, aliases, Wikidata cache."""
    try:
        from graph.app.authority import stats
        result = stats()
        if as_json:
            _emit({"status": "success", "command": "authority-stats", **result})
        else:
            table = Table(title="Authority DB (.storage/concepts.db)")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold green")
            for k, v in result.items():
                table.add_row(k, str(v))
            console.print(table)
    except Exception as e:
        _fail(as_json, "Authority Stats", e)


if __name__ == "__main__":
    main()
