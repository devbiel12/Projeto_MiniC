"""
fixture_runner.py
=================

Validador automático de fixtures para testes acadêmicos.
Compatível com Python 3.8+.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import List, Sequence

DIRETORIO_ATUAL = Path(__file__).resolve().parent.parent.parent
if str(DIRETORIO_ATUAL) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_ATUAL))

from ProjetoMiniC.src.lexer.jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
from ProjetoMiniC.src.lexer.scanner import Scanner

INPUT_SUFFIXES: Sequence[str] = (".minic", ".mc", ".c", "")


def _remover_sufixo(texto: str, sufixo: str) -> str:
    if texto.endswith(sufixo):
        return texto[:-len(sufixo)]
    return texto


def _read_jsonl(path: Path) -> List[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _candidate_inputs(expected_file: Path) -> List[Path]:
    base = _remover_sufixo(expected_file.name, ".expected.jsonl")
    candidates: List[Path] = []
    for suffix in INPUT_SUFFIXES:
        candidate = expected_file.with_name(base + suffix)
        if candidate.exists():
            candidates.append(candidate)
    return candidates


def run_fixture(expected_file: Path, input_file: Path, root: Path) -> bool:
    source = input_file.read_text(encoding="utf-8")
    scanner = Scanner(source)
    scanner.scan_tokens()

    actual_tokens_text = serialize_tokens_jsonl(scanner.tokens)
    actual_records = [json.loads(line) for line in actual_tokens_text.splitlines() if line.strip()]
    expected_records = _read_jsonl(expected_file)

    if actual_records != expected_records:
        print(f"FAIL {expected_file.relative_to(root)} (Tokens divergentes)")
        return False

    errors_file = expected_file.with_name(expected_file.name.replace(".expected.jsonl", ".errors.jsonl"))
    if errors_file.exists():
        actual_errors_text = serialize_errors_jsonl(scanner.errors)
        actual_error_records = [json.loads(line) for line in actual_errors_text.splitlines() if line.strip()]
        expected_error_records = _read_jsonl(errors_file)

        if actual_error_records != expected_error_records:
            print(f"FAIL {errors_file.relative_to(root)} (Erros divergentes)")
            return False

    print(f"PASS {expected_file.relative_to(root)}")
    return True


def discover_fixtures(root: Path) -> List[tuple[Path, Path]]:
    fixtures: List[tuple[Path, Path]] = []
    for expected_file in sorted(root.rglob("*.expected.jsonl")):
        candidates = _candidate_inputs(expected_file)
        if candidates:
            fixtures.append((expected_file, candidates[0]))
    return fixtures


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa fixtures do scanner MiniC.")
    parser.add_argument("root", nargs="?", default=".", help="Diretório raiz para busca")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    fixtures = discover_fixtures(root)

    if not fixtures:
        print("Nenhum fixture encontrado.")
        return 1

    passed = 0
    failed = 0
    for exp, inp in fixtures:
        if run_fixture(exp, inp, root):
            passed += 1
        else:
            failed += 1

    print(f"\nResumo: PASS={passed} FAIL={failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
