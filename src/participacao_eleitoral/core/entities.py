from dataclasses import dataclass
from typing import ClassVar

from .contracts.comparecimento import ComparecimentoContrato
from .contracts.comparecimento_silver import ComparecimentoSilverContrato


@dataclass(frozen=True)
class Dataset:
    """
    Representa um dataset lógico do domínio.

    NÃO sabe:
    - onde será salvo
    - como será baixado
    - em que formato

    Sabe apenas:
    - identidade
    - regras de validade
    """

    nome: str
    ano: int
    url_origem: str

    # Tipos de datasets conhecidos no domínio
    TIPOS_CONHECIDOS: ClassVar[set[str]] = {
        ComparecimentoContrato.DATASET_NAME,
        ComparecimentoSilverContrato.DATASET_NAME,
    }

    def __post_init__(self) -> None:
        # Validações de nome
        if not self.nome or not isinstance(self.nome, str):
            raise ValueError("Nome deve ser string não vazia")

        if self.nome not in self.TIPOS_CONHECIDOS:
            raise ValueError(
                f"Dataset desconhecido: {self.nome}. Tipos válidos: {self.TIPOS_CONHECIDOS}"
            )

        # Regra de negócio: anos válidos
        if not isinstance(self.ano, int) or not (2000 <= self.ano <= 2030):
            raise ValueError(f"Ano inválido: {self.ano}. Deve estar entre 2000 e 2030")

        # Regra de negócio: datasets devem ser públicos (HTTP) ou paths locais
        if not isinstance(self.url_origem, str):
            raise ValueError("URL deve ser string")

        # Validação de formato da URL/path
        if not self.url_origem.strip():
            raise ValueError("URL não pode ser vazia")

        # Para Bronze: HTTP/HTTPS (datasets externos)
        # Para Silver: path local (transformação de dados já baixados)
        is_http = self.url_origem.startswith(("http://", "https://"))
        # Path Windows: C:\ ou Unix: /
        is_windows_path = len(self.url_origem) > 1 and self.url_origem[1] == ":"
        is_unix_path = self.url_origem.startswith("/")
        is_local = is_windows_path or is_unix_path

        if not (is_http or is_local):
            raise ValueError(
                f"URL/Path inválido: {self.url_origem}. Deve começar com http://, https:// ou ser um caminho local"
            )

    @property
    def identificador_unico(self) -> str:
        """Retorna identificador único do dataset."""
        return f"{self.nome}:{self.ano}"

    @property
    def eh_comparecimento(self) -> bool:
        """Verifica se é dataset de comparecimento."""
        return self.nome == ComparecimentoContrato.DATASET_NAME

    def obter_contrato(self) -> type[ComparecimentoContrato]:
        """Retorna o contrato correspondente ao dataset."""
        if self.eh_comparecimento:
            return ComparecimentoContrato
        raise ValueError(f"Contrato não encontrado para dataset: {self.nome}")
