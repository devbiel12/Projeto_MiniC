"""Runner de fixtures para o scanner MiniC.

Procura arquivos ``*.expected.jsonl`` e tenta localizar a entrada irmã
com o mesmo nome-base no mesmo diretório. A comparação é feita em JSONL
acadêmico, com tokens e diagnósticos serializados a partir do scanner.
"""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from typing import Iterable, List, Sequence

from .jsonl_serializer import serialize_tokens_jsonl
from .scanner import Scanner


INPUT_SUFFIXES: Sequence[str] = (".minic", ".mc", ".c", "")


def _read_jsonl(path: Path) -> List[dict]:
    return [json.loads(raw_line) for raw_line in path.read_text(encoding="utf-8").splitlines() if raw_line.strip()]


def _write_jsonl(records: Iterable[dict]) -> str:
    return "\n".join(json.dumps(record, ensure_ascii=False) for record in records)


def _candidate_inputs(expected_file: Path) -> List[Path]:
    base = expected_file.name.removesuffix(".expected.jsonl")
    candidates: List[Path] = []
    for suffix in INPUT_SUFFIXES:
        candidate = expected_file.with_name(base + suffix)
        if candidate.exists():
            candidates.append(candidate)
    return candidates


def _diff_lines(expected_text: str, actual_text: str, expected_name: str, actual_name: str) -> str:
    diff = list(
        difflib.unified_diff(
            expected_text.splitlines(),
            actual_text.splitlines(),
            fromfile=expected_name,
            tofile=actual_name,
            lineterm="",
        )
    )
    if len(diff) > 40:
        diff = diff[:40] + ["... diff resumido ..."]
    return "\n".join(diff)


def run_fixture(expected_file: Path, input_file: Path, root: Path) -> bool:
    source = input_file.read_text(encoding="utf-8")
    scanner = Scanner(source)
    scanner.scan_tokens()

    actual_text = serialize_tokens_jsonl(scanner.tokens)
    actual_records = _read_jsonl_text(actual_text)

    expected_records = _read_jsonl(expected_file)
    expected_text = _write_jsonl(expected_records)

    if actual_records == expected_records:
        expected_errors_file = _candidate_errors_file(expected_file)
        if expected_errors_file is None:
            print(f"PASS {expected_file.relative_to(root)}")
            return True

        actual_errors_text = _write_jsonl(_read_jsonl_text_errors(scanner.errors))
        expected_errors_records = _read_jsonl(expected_errors_file)
        expected_errors_text = _write_jsonl(expected_errors_records)
        if _read_jsonl_text(actual_errors_text) == expected_errors_records:
            print(f"PASS {expected_file.relative_to(root)}")
            return True

        print(f"FAIL {expected_errors_file.relative_to(root)}")
        print(
            _diff_lines(
                expected_errors_text,
                actual_errors_text,
                expected_errors_file.name,
                f"{input_file.stem}.errors.actual.jsonl",
            )
        )
        return False

    print(f"FAIL {expected_file.relative_to(root)}")
    print(_diff_lines(expected_text, actual_text, expected_file.name, f"{input_file.stem}.actual.jsonl"))

    return False


def _read_jsonl_text(text: str) -> List[dict]:
    return [json.loads(raw_line) for raw_line in text.splitlines() if raw_line.strip()]


def _read_jsonl_text_errors(errors: list) -> List[dict]:
    return [json.loads(raw_line) for raw_line in _write_jsonl(
        {"error": error.code, "lexeme": error.lexeme, "line": error.line, "column": error.column}
        for error in errors
    ).splitlines() if raw_line.strip()]


def _candidate_errors_file(expected_file: Path) -> Path | None:
    candidates = [
        expected_file.with_name(expected_file.name.replace(".expected.jsonl", ".errors.jsonl")),
        expected_file.with_name(expected_file.name.replace(".expected.jsonl", ".expected.errors.jsonl")),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def discover_fixtures(root: Path) -> List[tuple[Path, Path]]:
    fixtures: List[tuple[Path, Path]] = []
    for expected_file in sorted(root.rglob("*.expected.jsonl")):
        candidates = _candidate_inputs(expected_file)
        if candidates:
            fixtures.append((expected_file, candidates[0]))
    return fixtures


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa fixtures do scanner MiniC.")
    parser.add_argument("root", nargs="?", default=".", help="Diretório raiz para busca dos fixtures")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    fixtures = discover_fixtures(root)

    if not fixtures:
        print("Nenhum fixture encontrado.")
        return 1

    passed = 0
    failed = 0
    for expected_file, input_file in fixtures:
        if run_fixture(expected_file, input_file, root):
            passed += 1
        else:
            failed += 1

    print(f"Resumo: PASS={passed} FAIL={failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())