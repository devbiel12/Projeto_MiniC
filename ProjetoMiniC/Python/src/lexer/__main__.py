"""
__main__.py
===========

Ponto de entrada do pacote `src.lexer` com interface Tkinter.

Permite executar:
1. os testes já criados do lexer;
2. um código escrito diretamente na interface;
3. um arquivo `.py` de entrada para análise léxica.

Exemplo:
    cd "C:/Users/guilherme.lima/OneDrive - Alpargatas S.A/Documentos/GitHub/Projeto_MiniC/ProjetoMiniC/Python"
    uv run python -m src.lexer
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .demo import TEST_CODE_1, TEST_CODE_2, TEST_CODE_3
from .scanner import Scanner


def scan_source(source: str, title: str = "Análise do lexer") -> str:
    """Executa o scanner sobre o texto e devolve a saída formatada."""
    scanner = Scanner(source)
    scanner.scan_tokens()

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append(title)
    lines.append("=" * 80)
    lines.append("Código-fonte:")
    lines.append(source)
    lines.append("-" * 80)
    lines.append("Tokens reconhecidos:")

    if not scanner.tokens:
        lines.append("Nenhum token foi gerado.")
    else:
        header = f"{'TIPO':<14}{'LEXEMA':<26}{'LINHA':<7}{'COLUNA':<8}{'ATRIBUTO'}"
        lines.append(header)
        lines.append("-" * len(header))
        for token in scanner.tokens:
            nome, lexema, linha, coluna, atributo = token.as_row()
            lexema_repr = repr(lexema)
            if len(lexema_repr) > 24:
                lexema_repr = lexema_repr[:21] + "...'"
            lines.append(f"{nome:<14}{lexema_repr:<26}{linha:<7}{coluna:<8}{atributo}")

    lines.append("-" * 80)
    lines.append("Diagnóstico:")
    if scanner.errors:
        lines.append(f"{len(scanner.errors)} erro(s) léxico(s) encontrado(s):")
        for err in scanner.errors:
            lines.append(f"  [ERRO LÉXICO] {err.diagnostic()}")
    else:
        lines.append("Nenhum erro léxico encontrado.")

    return "\n".join(lines)


def run_builtin_tests() -> str:
    """Retorna a análise combinando todos os testes do arquivo demo.py."""
    source = "\n\n".join((TEST_CODE_1, TEST_CODE_2, TEST_CODE_3))
    return scan_source(source, "Teste 1 + Teste 2 + Teste 3")


class LexerApp(tk.Tk):
    """Interface gráfica para testar o lexer do MiniC."""

    def __init__(self) -> None:
        super().__init__()
        self.title("MiniC - Analisador Léxico")
        self.geometry("1100x760")
        self.minsize(950, 600)
        self.configure(bg="#f2f4f7")
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="Analisador Léxico MiniC", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        toolbar = ttk.Frame(container)
        toolbar.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(toolbar, text="Executar testes criados", command=self.run_tests).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Executar texto digitado", command=self.run_text_input).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Abrir arquivo .py", command=self.run_file_input).pack(side=tk.LEFT)

        self.input_text = scrolledtext.ScrolledText(
            container,
            wrap=tk.WORD,
            height=18,
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.input_text.insert(
            tk.END,
            "int main() {\n"
            "    int x = 10;\n"
            "    if (x > 0 && x != 0) {\n"
            "        print(x);\n"
            "    }\n"
            "    return 0;\n"
            "}\n",
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Resultado:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 4))

        self.output_text = scrolledtext.ScrolledText(
            container,
            wrap=tk.WORD,
            height=18,
            state="disabled",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def _set_output(self, text: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.configure(state="disabled")

    def run_tests(self) -> None:
        self._set_output(run_builtin_tests())

    def run_text_input(self) -> None:
        source = self.input_text.get("1.0", tk.END).strip()
        if not source:
            messagebox.showwarning("Entrada vazia", "Digite algum código MiniC antes de analisar.")
            return
        self._set_output(scan_source(source, "Texto digitado pelo usuário"))

    def run_file_input(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo .py para testar",
            filetypes=[("Python", "*.py"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                source = handle.read()
        except OSError as exc:
            messagebox.showerror("Erro ao abrir arquivo", str(exc))
            return

        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, source)
        self._set_output(scan_source(source, f"Arquivo: {os.path.basename(file_path)}"))


def main() -> None:
    """Executa a interface gráfica do lexer. Se o Tkinter não estiver disponível, cai para execução em modo texto."""
    try:
        app = LexerApp()
        app.mainloop()
    except tk.TclError:
        print("Tkinter não pôde iniciar neste ambiente. Executando em modo texto.")
        print(run_builtin_tests())


if __name__ == "__main__":
    main()
