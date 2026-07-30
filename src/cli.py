import sys
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

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
    """
    Ingest a PDF course document, run Gemini Vision OCR, sanitize LaTeX, and save to Obsidian Vault.
    """
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
def query(prompt: str):
    """
    Query your math knowledge graph for conceptual explanations and derivations.
    """
    console.print(f"[bold cyan]Querying Math Knowledge Base:[/bold cyan] '{prompt}'")
    try:
        from src.retrieval.engine import MathQueryEngine
        engine = MathQueryEngine()
        response = engine.query(prompt)
        console.print(Panel(Markdown(response), title="Explanation & Derivation"))
    except Exception as e:
        console.print(f"[bold red]Query Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
