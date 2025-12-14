"""Interface de linha de comando (CLI) para o projeto"""

import typer
from rich.console import Console
from rich.panel import Panel

from participacao_eleitoral.config import Settings
from participacao_eleitoral.ingestion.pipeline import IngestionPipeline
from participacao_eleitoral.ingestion.models import StatusIngestao
from participacao_eleitoral.ingestion.tse_urls import TSEDatasetURLs
from participacao_eleitoral.utils.logger import ModernLogger

# ===== Bootstrap =====
app = typer.Typer(
    name="participacao-eleitoral",
    help="Pipeline de análise de participação eleitoral brasileira",
    add_completion=False,
)

console = Console()


def _build_pipeline() -> IngestionPipeline:
    settings = Settings()
    logger = ModernLogger(
        level=settings.log_level,
        show_timestamp=settings.show_timestamps,
    )
    return IngestionPipeline(settings=settings, logger=logger)


# ===== Commands =====
@app.command()
def ingest(
    ano: int = typer.Argument(..., help="Ano da eleição (ex: 2024, 2022, 2020)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forçar re-ingestão se já existe"),
):
    """Ingere dados de comparecimento eleitoral do TSE."""

    console.print(f"\n[bold cyan]🚀 Iniciando ingestão de {ano}[/bold cyan]\n")

    pipeline = _build_pipeline()

    # Caminho correto do Parquet
    dataset_dir = (
        pipeline.settings.bronze_dir
        / "comparecimento_abstencao"
        / f"year={ano}"
    )
    parquet_path = dataset_dir / "data.parquet"

    if parquet_path.exists() and not force:
        console.print(
            f"[yellow]⚠️ Dados de {ano} já existem:[/yellow]\n"
            f"  {parquet_path}\n\n"
            f"Use --force para reprocessar.\n"
        )
        raise typer.Exit(0)

    try:
        metadata = pipeline.run(ano)

        if metadata.status != StatusIngestao.SUCESSO:
            raise RuntimeError("Ingestão finalizou com falha")

        console.print(
            Panel.fit(
                f"[bold green]✅ Ingestão concluída com sucesso![/bold green]\n\n"
                f"[cyan]Ano:[/cyan] {metadata.dataset.ano}\n"
                f"[cyan]Dataset:[/cyan] comparecimento_abstencao\n"
                f"[cyan]Arquivo:[/cyan] {metadata.arquivo_destino}\n"
                f"[cyan]Linhas:[/cyan] {metadata.linhas_ingeridas:,}\n"
                f"[cyan]Tamanho:[/cyan] {metadata.tamanho_bytes / 1024 / 1024:.2f} MB\n"
                f"[cyan]Duração:[/cyan] {metadata.duracao_segundos:.1f}s\n"
                f"[cyan]Checksum:[/cyan] {metadata.checksum_sha256[:16]}...\n",
                title="📊 Resultado da Ingestão",
                border_style="green",
            )
        )

    except Exception as exc:
        console.print(
            Panel.fit(
                f"[bold red]❌ Falha na ingestão[/bold red]\n\n"
                f"[cyan]Ano:[/cyan] {ano}\n"
                f"[cyan]Erro:[/cyan] {exc}\n",
                title="Erro",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def list_anos():
    """Lista anos disponíveis para ingestão"""

    settings = Settings()

    console.print("\n[bold cyan]📅 Anos Disponíveis[/bold cyan]\n")

    for ano in TSEDatasetURLs.listar_anos_disponiveis():
        parquet_path = (
            settings.bronze_dir
            / "comparecimento_abstencao"
            / f"year={ano}"
            / "data.parquet"
        )
        status = (
            "[green]✅ Ingerido[/green]"
            if parquet_path.exists()
            else "[dim]⭕ Não ingerido[/dim]"
        )
        console.print(f"  • {ano} - {status}")

    console.print()