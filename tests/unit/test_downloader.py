import pytest

from participacao_eleitoral.core.entities import Dataset
from participacao_eleitoral.ingestion.downloader import TSEDownloader


def test_downloader_http_mock(monkeypatch, tmp_path, settings, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Testa o downloader sem fazer download real.
    """

    def fake_download(url, dest):  # type: ignore[no-untyped-def]
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


def test_downloader_http_error(monkeypatch, tmp_path, settings, logger) -> None:  # type: ignore[no-untyped-def]
    """
    Testa tratamento de erro HTTP no downloader.
    """

    def fake_download_error(url, dest):  # type: ignore[no-untyped-def]
        raise Exception("HTTP error")

    downloader = TSEDownloader(settings=settings, logger=logger)

    monkeypatch.setattr(
        downloader,
        "_download_http",
        fake_download_error,
    )

    dataset = Dataset(
        nome="comparecimento_abstencao",
        ano=2022,
        url_origem="https://exemplo.com/teste.csv",
    )

    csv_path = tmp_path / "raw.csv"

    with pytest.raises(Exception, match="HTTP error"):
        downloader.download_csv(dataset, csv_path)
