"""
__main__.py (parser)
=====================
Ponto de entrada do pacote do Parser. Suporta interface gráfica via
Tkinter (mesmo padrão visual do pacote do Lexer) e execução direta via
CLI no terminal.

Reaproveita o Scanner existente para obter os tokens e passa-os ao
Parser para construir a AST -- nenhuma lógica léxica é duplicada aqui.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk
    _TKINTER_DISPONIVEL = True
except ImportError:
    _TKINTER_DISPONIVEL = False

try:
    from ..lexer.scanner import Scanner
    from ..ast.printer import print_tree, to_sexp
    from .parser import Parser
except (ImportError, ValueError):
    from ProjetoMiniC.src.lexer.scanner import Scanner
    from ProjetoMiniC.src.ast.printer import print_tree, to_sexp
    from ProjetoMiniC.src.parser.parser import Parser

EXTENSOES_SUPORTADAS = (
    ("Arquivos MiniC / C", "*.minic;*.mc;*.c;*.txt"),
    ("MiniC (*.minic)", "*.minic"),
    ("C (*.c)", "*.c"),
    ("Todos os arquivos", "*.*"),
)

# Programa de referência usado nos "testes embutidos" (exemplo oficial da
# especificação MiniC, seção 13.1).
CODIGO_TESTE_PROGRAMA_VALIDO = """int soma(int a, int b) {
    return a + b;
}

int main() {
    int valores[3];
    int i;
    int total = 0;
    for (i = 0; i < 3; i = i + 1) {
        valores[i] = i * 2;
        total = total + valores[i];
    }
    print(soma(total, 1));
    return 0;
}"""

CODIGO_TESTE_EXPRESSOES = """int main() {
    int x = 1 + 2 * 3;
    int y = (1 + 2) * 3;
    bool z = 1 < 2 && 2 != 0 || !x;
    return 0;
}"""

CODIGO_TESTE_ERRO_SINTATICO = """int main() {
    x = ;
    if x > 0) {
        y = 1
    }
    return 0;
}"""


@dataclass
class VisaoParser:
    """Estrutura com o resultado completo de uma análise (léxica + sintática)
    pronta para ser exibida na GUI ou no terminal."""
    titulo: str
    fonte: str
    arvore_ast: str
    sexp_ast: str
    tokens_texto: str
    erros_texto: str
    caminho_fonte: Optional[Path] = None


def analisar_codigo(texto_fonte: str, titulo: str = "Análise Sintática",
                     caminho: Optional[Path] = None) -> VisaoParser:
    """Roda Scanner -> Parser sobre o texto e monta a VisaoParser correspondente."""
    scanner = Scanner(texto_fonte)
    scanner.scan_tokens()

    parser = Parser(scanner.tokens)
    programa = parser.parse()

    linhas_erros: list[str] = []
    if scanner.possui_erros():
        linhas_erros.append(f"{len(scanner.erros)} erro(s) léxico(s):")
        for erro in scanner.erros:
            linhas_erros.append(f"  [LÉXICO] {erro.diagnostico()}")
    if parser.possui_erros():
        linhas_erros.append(f"{len(parser.erros)} erro(s) sintático(s):")
        for erro in parser.erros:
            linhas_erros.append(f"  [SINTÁTICO] {erro.diagnostico()}")
    if not linhas_erros:
        linhas_erros.append("Nenhum erro léxico ou sintático encontrado.")

    linhas_tokens = [
        f"{'TIPO':<14}{'LEXEMA':<26}{'LINHA':<7}{'COLUNA':<8}{'ATRIBUTO'}",
        "-" * 64,
    ]
    for token in scanner.tokens:
        nome, lexema, linha, coluna, atributo = token.para_linha_tabela()
        linhas_tokens.append(f"{nome:<14}{repr(lexema):<26}{linha:<7}{coluna:<8}{atributo}")

    return VisaoParser(
        titulo=titulo,
        fonte=texto_fonte,
        arvore_ast=print_tree(programa),
        sexp_ast=to_sexp(programa),
        tokens_texto="\n".join(linhas_tokens),
        erros_texto="\n".join(linhas_erros),
        caminho_fonte=caminho,
    )


def executar_testes_embutidos() -> VisaoParser:
    """Roda o parser sobre o programa de referência da especificação."""
    return analisar_codigo(CODIGO_TESTE_PROGRAMA_VALIDO, "Testes Embutidos (programa válido)")


# ------------------------------------------------------------------
# Modo terminal (CLI)
# ------------------------------------------------------------------

def executar_modo_terminal(argumentos: list[str]) -> int:
    caminho_arquivo: str | None = None
    formato_sexp = False

    for arg in argumentos:
        if arg == "--sexp":
            formato_sexp = True
        elif not arg.startswith("--") and caminho_arquivo is None:
            caminho_arquivo = arg

    if not caminho_arquivo:
        print("Uso: python -m src.parser <arquivo.minic> [--sexp]", file=sys.stderr)
        return 1

    caminho = Path(caminho_arquivo)
    if not caminho.exists() or not caminho.is_file():
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.", file=sys.stderr)
        return 1

    try:
        conteudo = caminho.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Erro ao ler arquivo '{caminho_arquivo}': {exc}", file=sys.stderr)
        return 1

    visao = analisar_codigo(conteudo, f"Arquivo: {caminho.name}", caminho)

    print("=" * 80)
    print(visao.titulo)
    print("=" * 80)
    print("Diagnóstico:")
    print(visao.erros_texto)
    print("-" * 80)
    print("AST:")
    print(visao.sexp_ast if formato_sexp else visao.arvore_ast)

    return 0 if "Nenhum erro" in visao.erros_texto else 3


# ------------------------------------------------------------------
# Interface gráfica (Tkinter) -- mesmo padrão visual do AplicacaoLexer
# ------------------------------------------------------------------

class _AplicacaoParserBase(tk.Tk if _TKINTER_DISPONIVEL else object):
    """Classe-base condicional: evita erro de importação em ambientes sem Tkinter."""
    pass


class AplicacaoParser(_AplicacaoParserBase):
    """Interface gráfica interativa do analisador sintático (Parser + AST)."""

    def __init__(self) -> None:
        if not _TKINTER_DISPONIVEL:
            raise RuntimeError("Tkinter indisponível neste ambiente.")
        super().__init__()
        self.title("MiniC - Analisador Sintático (Parser + AST)")
        self.geometry("1100x780")
        self.minsize(950, 600)
        self.configure(bg="#f2f4f7")
        self._visao_atual: Optional[VisaoParser] = None
        self._construir_interface()

    def _construir_interface(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(container, text="Analisador Sintático MiniC (Parser + AST)",
                            font=("Segoe UI", 16, "bold"))
        titulo.pack(anchor="w", pady=(0, 10))

        barra_botoes = ttk.Frame(container)
        barra_botoes.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(barra_botoes, text="Executar testes embutidos",
                   command=self.executar_testes).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Analisar código digitado",
                   command=self.executar_texto_digitado).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Abrir arquivo MiniC / C",
                   command=self.abrir_arquivo).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Copiar AST (parentetizada)",
                   command=self.copiar_sexp).pack(side=tk.LEFT)

        self.campo_texto = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, height=12, font=("Consolas", 10), padx=8, pady=8,
        )
        self.campo_texto.insert(tk.END, CODIGO_TESTE_EXPRESSOES)
        self.campo_texto.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        self.abas = ttk.Notebook(container)
        self.abas.pack(fill=tk.BOTH, expand=True)

        aba_arvore = ttk.Frame(self.abas)
        aba_sexp = ttk.Frame(self.abas)
        aba_tokens = ttk.Frame(self.abas)
        aba_erros = ttk.Frame(self.abas)

        self.abas.add(aba_arvore, text="AST em Árvore")
        self.abas.add(aba_sexp, text="AST Parentetizada")
        self.abas.add(aba_tokens, text="Tokens")
        self.abas.add(aba_erros, text="Diagnóstico")

        self.txt_arvore = scrolledtext.ScrolledText(aba_arvore, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_arvore.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.txt_sexp = scrolledtext.ScrolledText(aba_sexp, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_sexp.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.txt_tokens = scrolledtext.ScrolledText(aba_tokens, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_tokens.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.txt_erros = scrolledtext.ScrolledText(aba_erros, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_erros.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _renderizar_visao(self, visao: VisaoParser) -> None:
        self._visao_atual = visao
        for campo, conteudo in (
            (self.txt_arvore, visao.arvore_ast),
            (self.txt_sexp, visao.sexp_ast),
            (self.txt_tokens, visao.tokens_texto),
            (self.txt_erros, visao.erros_texto),
        ):
            campo.configure(state="normal")
            campo.delete("1.0", tk.END)
            campo.insert(tk.END, conteudo)
            campo.configure(state="disabled")

    def executar_testes(self) -> None:
        self._renderizar_visao(executar_testes_embutidos())

    def executar_texto_digitado(self) -> None:
        fonte = self.campo_texto.get("1.0", tk.END).strip()
        if not fonte:
            messagebox.showwarning("Entrada vazia", "Digite algum código MiniC antes de analisar.")
            return
        self._renderizar_visao(analisar_codigo(fonte, "Texto Digitado"))

    def abrir_arquivo(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo MiniC ou C", filetypes=EXTENSOES_SUPORTADAS,
        )
        if not caminho:
            return
        try:
            with open(caminho, "r", encoding="utf-8") as arq:
                fonte = arq.read()
        except OSError as exc:
            messagebox.showerror("Erro ao abrir arquivo", str(exc))
            return

        self.campo_texto.delete("1.0", tk.END)
        self.campo_texto.insert(tk.END, fonte)
        self._renderizar_visao(analisar_codigo(fonte, f"Arquivo: {os.path.basename(caminho)}", Path(caminho)))

    def copiar_sexp(self) -> None:
        if not self._visao_atual:
            messagebox.showwarning("Aviso", "Execute uma análise antes de copiar a AST.")
            return
        self.clipboard_clear()
        self.clipboard_append(self._visao_atual.sexp_ast)
        self.update_idletasks()
        messagebox.showinfo("Copiado", "AST (forma parentetizada) copiada para a área de transferência.")


def main() -> int:
    if len(sys.argv) > 1:
        return executar_modo_terminal(sys.argv[1:])

    if not _TKINTER_DISPONIVEL:
        print("Tkinter indisponível neste ambiente. Executando modo texto demonstrativo.")
        visao = executar_testes_embutidos()
        print(visao.erros_texto)
        print(visao.arvore_ast)
        return 0

    try:
        app = AplicacaoParser()
        app.mainloop()
        return 0
    except tk.TclError:
        print("Ambiente sem display gráfico (headless). Executando modo texto demonstrativo.")
        visao = executar_testes_embutidos()
        print(visao.erros_texto)
        print(visao.arvore_ast)
        return 0


if __name__ == "__main__":
    sys.exit(main())
