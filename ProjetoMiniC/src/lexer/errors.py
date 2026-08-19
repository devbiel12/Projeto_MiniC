"""
errors.py
=========

Hierarquia de erros léxicos e diagnósticos.
Compatível com Python 3.8+.
"""


class LexicalError(Exception):
    code: str = "LEXICAL_ERROR"

    def __init__(self, message: str, line: int, column: int, lexeme: str = ""):
        self.message = message
        self.line = line
        self.column = column
        self.lexeme = lexeme
        self.code = self.__class__.code
        super().__init__(self.diagnostic())

    def diagnostic(self) -> str:
        origem = f" próximo de {self.lexeme!r}" if self.lexeme else ""
        return f"linha {self.line}, coluna {self.column}: {self.message}{origem}"


class InvalidSymbolError(LexicalError):
    code = "UNKNOWN_SYMBOL"

    def __init__(self, char: str, line: int, column: int):
        super().__init__(
            f"símbolo inválido '{char}' (caractere não reconhecido)",
            line,
            column,
            char,
        )


class InvalidIdentifierError(LexicalError):
    code = "INVALID_IDENTIFIER"

    def __init__(self, lexeme: str, line: int, column: int):
        super().__init__(
            "identificador inválido (não pode iniciar com dígitos)",
            line,
            column,
            lexeme,
        )


class MalformedRealLiteralError(LexicalError):
    code = "MALFORMED_REAL_LITERAL"

    def __init__(self, lexeme: str, line: int, column: int):
        super().__init__(
            "literal real malformado (faltou a parte decimal após '.')",
            line,
            column,
            lexeme,
        )


class UnterminatedStringError(LexicalError):
    code = "UNTERMINATED_STRING_LITERAL"

    def __init__(self, partial: str, line: int, column: int):
        super().__init__(
            "cadeia de caracteres não terminada (faltou aspas duplas de fechamento)",
            line,
            column,
            partial,
        )


class UnterminatedCommentError(LexicalError):
    code = "UNTERMINATED_BLOCK_COMMENT"

    def __init__(self, line: int, column: int, lexeme: str = ""):
        super().__init__(
            "comentário de bloco não terminado (faltou '*/')",
            line,
            column,
            lexeme,
        )


class UnterminatedCharError(LexicalError):
    code = "UNTERMINATED_CHAR_LITERAL"

    def __init__(self, partial: str, line: int, column: int):
        super().__init__(
            "literal de caractere malformado (faltou aspas simples ' de fechamento)",
            line,
            column,
            partial,
        )
