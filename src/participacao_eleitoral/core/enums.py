from enum import Enum


class StatusIngestao(Enum):
    """
    Representa o estado final de uma operação de ingestão.

    Enum é usado (em vez de uma string simples) para:
    - Evitar erros de digitação
    - Permitir validação
    - Padronizar persistência
    """

    SUCESSO = "sucesso"
    FALHA = "falha"
    PARCIAL = "parcial"
