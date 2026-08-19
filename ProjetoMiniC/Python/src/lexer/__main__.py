"""
__main__.py
===========

Ponto de entrada do pacote `src.lexer` com interface Tkinter.

Permite executar:
1. os testes já criados do lexer;
2. um código escrito diretamente na interface;
3. um arquivo `.minic`, `.mc` ou `.c` de entrada para análise léxica;
4. exportação JSONL acadêmica em arquivo e área de transferência.

Exemplo:
    cd "C:/Users/guilherme.lima/OneDrive - Alpargatas S.A/Documentos/GitHub/Projeto_MiniC/ProjetoMiniC/Python"
    uv run python -m src.lexer
"""

from __future__ import annotations

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .analysis_result import AnalysisResult, AnalysisView
from .demo import TEST_CODE_1, TEST_CODE_2, TEST_CODE_3
from .jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
from .scanner import Scanner


SOURCE_SUFFIXES = (".minic", ".mc", ".c")


def _format_source_output(scanner: Scanner, source: str, title: str = "Análise do lexer") -> str:
    """Executa o scanner sobre o texto e devolve a saída formatada."""

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


def _build_analysis_view(
    source: str,
    title: str = "Análise do lexer",
    source_path: Path | None = None,
) -> AnalysisView:
    """Executa a análise e retorna um objeto pronto para exibição e exportação."""

    scanner = Scanner(source)
    scanner.scan_tokens()
    result = AnalysisResult(tokens=scanner.tokens, errors=scanner.errors)
    return AnalysisView(
        title=title,
        source=source,
        result=result,
        formatted_output=_format_source_output(scanner, source, title),
        tokens_jsonl=serialize_tokens_jsonl(scanner.tokens),
        errors_jsonl=serialize_errors_jsonl(scanner.errors),
        source_path=source_path,
    )


def analyze_source(source: str, title: str = "Análise do lexer") -> tuple[str, Scanner]:
    """Executa a análise e retorna a saída visual junto do scanner."""

    scanner = Scanner(source)
    scanner.scan_tokens()
    return _format_source_output(scanner, source, title), scanner


def scan_source(source: str, title: str = "Análise do lexer") -> str:
    """Executa o scanner sobre o texto e devolve a saída formatada."""

    output, _ = analyze_source(source, title)
    return output


def run_builtin_tests() -> str:
    """Retorna a análise combinando todos os testes do arquivo demo.py."""
    source = "\n\n".join((TEST_CODE_1, TEST_CODE_2, TEST_CODE_3))
    return scan_source(source, "Teste 1 + Teste 2 + Teste 3")


def _collect_source_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        candidate = Path(raw_path)
        if candidate.is_file() and candidate.suffix.lower() in SOURCE_SUFFIXES:
            files.append(candidate)
    return files


def _collect_source_files_from_directory(directory: str) -> list[Path]:
    root = Path(directory)
    if not root.is_dir():
        return []
    return [path for path in sorted(root.rglob("*")) if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES]


class LexerApp(tk.Tk):
    """Interface gráfica para testar o lexer do MiniC."""

    def __init__(self) -> None:
        super().__init__()
        self.title("MiniC - Analisador Léxico")
        self.geometry("1100x760")
        self.minsize(950, 600)
        self.configure(bg="#f2f4f7")
        self._last_source: str = ""
        self._last_input_path: Path | None = None
        self._analysis_views: list[AnalysisView] = []
        self._selected_view_index: int = 0
        self._status_var = tk.StringVar(value="Pronto para analisar MiniC.")
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
        ttk.Button(toolbar, text="Abrir arquivo MiniC", command=self.run_file_input).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Abrir arquivos MiniC", command=self.run_files_input).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Abrir pasta MiniC", command=self.run_folder_input).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Exportar JSONL", command=self.export_jsonl).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Exportar em lote", command=self.export_jsonl_batch).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Copiar JSONL", command=self.copy_jsonl).pack(side=tk.LEFT)

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

        preview_splitter = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        preview_splitter.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        sidebar_frame = ttk.Frame(preview_splitter, padding=(0, 0, 8, 0))
        preview_splitter.add(sidebar_frame, weight=1)

        preview_frame = ttk.Frame(preview_splitter)
        preview_splitter.add(preview_frame, weight=4)

        ttk.Label(sidebar_frame, text="Arquivos analisados:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        sidebar_list_frame = ttk.Frame(sidebar_frame)
        sidebar_list_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        self.view_listbox = tk.Listbox(sidebar_list_frame, activestyle="dotbox", exportselection=False)
        self.view_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.view_listbox.bind("<<ListboxSelect>>", self._on_view_selected)

        sidebar_scrollbar = ttk.Scrollbar(sidebar_list_frame, orient=tk.VERTICAL, command=self.view_listbox.yview)
        sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.view_listbox.configure(yscrollcommand=sidebar_scrollbar.set)

        preview_notebook = ttk.Notebook(preview_frame)
        preview_notebook.pack(fill=tk.BOTH, expand=True)

        output_frame = ttk.Frame(preview_notebook)
        json_frame = ttk.Frame(preview_notebook)
        errors_frame = ttk.Frame(preview_notebook)

        preview_notebook.add(output_frame, text="Saída formatada")
        preview_notebook.add(json_frame, text="JSONL")
        preview_notebook.add(errors_frame, text="JSONL de erros")

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            height=18,
            state="disabled",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.json_text = scrolledtext.ScrolledText(
            json_frame,
            wrap=tk.WORD,
            height=18,
            state="disabled",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.json_text.pack(fill=tk.BOTH, expand=True)

        self.errors_text = scrolledtext.ScrolledText(
            errors_frame,
            wrap=tk.WORD,
            height=18,
            state="disabled",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.errors_text.pack(fill=tk.BOTH, expand=True)

        status_bar = ttk.Label(container, textvariable=self._status_var, anchor="w")
        status_bar.pack(fill=tk.X, pady=(8, 0))

    def _set_output(self, text: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self._status_var.set(text)

    def _set_json_preview(self, jsonl_text: str, errors_jsonl_text: str) -> None:
        self.json_text.configure(state="normal")
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, jsonl_text)
        self.json_text.configure(state="disabled")

        self.errors_text.configure(state="normal")
        self.errors_text.delete("1.0", tk.END)
        self.errors_text.insert(tk.END, errors_jsonl_text or "Nenhum erro léxico encontrado.")
        self.errors_text.configure(state="disabled")

    def _refresh_view_selector(self) -> None:
        labels = [view.title for view in self._analysis_views]
        self.view_listbox.delete(0, tk.END)
        for label in labels:
            self.view_listbox.insert(tk.END, label)
        if labels:
            self.view_listbox.selection_set(self._selected_view_index)
            self.view_listbox.see(self._selected_view_index)

    def _set_analysis_views(self, views: list[AnalysisView]) -> None:
        self._analysis_views = views
        self._selected_view_index = 0
        self._refresh_view_selector()
        if views:
            self._render_selected_view(0)
            errored_views = sum(1 for view in views if view.errors_jsonl)
            self._set_status(f"{len(views)} análise(s) carregada(s) | {errored_views} com erros léxicos.")
        else:
            self._set_output("Nenhuma análise disponível.")
            self._set_json_preview("", "")
            self._set_status("Nenhuma análise carregada.")

    def _render_selected_view(self, index: int) -> None:
        if not self._analysis_views:
            return
        bounded_index = max(0, min(index, len(self._analysis_views) - 1))
        self._selected_view_index = bounded_index
        self.view_listbox.selection_clear(0, tk.END)
        self.view_listbox.selection_set(bounded_index)
        self.view_listbox.see(bounded_index)
        view = self._analysis_views[bounded_index]
        self._set_output(view.formatted_output)
        self._set_json_preview(view.tokens_jsonl, view.errors_jsonl)
        if view.source_path is not None:
            self._last_input_path = view.source_path

    def _on_view_selected(self, _event: tk.Event) -> None:
        selection = self.view_listbox.curselection()
        if not selection:
            return
        self._render_selected_view(selection[0])

    def _update_analysis(self, source: str, title: str, source_path: Path | None = None) -> None:
        self._last_source = source
        self._set_analysis_views([_build_analysis_view(source, title, source_path)])

    def _ensure_view(self) -> AnalysisView | None:
        if not self._analysis_views:
            messagebox.showwarning("Sem análise", "Execute uma análise antes de exportar o JSONL.")
            return None
        return self._analysis_views[self._selected_view_index]

    def run_tests(self) -> None:
        source = "\n\n".join((TEST_CODE_1, TEST_CODE_2, TEST_CODE_3))
        self._last_input_path = None
        self._update_analysis(source, "Teste 1 + Teste 2 + Teste 3")
        self._set_status("Testes embutidos executados com sucesso.")

    def run_text_input(self) -> None:
        source = self.input_text.get("1.0", tk.END).strip()
        if not source:
            messagebox.showwarning("Entrada vazia", "Digite algum código MiniC antes de analisar.")
            return
        self._last_input_path = None
        self._update_analysis(source, "Texto digitado pelo usuário")
        self._set_status("Código digitado analisado.")

    def run_file_input(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo MiniC",
            filetypes=[
                ("MiniC", "*.minic"),
                ("MiniC C", "*.mc"),
                ("C", "*.c"),
                ("Todos os arquivos", "*.*"),
            ],
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
        self._last_input_path = Path(file_path)
        self._update_analysis(source, f"Arquivo: {os.path.basename(file_path)}", Path(file_path))
        self._set_status(f"Arquivo carregado: {Path(file_path).name}")

    def run_files_input(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Selecione arquivos MiniC",
            filetypes=[
                ("MiniC", "*.minic"),
                ("MiniC C", "*.mc"),
                ("C", "*.c"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not file_paths:
            return

        source_files = _collect_source_files(list(file_paths))
        if not source_files:
            messagebox.showwarning("Arquivos inválidos", "Selecione ao menos um arquivo MiniC, .mc ou .c.")
            return

        views: list[AnalysisView] = []
        for file_path in source_files:
            try:
                source = file_path.read_text(encoding="utf-8")
            except OSError as exc:
                messagebox.showerror("Erro ao abrir arquivo", f"{file_path.name}: {exc}")
                continue
            views.append(_build_analysis_view(source, f"Arquivo: {file_path.name}", file_path))

        self._last_input_path = source_files[0] if len(source_files) == 1 else None
        self._set_analysis_views(views)
        self._set_status(f"{len(views)} arquivo(s) carregado(s) para análise.")

    def run_folder_input(self) -> None:
        directory = filedialog.askdirectory(title="Selecione uma pasta com arquivos MiniC")
        if not directory:
            return

        source_files = _collect_source_files_from_directory(directory)
        if not source_files:
            messagebox.showwarning("Pasta vazia", "Nenhum arquivo .minic, .mc ou .c foi encontrado na pasta selecionada.")
            return

        views: list[AnalysisView] = []
        for file_path in source_files:
            try:
                source = file_path.read_text(encoding="utf-8")
            except OSError as exc:
                messagebox.showerror("Erro ao abrir arquivo", f"{file_path.name}: {exc}")
                continue
            views.append(_build_analysis_view(source, f"Arquivo: {file_path.name}", file_path))

        self._last_input_path = None
        self._set_analysis_views(views)
        self._set_status(f"{len(views)} arquivo(s) carregado(s) da pasta selecionada.")

    def export_jsonl(self) -> None:
        view = self._ensure_view()
        if view is None:
            return

        default_name = self._suggested_jsonl_name()
        file_path = filedialog.asksaveasfilename(
            title="Salvar JSONL",
            defaultextension=".jsonl",
            initialfile=default_name,
            filetypes=[("JSONL", "*.jsonl"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(view.tokens_jsonl)
        except OSError as exc:
            messagebox.showerror("Erro ao salvar JSONL", str(exc))
            return

        if view.errors_jsonl:
            errors_path = Path(file_path).with_suffix(".errors.jsonl")
            try:
                with open(errors_path, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(view.errors_jsonl)
            except OSError as exc:
                messagebox.showerror("Erro ao salvar errors.jsonl", str(exc))
                return

        messagebox.showinfo("Exportação concluída", f"JSONL salvo em:\n{file_path}")
        self._set_status(f"JSONL exportado em {Path(file_path).name}.")

    def copy_jsonl(self) -> None:
        view = self._ensure_view()
        if view is None:
            return

        self.clipboard_clear()
        self.clipboard_append(view.tokens_jsonl)
        self.update_idletasks()
        messagebox.showinfo("Copiado", "JSONL acadêmico copiado para a área de transferência.")
        self._set_status("JSONL copiado para a área de transferência.")

    def export_jsonl_batch(self) -> None:
        if not self._analysis_views:
            messagebox.showwarning("Sem análise", "Execute uma análise antes de exportar em lote.")
            return

        if len(self._analysis_views) == 1:
            self.export_jsonl()
            return

        directory = filedialog.askdirectory(title="Selecione uma pasta para salvar os JSONL")
        if not directory:
            return

        output_dir = Path(directory)
        saved_files = 0
        errored_files = 0
        used_names: set[str] = set()

        for view in self._analysis_views:
            stem = self._export_stem_for_view(view, used_names)
            jsonl_path = output_dir / f"{stem}.jsonl"
            try:
                with open(jsonl_path, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(view.tokens_jsonl)
                saved_files += 1
            except OSError as exc:
                messagebox.showerror("Erro ao salvar JSONL", f"{jsonl_path.name}: {exc}")
                return

            if view.errors_jsonl:
                errors_path = output_dir / f"{stem}.errors.jsonl"
                try:
                    with open(errors_path, "w", encoding="utf-8", newline="\n") as handle:
                        handle.write(view.errors_jsonl)
                    errored_files += 1
                except OSError as exc:
                    messagebox.showerror("Erro ao salvar errors.jsonl", f"{errors_path.name}: {exc}")
                    return

        messagebox.showinfo(
            "Exportação em lote concluída",
            f"{saved_files} arquivo(s) JSONL salvo(s) em:\n{directory}\n{errored_files} arquivo(s) também geraram .errors.jsonl.",
        )
        self._set_status(f"Exportação em lote concluída: {saved_files} JSONL e {errored_files} .errors.jsonl.")

    def _export_stem_for_view(self, view: AnalysisView, used_names: set[str]) -> str:
        if view.source_path is not None:
            base_name = view.source_path.stem
        else:
            base_name = self._sanitize_stem(view.title)

        candidate = base_name or "analise"
        suffix = 2
        while candidate in used_names:
            candidate = f"{base_name}_{suffix}"
            suffix += 1
        used_names.add(candidate)
        return candidate

    def _sanitize_stem(self, text: str) -> str:
        cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in text.strip())
        return cleaned.strip("_") or "analise"

    def _suggested_jsonl_name(self) -> str:
        if self._last_input_path is not None:
            return f"{self._last_input_path.stem}.jsonl"
        return "analise.jsonl"


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