from participacao_eleitoral.ingestion.pipeline import IngestionPipeline


def test_pipeline_fluxo_completo(tmp_path, settings, logger, monkeypatch):
    """
    Pipeline deve executar fluxo completo sem erro.
    """

    # Ajusta bronze_dir para ambiente de teste
    settings.bronze_dir = tmp_path / "bronze"

    pipeline = IngestionPipeline(
        settings=settings,
        logger=logger,
    )

    # Monkeypatch do downloader (não baixar de verdade)
    monkeypatch.setattr(
        pipeline.downloader,
        "download_csv",
        lambda dataset, output_path: type(
            "Result",
            (),
            {
                "csv_path": tmp_path / "fake.csv",
                "tamanho_bytes": 100,
                "checksum_sha256": "abc",
            },
        )(),
    )

    # Cria CSV fake
    (tmp_path / "fake.csv").write_text(
        "ANO_ELEICAO;CD_MUNICIPIO;NM_MUNICIPIO;SG_UF;QT_APTOS;QT_COMPARECIMENTO;QT_ABSTENCOES\n"
        "2022;12345;Recife;PE;1000;800;200\n"
    )

    pipeline.run(2022)

    assert (settings.bronze_dir / "comparecimento_abstencao").exists()
