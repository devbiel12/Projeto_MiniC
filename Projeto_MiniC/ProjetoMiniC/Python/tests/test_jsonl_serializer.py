from __future__ import annotations

import json
import unittest

from src.lexer.errors import InvalidSymbolError, UnterminatedCommentError
from src.lexer.jsonl_serializer import (
    error_to_academic_record,
    serialize_errors_jsonl,
    serialize_tokens_jsonl,
    token_to_academic_record,
)
from src.lexer.scanner import Scanner


class JsonlSerializerTests(unittest.TestCase):
    def _scan(self, source: str) -> Scanner:
        scanner = Scanner(source)
        scanner.scan_tokens()
        return scanner

    def test_reserved_word_and_identifier_attributes(self) -> None:
        scanner = self._scan("int x;")
        records = [token_to_academic_record(token).to_dict() for token in scanner.tokens]
        self.assertEqual(records[0]["token"], "INT")
        self.assertIsNone(records[0]["attribute"])
        self.assertEqual(records[1]["token"], "IDENT")
        self.assertEqual(records[1]["attribute"], "x")

    def test_numeric_attributes_and_positions(self) -> None:
        scanner = self._scan("123 3.14")
        records = [token_to_academic_record(token).to_dict() for token in scanner.tokens]
        self.assertEqual(records[0]["token"], "INT_LIT")
        self.assertEqual(records[0]["attribute"], 123)
        self.assertEqual(records[0]["line"], 1)
        self.assertEqual(records[0]["column"], 1)
        self.assertEqual(records[1]["token"], "FLOAT_LIT")
        self.assertEqual(records[1]["attribute"], 3.14)

    def test_jsonl_includes_eof(self) -> None:
        scanner = self._scan("x")
        text = serialize_tokens_jsonl(scanner.tokens)
        lines = text.splitlines()
        self.assertEqual(json.loads(lines[-1])["token"], "EOF")
        self.assertEqual(json.loads(lines[-1])["lexeme"], "")

    def test_error_serialization(self) -> None:
        error = InvalidSymbolError("@", 1, 7)
        record = error_to_academic_record(error).to_dict()
        self.assertEqual(record, {"error": "UNKNOWN_SYMBOL", "lexeme": "@", "line": 1, "column": 7})
        self.assertEqual(serialize_errors_jsonl([error]), json.dumps(record, ensure_ascii=False))

    def test_unterminated_comment_error_jsonl(self) -> None:
        error = UnterminatedCommentError(2, 4)
        text = serialize_errors_jsonl([error])
        self.assertEqual(json.loads(text)["error"], "UNTERMINATED_BLOCK_COMMENT")

    def test_token_type_mapping_for_delimiters(self) -> None:
        scanner = self._scan("( ) { } [ ] ; , .")
        names = [token_to_academic_record(token).token for token in scanner.tokens[:-1]]
        self.assertEqual(
            names,
            ["LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET", "SEMICOLON", "COMMA", "DOT"],
        )


if __name__ == "__main__":
    unittest.main()