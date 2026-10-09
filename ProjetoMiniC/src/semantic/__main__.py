"""
__main__.py (semantic)
======================
Ponto de entrada do pacote do Analisador Semântico.
Suporta interface gráfica via Tkinter (mesmo padrão visual dos pacotes Lexer e Parser)
e execução direta via CLI no terminal.
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
    from ..parser.parser import Parser
    from ..ast.printer import print_tree
    from .analyzer import SemanticAnalyzer, Diagnostic
except (ImportError, ValueError):
    from ProjetoMiniC.src.lexer.scanner import Scanner
    from ProjetoMiniC.src.parser.parser import Parser
    from ProjetoMiniC.src.ast.printer import print_tree
    from ProjetoMiniC.src.semantic.analyzer import SemanticAnalyzer, Diagnostic

EXTENSOES_SUPORTADAS = (
    ("Arquivos MiniC / C", "*.minic;*.mc;*.c;*.txt"),
    ("MiniC (*.minic)", "*.minic"),
    ("C (*.c)", "*.c"),
    ("Todos os arquivos", "*.*"),
)

CODIGO_TESTE_SEMANTICO_VALIDO = """float soma(float a, float b) {
    return a + b;
}

int principal() {
    int n;
    float r;
    n = 3;
    r = soma(n, 2);
    return n;
}"""

CODIGO_TESTE_SEMANTICO_ERROS = """int combina(int a, float b) {
    return a;
}

int principal() {
    int n;
    n = 2.5;
    n = ausente + 1;
    combina(1 < 2, 3 < 4);
    return 0;
}"""


@dataclass
class VisaoSemantica:
    titulo: str
    fonte: str
    relatorio_semantico: str
    diagnosticos: list[Diagnostic]
    arvore_ast: str
    tokens_texto: str
    caminho_fonte: Optional[Path] = None


def analisar_semantica(texto_fonte: str, titulo: str = "Análise Semântica",
                       caminho: Optional[Path] = None) -> VisaoSemantica:
    scanner = Scanner(texto_fonte)
    scanner.scan_tokens()

    parser = Parser(scanner.tokens)
    programa = parser.parse()

    linhas_relatorio: list[str] = []
    diagnosticos: list[Diagnostic] = []

    if scanner.possui_erros():
        linhas_relatorio.append(f"{len(scanner.erros)} erro(s) léxico(s):")
        for erro in scanner.erros:
            linhas_relatorio.append(f"  [LÉXICO] {erro.diagnostico()}")

    if parser.possui_erros():
        linhas_relatorio.append(f"{len(parser.erros)} erro(s) sintático(s):")
        for erro in parser.erros:
            linhas_relatorio.append(f"  [SINTÁTICO] {erro.diagnostico()}")

    if not scanner.possui_erros() and not parser.possui_erros():
        analyzer = SemanticAnalyzer()
        diagnosticos = analyzer.analyze(programa)
        for d in diagnosticos:
            linhas_relatorio.append(d.formatar())
        if diagnosticos:
            n = len(diagnosticos)
            palavra = "erro" if n == 1 else "erros"
            linhas_relatorio.append(f"\nAnálise semântica concluída: {n} {palavra}; programa rejeitado.")
        else:
            linhas_relatorio.append("Análise semântica concluída: 0 erros; programa aceito.")
    else:
        linhas_relatorio.append("\nAnálise semântica cancelada devido a erros léxicos/sintáticos.")

    linhas_tokens = [
        f"{'TIPO':<14}{'LEXEMA':<26}{'LINHA':<7}{'COLUNA':<8}{'ATRIBUTO'}",
        "-" * 64,
    ]
    for token in scanner.tokens:
        nome, lexema, linha, coluna, atributo = token.para_linha_tabela()
        linhas_tokens.append(f"{nome:<14}{repr(lexema):<26}{linha:<7}{coluna:<8}{atributo}")

    return VisaoSemantica(
        titulo=titulo,
        fonte=texto_fonte,
        relatorio_semantico="\n".join(linhas_relatorio),
        diagnosticos=diagnosticos,
        arvore_ast=print_tree(programa),
        tokens_texto="\n".join(linhas_tokens),
        caminho_fonte=caminho,
    )


class _AplicacaoSemanticaBase(tk.Tk if _TKINTER_DISPONIVEL else object):
    pass


class AplicacaoSemantica(_AplicacaoSemanticaBase):
    """Interface gráfica interativa do analisador semântico (Aula 15)."""

    def __init__(self) -> None:
        if not _TKINTER_DISPONIVEL:
            raise RuntimeError("Tkinter indisponível neste ambiente.")
        super().__init__()
        self.title("MiniC - Analisador Semântico (Tipos, Escopo & Regras)")
        self.geometry("1100x780")
        self.minsize(950, 600)
        self.configure(bg="#f2f4f7")
        self._visao_atual: Optional[VisaoSemantica] = None
        self._construir_interface()

    def _construir_interface(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(container, text="Analisador Semântico MiniC (Aula 15)",
                            font=("Segoe UI", 16, "bold"))
        titulo.pack(anchor="w", pady=(0, 10))

        barra_botoes = ttk.Frame(container)
        barra_botoes.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(barra_botoes, text="Exemplo Válido",
                   command=self.exemplo_valido).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Exemplo com Erros",
                   command=self.exemplo_erros).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Analisar Código Digitado",
                   command=self.executar_texto_digitado).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Abrir Arquivo MiniC / C",
                   command=self.abrir_arquivo).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra_botoes, text="Limpar",
                   command=self.limpar).pack(side=tk.LEFT)

        self.campo_texto = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, height=12, font=("Consolas", 10), padx=8, pady=8,
        )
        self.campo_texto.insert(tk.END, CODIGO_TESTE_SEMANTICO_VALIDO)
        self.campo_texto.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        self.abas = ttk.Notebook(container)
        self.abas.pack(fill=tk.BOTH, expand=True)

        aba_semantica = ttk.Frame(self.abas)
        aba_arvore = ttk.Frame(self.abas)
        aba_tokens = ttk.Frame(self.abas)

        self.abas.add(aba_semantica, text="Diagnóstico Semântico")
        self.abas.add(aba_arvore, text="AST Anotada")
        self.abas.add(aba_tokens, text="Tokens")

        self.txt_semantica = scrolledtext.ScrolledText(aba_semantica, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_semantica.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.txt_arvore = scrolledtext.ScrolledText(aba_arvore, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_arvore.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.txt_tokens = scrolledtext.ScrolledText(aba_tokens, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.txt_tokens.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _renderizar_visao(self, visao: VisaoSemantica) -> None:
        self._visao_atual = visao
        for campo, conteudo in (
            (self.txt_semantica, visao.relatorio_semantico),
            (self.txt_arvore, visao.arvore_ast),
            (self.txt_tokens, visao.tokens_texto),
        ):
            campo.configure(state="normal")
            campo.delete("1.0", tk.END)
            campo.insert(tk.END, conteudo)
            campo.configure(state="disabled")

    def exemplo_valido(self) -> None:
        self.campo_texto.delete("1.0", tk.END)
        self.campo_texto.insert(tk.END, CODIGO_TESTE_SEMANTICO_VALIDO)
        self._renderizar_visao(analisar_semantica(CODIGO_TESTE_SEMANTICO_VALIDO, "Exemplo Válido"))

    def exemplo_erros(self) -> None:
        self.campo_texto.delete("1.0", tk.END)
        self.campo_texto.insert(tk.END, CODIGO_TESTE_SEMANTICO_ERROS)
        self._renderizar_visao(analisar_semantica(CODIGO_TESTE_SEMANTICO_ERROS, "Exemplo com Erros Semânticos"))

    def executar_texto_digitado(self) -> None:
        fonte = self.campo_texto.get("1.0", tk.END).strip()
        if not fonte:
            messagebox.showwarning("Entrada vazia", "Digite algum código MiniC antes de analisar.")
            return
        self._renderizar_visao(analisar_semantica(fonte, "Texto Digitado"))

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
        self._renderizar_visao(analisar_semantica(fonte, f"Arquivo: {os.path.basename(caminho)}", Path(caminho)))

    def limpar(self) -> None:
        self.campo_texto.delete("1.0", tk.END)
        for campo in (self.txt_semantica, self.txt_arvore, self.txt_tokens):
            campo.configure(state="normal")
            campo.delete("1.0", tk.END)
            campo.configure(state="disabled")


def main() -> int:
    if len(sys.argv) > 1:
        caminho = Path(sys.argv[1])
        if not caminho.exists():
            print(f"Erro: Arquivo '{caminho}' não encontrado.", file=sys.stderr)
            return 1
        conteudo = caminho.read_text(encoding="utf-8")
        visao = analisar_semantica(conteudo, f"Arquivo: {caminho.name}", caminho)
        print("=" * 80)
        print(visao.titulo)
        print("=" * 80)
        print(visao.relatorio_semantico)
        return 1 if visao.diagnosticos else 0

    if not _TKINTER_DISPONIVEL:
        print("Tkinter indisponível neste ambiente.")
        return 1

    try:
        app = AplicacaoSemantica()
        app.mainloop()
        return 0
    except tk.TclError:
        print("Ambiente sem display gráfico.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

