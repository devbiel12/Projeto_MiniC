from __future__ import annotations

import unittest

from src.lexer.jsonl_serializer import serialize_errors_jsonl, serialize_tokens_jsonl
from src.lexer.scanner import Scanner


class ScannerTests(unittest.TestCase):
    def test_maximal_munch_operators(self) -> None:
        scanner = Scanner("a==b != c <= d >= e && f || g = h !i")
        tokens = scanner.scan_tokens()
        names = [token.type.name for token in tokens]
        self.assertIn("EQ", names)
        self.assertIn("NEQ", names)
        self.assertIn("LE", names)
        self.assertIn("GE", names)
        self.assertIn("AND", names)
        self.assertIn("OR", names)
        self.assertIn("ASSIGN", names)
        self.assertIn("NOT", names)

    def test_comment_skipping_preserves_next_token_position(self) -> None:
        scanner = Scanner("int x; // comment\nfloat y;")
        tokens = scanner.scan_tokens()
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[3].line, 2)
        self.assertEqual(tokens[3].column, 1)

    def test_error_recovery_keeps_following_tokens(self) -> None:
        scanner = Scanner("int x @ 3; return 0;")
        tokens = scanner.scan_tokens()
        self.assertGreaterEqual(len(scanner.errors), 1)
        self.assertTrue(any(token.lexeme == "return" for token in tokens))
        self.assertTrue(any(token.lexeme == "0" for token in tokens))

    def test_jsonl_round_trip_has_one_record_per_line(self) -> None:
        scanner = Scanner("int main() { return 0; }")
        scanner.scan_tokens()
        token_lines = serialize_tokens_jsonl(scanner.tokens).splitlines()
        self.assertTrue(all(line.strip().startswith("{") for line in token_lines))

    def test_errors_jsonl_only_contains_errors(self) -> None:
        scanner = Scanner("@")
        scanner.scan_tokens()
        errors_text = serialize_errors_jsonl(scanner.errors)
        self.assertTrue(errors_text)
        self.assertNotIn("token", errors_text)


if __name__ == "__main__":
    unittest.main()