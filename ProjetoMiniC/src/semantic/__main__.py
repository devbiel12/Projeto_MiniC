"""Interface gráfica e CLI da análise semântica do MiniC."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from ProjetoMiniC.src.ast.printer import print_tree
from ProjetoMiniC.src.lexer.scanner import Scanner
from ProjetoMiniC.src.parser.parser import Parser
from .semantic import SemanticAnalyzer

EXTENSOES_SUPORTADAS = (
    ("Arquivos MiniC / C", "*.minic;*.mc;*.c;*.txt"),
    ("MiniC (*.minic)", "*.minic"),
    ("C (*.c)", "*.c"),
    ("Todos os arquivos", "*.*"),
)

EXEMPLO = """int soma(int a, int b) {
    return a + b;
}

int main() {
    int resultado = soma(2, 3);
    print(resultado);
    return 0;
}
"""


@dataclass
class ResultadoSemantico:
    codigo_fonte: str
    diagnosticos: list[str]
    arvore: str
    simbolos: str
    codigo_saida: int
    ast_node: object | None = None

    @property
    def sucesso(self) -> bool:
        return self.codigo_saida == 0


def analisar_fonte(fonte: str) -> ResultadoSemantico:
    """Executa léxico + sintático + semântico para alimentar a interface."""
    scanner = Scanner(fonte)
    scanner.scan_tokens()

    if scanner.errors:
        return ResultadoSemantico(
            codigo_fonte=fonte,
            diagnosticos=["[ERRO LÉXICO] " + erro.diagnostic() for erro in scanner.errors],
            arvore="",
            simbolos="",
            codigo_saida=2,
        )

    parser = Parser(scanner.tokens)
    arvore = parser.parse()
    if parser.errors or arvore is None:
        return ResultadoSemantico(
            codigo_fonte=fonte,
            diagnosticos=["[ERRO SINTÁTICO] " + str(erro) for erro in parser.errors],
            arvore="",
            simbolos="",
            codigo_saida=3,
        )

    resultado = SemanticAnalyzer().analyze(arvore)
    diagnosticos = ["[ERRO SEMÂNTICO] " + str(d) for d in resultado.diagnostics]

    simbolos_linhas = ["Tabela de símbolos:"]
    for simbolo in resultado.global_scope.symbols.values():
        simbolos_linhas.append(
            f"  {simbolo.name}: {simbolo.category} {simbolo.type_display()} "
            f"(linha {simbolo.line}, coluna {simbolo.column})"
        )

    if resultado.success:
        diagnosticos.append("Análise semântica concluída: 0 erros; programa aceito.")
        codigo_saida = 0
    else:
        quantidade = len(resultado.diagnostics)
        substantivo = "erro" if quantidade == 1 else "erros"
        diagnosticos.append(
            f"Análise semântica concluída: {quantidade} {substantivo}; programa rejeitado."
        )
        codigo_saida = 4

    return ResultadoSemantico(
        codigo_fonte=fonte,
        diagnosticos=diagnosticos,
        arvore=print_tree(arvore),
        simbolos="\n".join(simbolos_linhas),
        codigo_saida=codigo_saida,
        ast_node=arvore,
    )


class SemanticApp(tk.Tk):
    """Interface gráfica seguindo o mesmo padrão visual/funcional do parser."""

    def __init__(self) -> None:
        super().__init__()
        self.title("MiniC - Analisador Semântico")
        self.geometry("1100x780")
        self.minsize(900, 600)
        self._resultado: ResultadoSemantico | None = None
        self._construir_interface()

    def _construir_interface(self) -> None:
        container = ttk.Frame(self, padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Analisador Semântico MiniC",
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            container,
            text="Digite ou abra um programa para verificar as regras semânticas e a tabela de símbolos.",
        ).pack(anchor="w", pady=(2, 12))

        barra = ttk.Frame(container)
        barra.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(barra, text="Analisar código", command=self.analisar).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra, text="Abrir arquivo", command=self.abrir_arquivo).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra, text="Copiar diagnóstico", command=self.copiar_diagnostico).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(barra, text="Limpar", command=self.limpar).pack(side=tk.LEFT)

        self.status = ttk.Label(barra, text="Pronto para analisar.", foreground="#40536d")
        self.status.pack(side=tk.RIGHT)

        ttk.Label(container, text="Código-fonte", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.campo_fonte = scrolledtext.ScrolledText(
            container, wrap=tk.NONE, height=16, undo=True, font=("Consolas", 10)
        )
        self.campo_fonte.insert("1.0", EXEMPLO)
        self.campo_fonte.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.abas = ttk.Notebook(container)
        self.abas.pack(fill=tk.BOTH, expand=True)

        aba_diagnostico = ttk.Frame(self.abas)
        aba_ast = ttk.Frame(self.abas)
        aba_simbolos = ttk.Frame(self.abas)
        self.abas.add(aba_diagnostico, text="Diagnóstico")
        self.abas.add(aba_ast, text="AST")
        self.abas.add(aba_simbolos, text="Tabela de símbolos")

        self.campo_diagnostico = scrolledtext.ScrolledText(
            aba_diagnostico, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED
        )
        self.campo_diagnostico.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.campo_ast = scrolledtext.ScrolledText(
            aba_ast, wrap=tk.NONE, font=("Consolas", 10), state=tk.DISABLED
        )
        self.campo_ast.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.campo_simbolos = scrolledtext.ScrolledText(
            aba_simbolos, wrap=tk.NONE, font=("Consolas", 10), state=tk.DISABLED
        )
        self.campo_simbolos.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    @staticmethod
    def _mostrar(campo: scrolledtext.ScrolledText, texto: str) -> None:
        campo.configure(state=tk.NORMAL)
        campo.delete("1.0", tk.END)
        campo.insert("1.0", texto)
        campo.configure(state=tk.DISABLED)

    def analisar(self) -> None:
        fonte = self.campo_fonte.get("1.0", tk.END).rstrip("\n")
        if not fonte.strip():
            messagebox.showwarning("Código vazio", "Digite ou abra um programa MiniC antes de analisar.")
            return

        self._resultado = analisar_fonte(fonte)
        self._mostrar(self.campo_diagnostico, "\n".join(self._resultado.diagnosticos))
        self._mostrar(self.campo_ast, self._resultado.arvore or "AST indisponível: corrija os erros léxicos/sintáticos.")
        self._mostrar(self.campo_simbolos, self._resultado.simbolos or "Tabela de símbolos indisponível.")

        if self._resultado.sucesso:
            self.status.configure(text="Programa aceito: sem erros semânticos.", foreground="#18794e")
            self.abas.select(0)
        else:
            self.status.configure(text="Programa rejeitado: verifique o diagnóstico.", foreground="#b42318")
            self.abas.select(0)

    def abrir_arquivo(self) -> None:
        caminho = filedialog.askopenfilename(title="Abrir programa MiniC / C", filetypes=EXTENSOES_SUPORTADAS)
        if not caminho:
            return
        try:
            fonte = Path(caminho).read_text(encoding="utf-8-sig")
        except OSError as erro:
            messagebox.showerror("Erro ao abrir arquivo", str(erro))
            return
        self.campo_fonte.delete("1.0", tk.END)
        self.campo_fonte.insert("1.0", fonte)
        self.title("MiniC - Analisador Semântico - " + os.path.basename(caminho))
        self.analisar()

    def copiar_diagnostico(self) -> None:
        if self._resultado is None:
            messagebox.showwarning("Diagnóstico indisponível", "Execute uma análise antes de copiar o diagnóstico.")
            return
        texto = "\n".join(self._resultado.diagnosticos)
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.update_idletasks()
        messagebox.showinfo("Copiado", "Diagnóstico copiado para a área de transferência.")

    def limpar(self) -> None:
        self.campo_fonte.delete("1.0", tk.END)
        self._mostrar(self.campo_diagnostico, "")
        self._mostrar(self.campo_ast, "")
        self._mostrar(self.campo_simbolos, "")
        self._resultado = None
        self.status.configure(text="Pronto para analisar.", foreground="#40536d")


def executar_cli(argv: list[str]) -> int:
    show_symbols = "--symbols" in argv
    show_ast = "--ast" in argv
    paths = [arg for arg in argv if not arg.startswith("--")]
    if len(paths) != 1:
        print("Uso: python -m ProjetoMiniC.src.semantic <arquivo.minic> [--symbols] [--ast]", file=sys.stderr)
        return 1

    path = Path(paths[0])
    try:
        fonte = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        print(f"Erro ao ler arquivo '{path}': {error}", file=sys.stderr)
        return 1

    resultado = analisar_fonte(fonte)
    if show_ast and resultado.arvore:
        print(resultado.arvore)
    if show_symbols and resultado.simbolos:
        print(resultado.simbolos)
    destino = sys.stdout if resultado.sucesso else sys.stderr
    for diagnostico in resultado.diagnosticos:
        print(diagnostico, file=destino)
    return resultado.codigo_saida


def main() -> int:
    if len(sys.argv) > 1:
        return executar_cli(sys.argv[1:])
    try:
        app = SemanticApp()
        app.mainloop()
        return 0
    except tk.TclError:
        print("Ambiente sem display gráfico (headless).", file=sys.stderr)
        print("Uso: python -m ProjetoMiniC.src.semantic <arquivo.minic>", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
