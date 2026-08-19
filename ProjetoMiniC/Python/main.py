"""Launcher gráfico para o projeto MiniC.

Oferece botões para iniciar as várias fases (lexer, parser, IR, etc.).
Atualmente apenas o lexer possui interface; os demais botões exibem um
placeholder informando que a funcionalidade ainda não foi adicionada.
"""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


def _launch_module(module_name: str) -> None:
    """Tenta executar `python -m {module_name}` em um processo separado.

    Se o módulo não fornecer um ponto de entrada, o processo pode terminar
    imediatamente; nesse caso o usuário será informado.
    """
    try:
        proc = subprocess.Popen([sys.executable, "-m", module_name])
    except OSError as exc:
        messagebox.showerror("Erro ao executar módulo", f"Não foi possível iniciar {module_name}: {exc}")
        return

    messagebox.showinfo("Processo iniciado", f"{module_name} iniciado (PID {proc.pid}).")


class LauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Compilador MiniC - Painel")
        self.geometry("1000x560")
        self.configure(bg="#1f1f23")
        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Label(self, text="Compilador de C em Python", fg="white", bg="#1f1f23", font=("Segoe UI", 20, "bold"))
        header.pack(pady=(24, 8))

        subtitle = tk.Label(self, text="Grupo 1 - 6 CCAM", fg="#cfcfff", bg="#1f1f23", font=("Segoe UI", 12))
        subtitle.pack(pady=(0, 18))

        frame = tk.Frame(self, bg="#1f1f23")
        frame.pack(expand=True)

        buttons = [
            ("Analise Léxico", lambda: _launch_module("src.lexer")),
            ("Gerador de IR", lambda: messagebox.showinfo("Em desenvolvimento", "Gerador de IR ainda não implementado.")),
            ("Analise Sintaxe", lambda: messagebox.showinfo("Em desenvolvimento", "Análise de sintaxe ainda não implementada.")),
            ("Analise Semantica", lambda: messagebox.showinfo("Em desenvolvimento", "Análise semântica ainda não implementada.")),
            ("Gerador de Codigo", lambda: messagebox.showinfo("Em desenvolvimento", "Gerador de código ainda não implementado.")),
            ("Otimizador", lambda: messagebox.showinfo("Em desenvolvimento", "Otimizador ainda não implementado.")),
        ]

        # Grid 2x3
        for idx, (label, cmd) in enumerate(buttons):
            r = idx // 3
            c = idx % 3
            btn = tk.Button(
                frame,
                text=label,
                command=cmd,
                bg="#4b6ef6",
                fg="white",
                activebackground="#6f8bff",
                activeforeground="white",
                font=("Segoe UI", 12, "bold"),
                bd=0,
                padx=24,
                pady=14,
            )
            btn.grid(row=r, column=c, padx=40, pady=18, ipadx=10, ipady=6, sticky="nsew")

        # Make columns expand evenly
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)


def main() -> None:
    app = LauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()