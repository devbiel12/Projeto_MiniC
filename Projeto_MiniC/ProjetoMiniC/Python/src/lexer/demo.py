"""
demo.py
=======

Demonstração e testes do pacote `minic_scanner`.

Executar diretamente com:
    python -m minic_scanner

ou:
    python -m minic_scanner.demo

Depende apenas de `scanner.py` (que já carrega tokens/errors/token_types).
"""

from .scanner import Scanner

# --------------------------------------------------------------------------- #
# Casos de teste
# --------------------------------------------------------------------------- #

# Teste 1: código de exemplo válido, extraído do enunciado da disciplina.
# Esse caso serve para verificar se o lexer reconhece corretamente palavras
# reservadas, identificadores, números e operadores básicos.
TEST_CODE_1 = """int main () {
int total = 2 + 3 * 4;
// mostra o resultado
print (total); return 0;}"""

# Teste 2: inclui erros intencionalmente para validar a recuperação do lexer.
# O caractere '@' é inválido para a linguagem e a string não fecha com ".
TEST_CODE_2 = """int main() {
    int x = 10 @ 5;
    char msg = "texto sem fechamento;
    return 0;
}"""

# Teste 3: mistura operadores lógicos (&&, ||, !=, !) com um comentário de
# bloco que não é fechado, para testar a detecção de erros léxicos.
TEST_CODE_3 = """int main() {
    int a = 1;
    int b = 2;
    if (a < b && b != 0 || !a) {
        print(a);
    }
    /* comentario de bloco que nunca fecha
    return 0;
}"""


def run_test(title: str, source: str) -> Scanner:
    """Executa o scanner sobre `source` e imprime tokens + diagnóstico."""
    # Essa função serve como "case de teste": mostra o código, executa a
    # análise léxica e imprime os tokens e os erros encontrados.
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    print("Código-fonte:")
    print(source)
    print("-" * 78)

    scanner = Scanner(source)
    scanner.scan_tokens()

    print("Tokens reconhecidos:")
    scanner.print_tokens()

    print("-" * 78)
    print("Diagnóstico:")
    scanner.print_errors()

    return scanner


def main() -> None:
    """Ponto de entrada da demonstração: roda os 3 testes e imprime o resumo."""
    # O método main orquestra todos os cenários de validação do lexer.
    # Cada execução gera um relatório que mostra tokens reconhecidos e erros.
    s1 = run_test("Teste 1 - Código válido (enunciado)", TEST_CODE_1)
    s2 = run_test("Teste 2 - Erros: símbolo inválido e cadeia não terminada", TEST_CODE_2)
    s3 = run_test("Teste 3 - Operadores lógicos e comentário de bloco não terminado", TEST_CODE_3)

    print("\n" + "=" * 78)
    print("Resumo dos testes")
    print("=" * 78)
    for i, s in enumerate((s1, s2, s3), start=1):
        status = "COM ERROS" if s.has_errors() else "OK"
        print(f"Teste {i}: {len(s.tokens) - 1} token(s) | {len(s.errors)} erro(s) | status={status}")


if __name__ == "__main__":
    main()
