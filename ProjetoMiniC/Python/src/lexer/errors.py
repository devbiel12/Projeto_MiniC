"""
errors.py
=========

Hierarquia de exceções léxicas usadas pelo `Scanner` para reportar e
diagnosticar problemas no código-fonte:

    LexicalError                (base)
        InvalidSymbolError       -> símbolo fora do alfabeto da linguagem
        UnterminatedStringError  -> cadeia "..." sem fechamento
        UnterminatedCommentError -> comentário /* ... sem '*/'
        UnterminatedCharError    -> literal '...' mal formado

Este módulo não depende de nenhum outro módulo do pacote.
"""


# ------------------------------------------------------------------
# A hierarquia de erros abaixo centraliza os diagnósticos léxicos do
# projeto. Cada classe representa um tipo específico de problema no código
# fonte, como símbolo inválido, string não fechada ou comentário mal
# encerrado. Isso permite reportar erros de forma clara e consistente.
# ------------------------------------------------------------------
class LexicalError(Exception):
    """Erro léxico genérico, com posição e mensagem de diagnóstico."""

    def __init__(self, message: str, line: int, column: int, lexeme: str = ""):
        # Guarda os dados do erro para facilitar a exibição e a depuração.
        self.message = message
        self.line = line
        self.column = column
        self.lexeme = lexeme
        super().__init__(self.diagnostic())

    def diagnostic(self) -> str:
        """Mensagem que permite localizar e corrigir o erro."""
        origem = f" próximo de {self.lexeme!r}" if self.lexeme else ""
        return f"linha {self.line}, coluna {self.column}: {self.message}{origem}"


class InvalidSymbolError(LexicalError):
    """Disparado quando um caractere não pertence ao alfabeto da linguagem."""

    def __init__(self, char: str, line: int, column: int):
        # Exemplo: uso de '@' ou outro caractere que o lexer não conhece.
        super().__init__(
            f"símbolo inválido '{char}' (caractere não reconhecido pela linguagem)",
            line, column, char,
        )


class UnterminatedStringError(LexicalError):
    """Disparado quando uma cadeia de caracteres não é fechada com '\"'."""

    def __init__(self, partial: str, line: int, column: int):
        super().__init__(
            "cadeia de caracteres não terminada (faltando '\"' de fechamento)",
            line, column, partial,
        )


class UnterminatedCommentError(LexicalError):
    """Disparado quando um comentário de bloco /* ... não é fechado com */."""

    def __init__(self, line: int, column: int):
        super().__init__(
            "comentário de bloco não terminado (faltando '*/')",
            line, column,
        )


class UnterminatedCharError(LexicalError):
    """Disparado quando um literal de caractere '...' não é fechado corretamente."""

    def __init__(self, partial: str, line: int, column: int):
        super().__init__(
            "literal de caractere mal formado (esperado ' de fechamento)",
            line, column, partial,
        )
