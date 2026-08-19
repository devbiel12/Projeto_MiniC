"""
demo.py
=======

Módulo de demonstração e teste rápido do analisador léxico MiniC.
Compatível com Python 3.8+.
"""

from .scanner import Scanner

TEST_CODE_1 = """int main() {
    int total = 2 + 3 * 4;
    // mostra o resultado calculado
    print(total);
    return 0;
}"""

TEST_CODE_2 = """int main() {
    int x = 10 @ 5;
    char msg = "texto sem fechamento;
    return 0;
}"""

TEST_CODE_3 = """int main() {
    int a = 1;
    int b = 2;
    if (a < b && b != 0 || !a) {
        print(a);
    }
    /* comentario de bloco sem fechamento
    return 0;
}"""


def executar_caso_teste(titulo: str, codigo_fonte: str) -> Scanner:
    print("\n" + "=" * 78)
    print(titulo)
    print("=" * 78)
    print("Código-fonte:")
    print(codigo_fonte)
    print("-" * 78)

    scanner = Scanner(codigo_fonte)
    scanner.scan_tokens()

    print("Tokens reconhecidos:")
    scanner.print_tokens()

    print("-" * 78)
    print("Diagnóstico:")
    scanner.print_errors()

    return scanner


def main() -> None:
    s1 = executar_caso_teste("Teste 1 - Código válido", TEST_CODE_1)
    s2 = executar_caso_teste("Teste 2 - Símbolo desconhecido e string aberta", TEST_CODE_2)
    s3 = executar_caso_teste("Teste 3 - Operadores e comentário não terminado", TEST_CODE_3)

    print("\n" + "=" * 78)
    print("Resumo dos Testes de Demonstração")
    print("=" * 78)
    for i, s in enumerate((s1, s2, s3), start=1):
        total_tokens = max(0, len(s.tokens) - 1)
        status = "COM ERROS" if s.has_errors() else "OK"
        print(f"Teste {i}: {total_tokens} token(s) | {len(s.errors)} erro(s) léxico(s) | status={status}")


if __name__ == "__main__":
    main()
