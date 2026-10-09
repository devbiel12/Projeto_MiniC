#!/usr/bin/env python3
"""
minic.py
========
Ponto de entrada do compilador MiniC para testes semânticos automatizados.
Compatível com o script de testes: ./testes_semanticos_py.sh minic.py [diretorio]
"""

import sys
from pathlib import Path

# Configuração do caminho de importação
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ProjetoMiniC.src.lexer.scanner import Scanner
from ProjetoMiniC.src.parser.parser import Parser
from ProjetoMiniC.src.semantic.analyzer import SemanticAnalyzer


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 minic.py <arquivo.c>", file=sys.stderr)
        sys.exit(2)

    caminho = Path(sys.argv[1])
    if not caminho.exists():
        print(f"Erro: arquivo não encontrado: {caminho}", file=sys.stderr)
        sys.exit(2)

    try:
        codigo = caminho.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}", file=sys.stderr)
        sys.exit(2)

    # 1. Análise Léxica
    scanner = Scanner(codigo)
    scanner.scan_tokens()
    if scanner.possui_erros():
        for err in scanner.erros:
            print(f"[ERRO LÉXICO] {err.diagnostico()}", file=sys.stderr)
        sys.exit(1)

    # 2. Análise Sintática
    parser = Parser(scanner.tokens)
    ast = parser.parse()
    if parser.possui_erros():
        for err in parser.erros:
            print(f"[ERRO SINTÁTICO] {err}", file=sys.stderr)
        sys.exit(1)

    # 3. Análise Semântica
    analyzer = SemanticAnalyzer()
    diagnosticos = analyzer.analyze(ast)

    linhas = [d.formatar() for d in diagnosticos]
    if diagnosticos:
        n = len(diagnosticos)
        palavra = "erro" if n == 1 else "erros"
        linhas.append(f"Análise semântica concluída: {n} {palavra}; programa rejeitado.")
    else:
        linhas.append("Análise semântica concluída: 0 erros; programa aceito.")

    # Formatar com \r\n entre linhas para bater com o gabarito no Windows
    # sem quebra de linha final (já que os gabaritos não terminam com newline)
    saida = "\r\n".join(linhas)

    # Escrever na saída padrão em binário UTF-8 garantindo bytes exatos
    sys.stdout.buffer.write(saida.encode("utf-8"))
    sys.stdout.buffer.flush()

    if diagnosticos:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

