import typer

# Configurações globais (paths, timeouts, etc.)
from participacao_eleitoral.config import Settings

# Pipeline orquestrador
from participacao_eleitoral.ingestion.pipeline import IngestionPipeline
from participacao_eleitoral.silver.region_mapper import RegionMapper
from participacao_eleitoral.silver.schemas.comparecimento_silver import SCHEMA_SILVER

# Transformação Silver (importados no topo para evitar erros de importação)
from participacao_eleitoral.silver.transformer import BronzeToSilverTransformer

# Logger estruturado
from participacao_eleitoral.utils.logger import ModernLogger

app = typer.Typer(help="CLI para ingestão de dados eleitorais do TSE")

data_app = typer.Typer(help="Comandos para manipulação de dados")
app.add_typer(data_app, name="data")

validate_app = typer.Typer(help="Comandos para validação")
app.add_typer(validate_app, name="validate")

utils_app = typer.Typer(help="Comandos utilitários")
app.add_typer(utils_app, name="utils")


@data_app.command()
def ingest(
    ano: int = typer.Argument(
        ...,
        help="Ano da eleição (ex: 2022, 2024)",
    ),
    log_level: str = typer.Option(
        "INFO",
        help="Nível de log (DEBUG, INFO, WARNING, ERROR)",
    ),
) -> None:
    """
    Executa a ingestão do dataset de comparecimento eleitoral.

    Este comando inicializa configurações, logger e chama o pipeline.
    """

    settings = Settings()
    settings.setup_dirs()  # Criar diretórios necessários

    log_file_path = settings.logs_dir / f"comparecimento_{ano}.log"
    logger = ModernLogger(level=log_level, log_file=str(log_file_path))

    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    try:
        logger.info(
            "cli_ingest_iniciada",
            ano=ano,
        )

        pipeline.run(ano)

        logger.success(
            "cli_ingest_concluida",
            ano=ano,
        )

        typer.echo(f"Ingestão do ano {ano} concluída com sucesso.")

    except Exception as exc:
        logger.error(
            "cli_ingest_falhou",
            ano=ano,
            erro=str(exc),
            tipo_erro=type(exc).__name__,
        )

        typer.echo(
            f"Erro ao executar ingestão do ano {ano}: {exc}",
            err=True,
        )

        raise typer.Exit(code=1) from exc


@data_app.command()
def transform(
    ano: int = typer.Argument(..., help="Ano da eleição"),
    log_level: str = typer.Option("INFO", help="Nível de log"),
) -> None:
    """
    Transforma dados da camada Bronze para Silver.

    Args:
        ano: Ano da eleição para transformar.
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR).

    Raises:
        typer.Exit: Se ocorrer erro durante transformação.

    Examples:
        >>> uv run participacao-eleitoral data transform 2022
        >>> uv run participacao-eleitoral data transform 2024 --log-level DEBUG
    """

    settings = Settings()
    settings.setup_dirs()

    log_file_path = settings.logs_dir / f"transform_silver_{ano}.log"
    logger = ModernLogger(level=log_level, log_file=str(log_file_path))

    # Criar caminhos
    bronze_path = settings.bronze_dir / "comparecimento_abstencao" / f"year={ano}" / "data.parquet"
    silver_path = settings.silver_dir / "comparecimento_abstencao" / f"year={ano}" / "data.parquet"

    try:
        logger.info(
            "cli_transform_iniciada",
            ano=ano,
            bronze=str(bronze_path),
            silver=str(silver_path),
        )

        # Verificar se bronze existe
        if not bronze_path.exists():
            typer.echo(
                f"Erro: Arquivo bronze não encontrado em {bronze_path}",
                err=True,
            )
            typer.echo(
                "Execute primeiro: uv run participacao-eleitoral data ingest {ano}",
                err=True,
            )
            raise typer.Exit(code=1)

        # Criar transformador e executar
        transformer = BronzeToSilverTransformer(logger=logger)

        # Criar mapper de região e schema
        region_mapper = RegionMapper()
        result = transformer.transform(
            bronze_path,
            silver_path,
            region_mapper=region_mapper,
            schema=SCHEMA_SILVER,
        )

        logger.success(
            "cli_transform_concluida",
            ano=ano,
            linhas=result.linhas,
        )

        typer.echo(f"Transformação do ano {ano} concluída com sucesso.")
        typer.echo(f"Linhas processadas: {result.linhas:,}")

    except Exception as exc:
        logger.error(
            "cli_transform_falhou",
            ano=ano,
            erro=str(exc),
            tipo_erro=type(exc).__name__,
        )

        typer.echo(
            f"Erro ao transformar ano {ano}: {exc}",
            err=True,
        )
        raise typer.Exit(code=1) from exc


@data_app.command()
def list_years(
    log_level: str = typer.Option(
        "INFO",
        help="Nível de log (DEBUG, INFO, WARNING, ERROR)",
    ),
) -> None:
    """Lista anos disponíveis para ingestão."""
    logger = ModernLogger(level=log_level)

    try:
        from participacao_eleitoral.ingestion.tse_urls import TSEDatasetURLs

        years = TSEDatasetURLs.ANOS_DISPONIVEIS
        typer.echo("Anos disponíveis:")
        for year in years:
            typer.echo(f"  - {year}")
    except Exception as exc:
        logger.error("list_years_failed", erro=str(exc))
        typer.echo(f"Erro ao listar anos: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@validate_app.command()
def schema(
    dataset: str = typer.Argument(..., help="Dataset para validar (comparecimento)"),
    log_level: str = typer.Option("INFO", help="Nível de log"),
) -> None:
    """Valida schema de um dataset."""
    logger = ModernLogger(level=log_level)

    try:
        if dataset == "comparecimento":
            from participacao_eleitoral.ingestion.schemas.comparecimento import (
                SCHEMA_COMPARECIMENTO,
            )

            typer.echo(f"Schema {dataset} válido: {len(SCHEMA_COMPARECIMENTO)} campos")
        else:
            typer.echo(f"Dataset {dataset} não reconhecido", err=True)
            raise typer.Exit(code=1)
    except Exception as exc:
        logger.error("schema_validation_failed", dataset=dataset, erro=str(exc))
        typer.echo(f"Erro na validação: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@utils_app.command()
def version() -> None:
    """Mostra versão da CLI."""
    typer.echo("participacao-eleitoral-cli v1.0.0")


@utils_app.command()
def config_show(
    log_level: str = typer.Option("INFO", help="Nível de log"),
) -> None:
    """Mostra configurações atuais."""
    settings = Settings()

    typer.echo("Configurações atuais:")
    typer.echo(f"  Data directory: {settings.data_dir}")
    typer.echo(f"  Logs directory: {settings.logs_dir}")
    typer.echo(f"  Bronze directory: {settings.bronze_dir}")
    typer.echo(f"  Silver directory: {settings.silver_dir}")
    typer.echo(f"  Gold directory: {settings.gold_dir}")
    typer.echo(f"  TSE base URL: {settings.tse_base_url}")
    typer.echo(f"  Request timeout: {settings.request_timeout}")
    typer.echo(f"  Log level: {settings.log_level}")
    typer.echo("")
