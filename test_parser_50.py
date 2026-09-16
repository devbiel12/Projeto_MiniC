"""Executa os 50 casos externos de regressao do parser MiniC."""

import argparse
import subprocess
import sys
from pathlib import Path


def read_expected(path):
    return path.read_text(encoding="utf-8").strip()


def run_case(parser_path, case_dir):
    source_path = case_dir / "codigo.c"
    expected_path = case_dir / "ast.esperada.txt"
    result = subprocess.run(
        [sys.executable, str(parser_path), str(source_path)],
        cwd=parser_path.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    number = int(case_dir.name.split("_", 1)[0])
    expected = read_expected(expected_path)

    if number <= 25:
        passed = result.returncode == 0 and result.stdout.strip() == expected
        detail = "AST diferente" if result.returncode == 0 else result.stderr.strip()
    else:
        passed = result.returncode != 0
        detail = "aceitou entrada invalida" if result.returncode == 0 else "rejeitou"

    return passed, detail


def main():
    project_root = Path(__file__).resolve().parent
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument(
        "cases_dir",
        nargs="?",
        type=Path,
        default=None,
        help="pasta casos do pacote testes-parser-50",
    )
    args = argument_parser.parse_args()
    candidates = []
    if args.cases_dir is not None:
        candidates.append(args.cases_dir)
    candidates.extend(
        [
            Path.home() / "Downloads" / "testes-parser-50" / "testes-parser-50" / "casos",
            project_root.parent / "testes-parser-50" / "testes-parser-50" / "casos",
        ]
    )
    cases_dir = next(
        (candidate.resolve() for candidate in candidates if candidate.is_dir()),
        None,
    )

    if cases_dir is None:
        print(
            "ERRO: pasta dos casos não encontrada. Informe o caminho, por exemplo:\n"
            '  python test_parser_50.py "C:\\caminho\\testes-parser-50\\testes-parser-50\\casos"',
            file=sys.stderr,
        )
        return 2

    case_dirs = sorted(
        path for path in cases_dir.iterdir()
        if path.is_dir() and (path / "codigo.c").is_file()
    )

    if len(case_dirs) != 50:
        print(
            "ERRO: esperados 50 casos com codigo.c; encontrados {} em {}".format(
                len(case_dirs), cases_dir
            ),
            file=sys.stderr,
        )
        return 2

    parser_path = project_root / "parser.py"
    passed = 0
    failed = []
    for case_dir in case_dirs:
        ok, detail = run_case(parser_path, case_dir)
        if ok:
            passed += 1
            status = "OK"
        else:
            failed.append((case_dir.name, detail))
            status = "FALHOU"
        print("[{}] {}".format(status, case_dir.name))

    print("\nResumo: {}/{} casos passaram.".format(passed, len(case_dirs)))
    for name, detail in failed:
        print("- {}: {}".format(name, detail))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())