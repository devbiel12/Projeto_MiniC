import unittest
from ProjetoMiniC.src.lexer.scanner import Scanner
from ProjetoMiniC.src.parser.parser import Parser
from ProjetoMiniC.src.semantic import SemanticAnalyzer


def analyze(source):
    scanner = Scanner(source)
    scanner.scan_tokens()
    if scanner.errors:
        return None, ["LEX"]
    parser = Parser(scanner.tokens)
    program = parser.parse()
    if parser.errors:
        return None, ["SYN"]
    result = SemanticAnalyzer().analyze(program)
    return result, [d.code for d in result.diagnostics]


class SemanticTests(unittest.TestCase):
    def test_valid_program(self):
        result, errors = analyze("int soma(int a, int b) { return a + b; } int main() { int x; x = soma(2, 3); return x; }")
        self.assertTrue(result.success)
        self.assertEqual([], errors)

    def test_undeclared(self):
        _, errors = analyze("int main() { x = 1; return 0; }")
        self.assertIn("SEM001", errors)

    def test_duplicate_same_scope(self):
        _, errors = analyze("int main() { int x; int x; return 0; }")
        self.assertIn("SEM002", errors)

    def test_shadowing(self):
        result, errors = analyze("int x; int main() { int x; { int x; x = 1; } return x; }")
        self.assertTrue(result.success, errors)

    def test_assignment_type(self):
        _, errors = analyze("int main() { int x; x = true; return x; }")
        self.assertIn("SEM003", errors)

    def test_promotion_int_to_float(self):
        result, errors = analyze("float f() { return 2; } int main() { float x; x = 2; return 0; }")
        self.assertTrue(result.success, errors)

    def test_narrowing_rejected(self):
        _, errors = analyze("int main() { int x; x = 2.5; return x; }")
        self.assertIn("SEM003", errors)

    def test_condition_bool(self):
        _, errors = analyze("int main() { if (1) return 0; return 0; }")
        self.assertIn("SEM005", errors)

    def test_vector_index(self):
        result, errors = analyze("int main() { int v[3]; v[1] = 2; return v[1]; }")
        self.assertTrue(result.success, errors)

    def test_vector_index_type(self):
        _, errors = analyze("int main() { int v[3]; v[1.2] = 2; return 0; }")
        self.assertIn("SEM006", errors)

    def test_vector_constant_bounds(self):
        _, errors = analyze("int main() { int v[3]; v[3] = 2; return 0; }")
        self.assertIn("SEM006", errors)

    def test_call_arity(self):
        _, errors = analyze("int f(int x) { return x; } int main() { return f(); }")
        self.assertIn("SEM007", errors)

    def test_call_argument_type(self):
        _, errors = analyze("int f(int x) { return x; } int main() { return f(true); }")
        self.assertIn("SEM008", errors)

    def test_return_type(self):
        _, errors = analyze("int f() { return true; } int main() { return 0; }")
        self.assertIn("SEM009", errors)

    def test_break_outside_loop(self):
        _, errors = analyze("int main() { break; return 0; }")
        self.assertIn("SEM010", errors)

    def test_missing_return(self):
        _, errors = analyze("int f(int x) { if (x > 0) return x; } int main() { return 0; }")
        self.assertIn("SEM011", errors)

    def test_void_as_expression(self):
        _, errors = analyze("void f() { return; } int main() { print(f()); return 0; }")
        self.assertIn("SEM012", errors)

    def test_recursive_function(self):
        result, errors = analyze("int fat(int n) { if (n == 0) return 1; return n * fat(n - 1); } int main() { return fat(4); }")
        self.assertTrue(result.success, errors)

    def test_break_continue_inside_loop(self):
        result, errors = analyze("int main() { int i; while (i < 3) { if (i == 1) continue; break; } return 0; }")
        self.assertTrue(result.success, errors)

    def test_official_integrated_case(self):
        source = "int soma(int a, int b) { return a + b; } int main() { int v[3]; v[0] = soma(1, 2); while (v[0] < 5) { v[0] = v[0] + 1; } return v[0]; }"
        result, errors = analyze(source)
        self.assertTrue(result.success, errors)


if __name__ == "__main__":
    unittest.main()
