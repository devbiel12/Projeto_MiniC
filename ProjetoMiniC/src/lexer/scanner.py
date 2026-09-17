"""
scanner.py
==========
Mecanismo principal de análise léxica (Scanner). Converte o código fonte
em uma lista sequencial de tokens e identifica violações sintáticas/léxicas.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

DIRETORIO_ATUAL = Path(__file__).resolve().parent
if str(DIRETORIO_ATUAL) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_ATUAL))

try:
    from .analysis_result import ResultadoAnalise
    from .errors import (
        ErroCaractereNaoTerminado,
        ErroCadeiaNaoTerminada,
        ErroComentarioNaoTerminado,
        ErroIdentificadorInvalido,
        ErroLexico,
        ErroLiteralRealMalformado,
        ErroSimboloInvalido,
    )
    from .jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
    from .token_types import PALAVRAS_RESERVADAS, TokenType
    from .tokens import Token
except (ImportError, ValueError):
    from ProjetoMiniC.src.lexer.analysis_result import ResultadoAnalise
    from ProjetoMiniC.src.lexer.errors import (
        ErroCaractereNaoTerminado,
        ErroCadeiaNaoTerminada,
        ErroComentarioNaoTerminado,
        ErroIdentificadorInvalido,
        ErroLexico,
        ErroLiteralRealMalformado,
        ErroSimboloInvalido,
    )
    from ProjetoMiniC.src.lexer.jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
    from ProjetoMiniC.src.lexer.token_types import PALAVRAS_RESERVADAS, TokenType
    from ProjetoMiniC.src.lexer.tokens import Token


class Scanner:
    """Analisador léxico por autômato finito determinístico de leitura direta."""

    # Mapeamento direto de pontuações de caractere único
    OPERADORES_SIMPLES: Dict[str, TokenType] = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "%": TokenType.PERCENT,
        ".": TokenType.DOT,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        ";": TokenType.SEMI,
        ",": TokenType.COMMA,
    }

    def __init__(self, codigo_fonte: str):
        self.codigo_fonte: str = codigo_fonte
        self.tamanho: int = len(codigo_fonte)
        self.posicao: int = 0
        self.linha: int = 1
        self.coluna: int = 1
        self.tokens: List[Token] = []
        self.erros: List[ErroLexico] = []

    def _esta_no_fim(self) -> bool:
        """Indica se toda a entrada do código-fonte já foi consumida."""
        return self.posicao >= self.tamanho

    def _espiar(self, deslocamento: int = 0) -> str:
        """Retorna o caractere na posição atual (com deslocamento opcional) sem avançar o ponteiro."""
        indice = self.posicao + deslocamento
        return self.codigo_fonte[indice] if indice < self.tamanho else "\0"

    def _avancar(self) -> str:
        """Consome o caractere atual da entrada e atualiza os contadores de linha/coluna."""
        caractere = self.codigo_fonte[self.posicao]
        self.posicao += 1
        if caractere == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return caractere

    def _compara_e_avanca(self, esperado: str) -> bool:
        """Avança o ponteiro apenas se o próximo caractere corresponder ao caractere esperado."""
        if self._espiar() == esperado:
            self._avancar()
            return True
        return False

    def _adicionar_token(self, tipo: TokenType, lexema: str, linha: int, coluna: int,
                           atributo: Optional[Union[int, float, str]] = None) -> None:
        """Instancia e adiciona um token reconhecido na coleção principal."""
        self.tokens.append(Token(tipo, lexema, linha, coluna, atributo))

    def scan_tokens(self) -> List[Token]:
        """Varre iterativamente a fonte até o fim e anexa o token EOF final."""
        while not self._esta_no_fim():
            self._ignorar_espacos_em_branco()
            if self._esta_no_fim():
                break
            self._processar_proximo_token()
        self.tokens.append(Token(TokenType.EOF, "", self.linha, self.coluna, None))
        return self.tokens

    def analisar(self) -> ResultadoAnalise:
        """Executa a análise e compila o relatório formal no objeto ResultadoAnalise."""
        self.scan_tokens()
        return ResultadoAnalise(tokens=self.tokens, erros=self.erros)

    def _ignorar_espacos_em_branco(self) -> None:
        """Ignora sequências de caracteres não-imprimíveis (espaços, tabulações, quebras)."""
        while not self._esta_no_fim() and self._espiar() in " \t\r\n":
            self._avancar()

    def _processar_proximo_token(self) -> None:
        """Ponto central de decisão do autômato (identifica o tipo de elemento a partir do primeiro caractere)."""
        linha_inicial, coluna_inicial = self.linha, self.coluna
        caractere = self._avancar()

        if caractere.isalpha() or caractere == "_":
            self._processar_identificador(linha_inicial, coluna_inicial, caractere)
        elif caractere.isdigit():
            self._processar_numero(linha_inicial, coluna_inicial, caractere)
        elif caractere == '"':
            self._processar_cadeia_caracteres(linha_inicial, coluna_inicial)
        elif caractere == "'":
            self._processar_literal_caractere(linha_inicial, coluna_inicial)
        elif caractere == "/" and self._espiar() == "/":
            self._processar_comentario_linha()
        elif caractere == "/" and self._espiar() == "*":
            self._processar_comentario_bloco(linha_inicial, coluna_inicial)
        else:
            self._processar_operador_ou_erro(caractere, linha_inicial, coluna_inicial)

    def _processar_identificador(self, linha: int, coluna: int, primeiro_caractere: str) -> None:
        """Processa identificadores de variáveis/funções e verifica palavras reservadas."""
        lexema = primeiro_caractere
        while not self._esta_no_fim() and (self._espiar().isalnum() or self._espiar() == "_"):
            lexema += self._avancar()

        token_type = PALAVRAS_RESERVADAS.get(lexema, TokenType.ID)
        atributo = lexema if token_type is TokenType.ID else None
        self._adicionar_token(token_type, lexema, linha, coluna, atributo)

    def _processar_numero(self, linha: int, coluna: int, primeiro_digito: str) -> None:
        """Processa literais numéricos inteiros, decimais (float) e trata erros de formatação."""
        digitos = primeiro_digito
        while not self._esta_no_fim() and self._espiar().isdigit():
            digitos += self._avancar()

        # Erro: Identificador iniciado incorretamente com números (ex: 12var)
        if not self._esta_no_fim() and (self._espiar().isalpha() or self._espiar() == "_"):
            letras = ""
            coluna_letras = self.coluna
            while not self._esta_no_fim() and (self._espiar().isalnum() or self._espiar() == "_"):
                letras += self._avancar()

            self.erros.append(ErroIdentificadorInvalido(digitos + letras, linha, coluna))
            self._adicionar_token(TokenType.NUM_INT, digitos, linha, coluna, int(digitos))
            self._adicionar_token(TokenType.ID, letras, linha, coluna_letras, letras)
            return

        # Análise de ponto flutuante ou erro de ponto flutuante incompleto (ex: 12.)
        if self._espiar() == ".":
            if not self._espiar(1).isdigit():
                coluna_ponto = self.coluna
                self._avancar()
                self.erros.append(ErroLiteralRealMalformado(digitos + ".", linha, coluna))
                self._adicionar_token(TokenType.NUM_INT, digitos, linha, coluna, int(digitos))
                self._adicionar_token(TokenType.DOT, ".", linha, coluna_ponto, None)
                return

            lexema = digitos + self._avancar()
            while not self._esta_no_fim() and self._espiar().isdigit():
                lexema += self._avancar()

            self._adicionar_token(TokenType.NUM_FLOAT, lexema, linha, coluna, float(lexema))
            return

        self._adicionar_token(TokenType.NUM_INT, digitos, linha, coluna, int(digitos))

    def _processar_cadeia_caracteres(self, linha: int, coluna: int) -> None:
        """Processa strings delimitadas por aspas duplas ("...")."""
        posicao_inicial = self.posicao - 1
        conteudo = ""
        fechado = False

        while not self._esta_no_fim():
            if self._espiar() == "\n":
                break
            if self._espiar() == '"':
                self._avancar()
                fechado = True
                break
            conteudo += self._avancar()

        if fechado:
            lexema = f'"{conteudo}"'
            self._adicionar_token(TokenType.STRING, lexema, linha, coluna, conteudo)
        else:
            lexema_erro = self.codigo_fonte[posicao_inicial:self.posicao]
            self.erros.append(ErroCadeiaNaoTerminada(lexema_erro, linha, coluna))

            recuo = 0
            while len(conteudo) > 0 and conteudo[-1] in (")", ";", "}", "]"):
                conteudo = conteudo[:-1]
                recuo += 1

            if recuo > 0:
                self.posicao -= recuo
                self.coluna -= recuo

    def _processar_literal_caractere(self, linha: int, coluna: int) -> None:
        """Processa caracteres individuais entre aspas simples ('c')."""
        if self._esta_no_fim() or self._espiar() == "\n":
            self.erros.append(ErroCaractereNaoTerminado("'", linha, coluna))
            return

        caractere = self._avancar()
        if self._compara_e_avanca("'"):
            self._adicionar_token(TokenType.CHAR_LITERAL, f"'{caractere}'", linha, coluna, caractere)
        else:
            lexema = f"'{caractere}"
            self.erros.append(ErroCaractereNaoTerminado(lexema, linha, coluna))
            if self._espiar() == ";":
                self._avancar()

    def _processar_comentario_linha(self) -> None:
        """Descarta o restante da linha atual ao identificar comentários de linha (//)."""
        self._avancar()
        while not self._esta_no_fim() and self._espiar() != "\n":
            self._avancar()

    def _processar_comentario_bloco(self, linha: int, coluna: int) -> None:
        """Processa comentários de múltiplas linhas (/* ... */)."""
        posicao_inicial = self.posicao - 1
        self._avancar()
        while True:
            if self._esta_no_fim():
                lexema = self.codigo_fonte[posicao_inicial:]
                self.erros.append(ErroComentarioNaoTerminado(linha, coluna, lexema))
                return
            if self._espiar() == "*" and self._espiar(1) == "/":
                self._avancar()
                self._avancar()
                return
            self._avancar()

    def _processar_operador_ou_erro(self, caractere: str, linha: int, coluna: int) -> None:
        """Analisa operadores de um ou dois caracteres e aciona erro para símbolos desconhecidos."""
        if caractere == "=":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.EQ, "==", linha, coluna)
            else:
                self._adicionar_token(TokenType.ASSIGN, "=", linha, coluna)
        elif caractere == "!":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.NEQ, "!=", linha, coluna)
            else:
                self._adicionar_token(TokenType.NOT, "!", linha, coluna)
        elif caractere == "<":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.LE, "<=", linha, coluna)
            else:
                self._adicionar_token(TokenType.LT, "<", linha, coluna)
        elif caractere == ">":
            if self._compara_e_avanca("="):
                self._adicionar_token(TokenType.GE, ">=", linha, coluna)
            else:
                self._adicionar_token(TokenType.GT, ">", linha, coluna)
        elif caractere == "&":
            if self._compara_e_avanca("&"):
                self._adicionar_token(TokenType.AND, "&&", linha, coluna)
            else:
                self._sinalizar_invalido(caractere, linha, coluna)
        elif caractere == "|":
            if self._compara_e_avanca("|"):
                self._adicionar_token(TokenType.OR, "||", linha, coluna)
            else:
                self._sinalizar_invalido(caractere, linha, coluna)
        elif caractere == "/":
            self._adicionar_token(TokenType.SLASH, "/", linha, coluna)
        elif caractere in self.OPERADORES_SIMPLES:
            self._adicionar_token(self.OPERADORES_SIMPLES[caractere], caractere, linha, coluna)
        else:
            self._sinalizar_invalido(caractere, linha, coluna)

    def _sinalizar_invalido(self, caractere: str, linha: int, coluna: int) -> None:
        """Registra a presença de caracteres não reconhecidos."""
        self.erros.append(ErroSimboloInvalido(caractere, linha, coluna))

    def possui_erros(self) -> bool:
        """Informa se foram registrados erros na execução do scanner."""
        return len(self.erros) > 0

    def imprimir_tokens(self) -> None:
        """Exibe a lista dos tokens reconhecidos em formato de tabela no terminal."""
        cabecalho = f"{'TIPO':<14}{'LEXEMA':<26}{'LINHA':<7}{'COLUNA':<8}{'ATRIBUTO'}"
        print(cabecalho)
        print("-" * len(cabecalho))
        for token in self.tokens:
            nome, lexema, linha, coluna, atributo = token.para_linha_tabela()
            lexema_repr = repr(lexema)
            if len(lexema_repr) > 24:
                lexema_repr = lexema_repr[:21] + "...'"
            print(f"{nome:<14}{lexema_repr:<26}{linha:<7}{coluna:<8}{atributo}")

    def imprimir_erros(self) -> None:
        """Imprime os erros identificados de maneira legível."""
        if not self.erros:
            print("Nenhum erro léxico encontrado.")
            return
        print(f"{len(self.erros)} erro(s) léxico(s) encontrado(s):")
        for erro in self.erros:
            print(f"  [ERRO LÉXICO] {erro.diagnostico()}")


def main() -> int:
    """Função de entrada do CLI ao rodar diretamente o módulo scanner.py."""
    caminho_alvo: str | None = None
    modo_apenas_jsonl = False

    for arg in sys.argv[1:]:
        if arg == "--jsonl":
            modo_apenas_jsonl = True
        elif not arg.startswith("--") and caminho_alvo is None:
            caminho_alvo = arg

    if not caminho_alvo:
        print("Uso: python scanner.py <arquivo.c | arquivo.minic> [--jsonl]", file=sys.stderr)
        return 1

    arquivo = Path(caminho_alvo)
    if not arquivo.exists() or not arquivo.is_file():
        print(f"Erro: Arquivo '{caminho_alvo}' não encontrado.", file=sys.stderr)
        return 1

    try:
        conteudo = arquivo.read_text(encoding="utf-8")
    except OSError as err:
        print(f"Erro ao ler arquivo: {err}", file=sys.stderr)
        return 1

    scanner = Scanner(conteudo)
    scanner.scan_tokens()

    saida_tokens_json = serialize_tokens_jsonl(scanner.tokens)
    saida_erros_json = serialize_errors_jsonl(scanner.erros) if scanner.erros else ""

    if modo_apenas_jsonl:
        if saida_tokens_json:
            print(saida_tokens_json)
        if saida_erros_json:
            print(saida_erros_json, file=sys.stderr)
        return 2 if scanner.possui_erros() else 0

    print("=" * 80)
    print(f"Análise Léxica - Arquivo: {arquivo.name}")
    print("=" * 80)
    print("Tokens reconhecidos:")
    scanner.imprimir_tokens()
    print("-" * 80)
    print("Diagnóstico:")
    scanner.imprimir_erros()

    print("-" * 80)
    print("Saída JSONL (Tokens):")
    print(saida_tokens_json if saida_tokens_json else "(vazio)")

    if scanner.erros:
        print("-" * 80)
        print("Saída JSONL (Erros):")
        print(saida_erros_json if saida_erros_json else "(vazio)")

    return 2 if scanner.possui_erros() else 0


if __name__ == "__main__":
    sys.exit(main())