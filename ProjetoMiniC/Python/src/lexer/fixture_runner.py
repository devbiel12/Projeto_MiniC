"""runner de fixtures para o scanner MiniC.

Procura arquivos ``*.expected.jsonl`` e tenta localizar a entrada irmã
com o mesmo nome-base no mesmo diretório. A comparação é feita em JSONL
canônico, com tokens e diagnósticos serializados a partir do scanner.
"""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from typing import Iterable, List, Sequence

from .scanner import Scanner


INPUT_SUFFIXES: Sequence[str] = (".minic", ".mc", ".txt", ".c", ".py", "")


def _serialize_actual(scanner: Scanner) -> List[dict]:
    records: List[dict] = []
    error_index = 0

    for token in scanner.tokens:
        if token.type.name == "ERROR" and error_index < len(scanner.errors):
            error = scanner.errors[error_index]
            error_index += 1
            records.append(
                {
                    "kind": "diagnostic",
                    "code": error.code,
                    "message": error.message,
                    "line": error.line,
                    "column": error.column,
                    "lexeme": error.lexeme,
                }
            )
            continue

        records.append({"kind": "token", **token.as_record()})

    return records


def _normalize_expected(records: Iterable[dict]) -> List[dict]:
    normalized: List[dict] = []
    for record in records:
        if not isinstance(record, dict):
            normalized.append({"kind": "raw", "value": record})
            continue

        if record.get("kind") == "diagnostic" or "code" in record:
            normalized.append(
                {
                    "kind": "diagnostic",
                    "code": record.get("code") or record.get("type") or record.get("name"),
                    "message": record.get("message", ""),
                    "line": record.get("line"),
                    "column": record.get("column"),
                    "lexeme": record.get("lexeme", ""),
                }
            )
        else:
            normalized.append(
                {
                    "kind": record.get("kind", "token"),
                    "type": record.get("type"),
                    "lexeme": record.get("lexeme", ""),
                    "line": record.get("line"),
                    "column": record.get("column"),
                    "attribute": record.get("attribute"),
                }
            )

    return normalized


def _read_jsonl(path: Path) -> List[dict]:
    lines: List[dict] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            lines.append(json.loads(raw_line))
    return lines


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

    actual_records = _serialize_actual(scanner)
    actual_text = _write_jsonl(actual_records)

    expected_records = _normalize_expected(_read_jsonl(expected_file))
    expected_text = _write_jsonl(expected_records)

    if actual_records == expected_records:
        print(f"PASS {expected_file.relative_to(root)}")
        return True

    print(f"FAIL {expected_file.relative_to(root)}")
    print(
        _diff_lines(
            expected_text,
            actual_text,
            expected_file.name,
            f"{input_file.stem}.actual.jsonl",
        )
    )
    return False


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