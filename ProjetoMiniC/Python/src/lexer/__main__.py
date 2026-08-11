"""
__main__.py
===========

Permite executar o pacote diretamente com Python.
Exemplo:
    uv run python -m src.lexer

O código abaixo importa a função principal do módulo de demonstração e
executa os testes do lexer quando o pacote é inicializado como módulo.
"""

from .demo import main

if __name__ == "__main__":
    # Ponto de entrada do módulo. Ao rodar 'python -m src.lexer', essa
    # condição ativa a execução da demonstração, que valida o scanner.
    main()
