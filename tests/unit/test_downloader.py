
from participacao_eleitoral.core.entities import Dataset
from participacao_eleitoral.ingestion.downloader import TSEDownloader


def test_downloader_http_mock(monkeypatch, tmp_path, settings, logger):
    """
    Testa o downloader sem fazer download real.
    """

    def fake_download(url, dest):
        dest.write_bytes(b"teste")
        return 5, "checksum_fake"

    downloader = TSEDownloader(settings=settings, logger=logger)

    monkeypatch.setattr(
        downloader,
        "_download_http",
        fake_download,
    )

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://exemplo.com/teste.csv",
    )

    csv_path = tmp_path / "raw.csv"

    result = downloader.download_csv(dataset, csv_path)

    assert result.csv_path.exists()
    assert result.tamanho_bytes == 5
