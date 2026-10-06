# Comandos do projeto

CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -pedantic -O2
SRC = C/main.c C/scanner.c C/token.c C/token_types.c C/errors.c C/util.c
OBJ = $(SRC:.c=.o)
TARGET = C/minic_scanner
PARSER_SRC = C/parser_main.c C/parser.c C/ast.c C/scanner.c C/token.c C/token_types.c C/errors.c C/util.c
PARSER_TARGET = parser
SEMANTIC_SRC = C/semantic_main.c C/semantic.c C/parser.c C/ast.c C/scanner.c C/token.c C/token_types.c C/errors.c C/util.c
SEMANTIC_TARGET = semantic

# Compatibilidade para comando de remoção no Windows e Linux
ifeq ($(OS),Windows_NT)
    RM = del /Q /F
    EXT = .exe
else
    RM = rm -f
    EXT =
endif

TARGET_BIN = $(TARGET)$(EXT)

all: $(TARGET_BIN) parser semantic

parser: $(PARSER_SRC)
	$(CC) $(CFLAGS) -o $(PARSER_TARGET) $(PARSER_SRC)

semantic: $(SEMANTIC_SRC)
	$(CC) $(CFLAGS) -o $(SEMANTIC_TARGET) $(SEMANTIC_SRC)

$(TARGET_BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Executa o scanner sobre todos os programas válidos de teste
test-valid: $(TARGET_BIN)
	@echo "=== Rodando Testes Validos (Programas C) ==="
	@for file in ProjetoMiniC/casos-programas-c/*.c; do \
		echo "Analisando $$file..."; \
		./$(TARGET_BIN) --jsonl "$$file" > "$$file.c.out.jsonl" 2>/dev/null; \
	done

# Executa o scanner sobre os casos invalidos
test-invalid: $(TARGET_BIN)
	@echo "=== Rodando Testes Invalidos ==="
	@for file in ProjetoMiniC/casos-invalidos/*.minic; do \
		echo "Analisando $$file..."; \
		./$(TARGET_BIN) --jsonl "$$file" > "$$file.out.jsonl" 2> "$$file.err.jsonl" || true; \
	done

# Roda ambos os testes
test: test-valid test-invalid

test-parser: parser
	python3 -m unittest discover -s tests -v

test-semantic: semantic
	@ok=0; total=0; for file in "C semantico"/*.c; do total=$$((total+1)); ./$(SEMANTIC_TARGET) "$$file" >/dev/null 2>/dev/null; rc=$$?; case "$$file" in *01_*|*02_*|*03_*|*04_*|*05_*|*06_*|*07_*|*08_*|*09_*|*10_*) exp=0;; *) exp=4;; esac; if [ "$$rc" -eq "$$exp" ]; then ok=$$((ok+1)); fi; done; echo "Semantica C: $$ok/$$total casos passaram."; test "$$ok" -eq "$$total"

# Executa os 50 casos externos do professor.
# Uso: make test-parser-50 CASES_DIR="C:\\caminho\\testes-parser-50\\testes-parser-50\\casos"
CASES_DIR ?= ../testes-parser-50/testes-parser-50/casos
test-parser-50:
	python test_parser_50.py "$(CASES_DIR)"

clean:
	$(RM) C/*.o $(TARGET_BIN)
	$(RM) $(PARSER_TARGET)
	$(RM) $(SEMANTIC_TARGET)
	$(RM) ProjetoMiniC/casos-programas-c/*.out.jsonl
	$(RM) ProjetoMiniC/casos-invalidos/*.out.jsonl
	$(RM) ProjetoMiniC/casos-invalidos/*.err.jsonl

.PHONY: all parser semantic clean test test-valid test-invalid test-parser test-parser-50 test-semantic
