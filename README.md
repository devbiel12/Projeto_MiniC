# Projeto MiniC

Compilador para a linguagem **MiniC** (um subconjunto de C), desenvolvido em duas implementações paralelas:

- **Python** — implementação principal, em `ProjetoMiniC/src`
- **C** — implementação em `C/` (analisador léxico e analisador sintático)

O objetivo é construir, em etapas, um pipeline de compilação completo: análise léxica, análise sintática, análise semântica, geração de código intermediário, otimização e geração de código final.

## Estado atual

| Etapa | Python | C |
|---|---|---|
| Análise léxica | ✅ Implementada | ✅ Implementada |
| Análise sintática | ✅ Implementada — passa nos 50 casos do professor | 🚧 Implementada, mas a AST ainda sai no formato antigo (ver [Testes](#testes)) |
| AST | ✅ Implementada (`src/ast`), com impressão em árvore e S-expression | 🚧 Implementada (`C/ast.c`), formato ainda não alinhado com o Python |
| Análise semântica | 🚧 Estrutura criada (`src/semantic`) | — |
| Geração de código / IR / otimização | 🚧 Estruturas criadas (`src/codegen`, `src/ir`, `src/optimizer`) | — |

A versão Python é a referência: é a que está validada contra os 50 casos de teste do parser.

## Requisitos

- **Python 3.10+** (testado com 3.12), somente biblioteca padrão
- **Tkinter** — usado nas interfaces gráficas e importado pelos módulos `python -m ProjetoMiniC.src.lexer` / `.parser` e pelos testes em `tests/`
- **gcc** (C11) e **make** para a versão em C

## Estrutura do repositório

```text
Projeto_MiniC/
├── main.py                      # Ponto de entrada principal (CLI + GUI) da versão Python
├── parser.py                    # CLI do parser: python parser.py arquivo.c
├── scanner.py                   # CLI do lexer, com resolução automática de path
├── scanner.c                    # Junta os módulos de C/ para compilar com: gcc scanner.c -o scanner
├── Makefile                     # Build e testes da versão em C (rodar SEMPRE a partir da raiz)
├── test_parser_50.py            # Runner dos 50 casos do parser (usa parser.py)
├── test_scanner_python.sh       # Compara os tokens do scanner Python com os .expected.jsonl
├── test_scanner_c.sh            # Compara os tokens do scanner C com os .expected.jsonl
├── tmp_validate.py              # Script temporário de validação rápida do lexer
├── tests/
│   └── test_parser.py           # Testes unittest do parser (Python × C)
├── testes-parser-50/
│   └── testes-parser-50/        # Pacote do professor: casos/, manifesto.json, README, INDICE, EXECUCAO
├── C/                           # Implementação em C
│   ├── main.c                   # CLI do scanner
│   ├── scanner.c / scanner.h
│   ├── token.c / token.h
│   ├── token_types.c / token_types.h
│   ├── errors.c / errors.h
│   ├── util.c / util.h
│   ├── parser_main.c            # CLI do parser
│   ├── parser.c / parser.h
│   └── ast.c / ast.h
└── ProjetoMiniC/                # Implementação em Python + recursos do projeto
    ├── docs/                    # Gramática (EBNF), especificação e notas
    ├── casos-programas-c/       # Programas .c válidos usados como casos de teste do lexer
    ├── casos-invalidos/         # Casos .minic com erros léxicos propositais
    └── src/
        ├── lexer/               # Análise léxica (scanner, tokens, erros, JSONL, GUI)
        ├── parser/              # Análise sintática (parser, erros, GUI)
        ├── ast/                 # Nós da AST (nodes.py) e impressão (printer.py)
        ├── semantic/            # (em construção)
        ├── codegen/             # (em construção)
        ├── ir/                  # (em construção)
        └── optimizer/           # (em construção)
```

## Executando a versão em Python

Todos os comandos abaixo devem ser executados **a partir da raiz do repositório**.

### Interface gráfica

```bash
python main.py
```

Abre o painel principal, com um botão para cada etapa do compilador. **Análise Léxica** e **Análise Sintática** abrem interfaces próprias; as demais etapas ainda exibem um aviso de "em desenvolvimento".

### Linha de comando

```bash
python main.py arquivo.minic                # análise léxica (tokens + diagnóstico)
python main.py arquivo.minic --tokens       # só a tabela de tokens
python main.py arquivo.minic --errors       # só os erros léxicos
python main.py arquivo.minic --jsonl        # tokens em JSONL (erros em JSONL no stderr)
python main.py arquivo.minic --parse        # roda o parser e informa se há erros sintáticos
python main.py arquivo.minic --ast          # imprime a AST em árvore
python main.py arquivo.minic --ast --sexp   # imprime a AST em S-expression
```

Atalhos por etapa:

```bash
python scanner.py arquivo.minic --jsonl     # apenas o lexer (aceita caminho relativo a ProjetoMiniC/)
python parser.py arquivo.c                  # apenas o parser; imprime a AST em S-expression
```

Exemplo de saída em S-expression:

```text
Program(Function(int main() Block(Return(Lit(int,0)))))
```

Os módulos também podem ser executados como pacote (também a partir da raiz):

```bash
python -m ProjetoMiniC.src.lexer            # interface gráfica do lexer
python -m ProjetoMiniC.src.lexer arquivo.minic --jsonl
python -m ProjetoMiniC.src.parser           # interface gráfica do parser
```

### Códigos de saída

| Código | Significado |
|---|---|
| `0` | Sucesso |
| `1` | Uso incorreto ou arquivo não encontrado/ilegível |
| `2` | Erro léxico |
| `3` | Erro sintático |

### Interfaces gráficas

- **Lexer** (`src/lexer/__main__.py`): executa os testes embutidos, analisa código colado ou aberto de arquivo (`.minic`, `.mc`, `.c`, `.txt`) e mostra a saída formatada, os tokens em JSONL e os erros em JSONL em abas separadas, com opção de copiar o JSONL.
- **Parser** (`src/parser/__main__.py`): permite digitar ou carregar um arquivo, executar o parser e consultar a AST, os diagnósticos com linha/coluna e os tokens reconhecidos.

## Executando a versão em C

O `Makefile` usa caminhos relativos à **raiz** do repositório. Não é mais necessário entrar em `C/`.

```bash
make                                  # compila o scanner em C/minic_scanner
./C/minic_scanner arquivo.c           # saída legível (tabela de tokens + diagnóstico)
./C/minic_scanner arquivo.c --jsonl   # tokens em JSONL no stdout, erros no stderr

make parser                           # compila o parser em ./parser
./parser arquivo.c                    # imprime a AST em S-expression
```

Também é possível compilar o scanner em um único passo, sem o Makefile:

```bash
gcc -std=c11 scanner.c -o scanner
./scanner arquivo.c
```

O parser em C usa os mesmos códigos de saída da tabela acima (`0`, `1`, `2` e `3`). No Windows, o `Makefile` já trata a extensão `.exe` e o comando de remoção.

Para remover binários e arquivos gerados: `make clean`.

## Testes

| Comando (na raiz) | O que faz |
|---|---|
| `make test` | Roda o scanner em C sobre `casos-programas-c/` e `casos-invalidos/` e grava as saídas em `*.out.jsonl` / `*.err.jsonl` (não compara com o esperado). Também há `make test-valid` e `make test-invalid`. |
| `bash test_scanner_python.sh scanner.py ProjetoMiniC/casos-programas-c` | Compara os tokens do scanner Python com os `.expected.jsonl`. |
| `bash test_scanner_c.sh scanner.c ProjetoMiniC/casos-programas-c` | Compila `scanner.c` e compara os tokens do scanner C com os `.expected.jsonl`. |
| `python test_parser_50.py testes-parser-50/testes-parser-50/casos` | Roda os 50 casos do parser (Python). |
| `make test-parser-50 CASES_DIR=testes-parser-50/testes-parser-50/casos` | Mesmo que o anterior, via Makefile. |
| `make test-parser` | Compila o parser em C e roda `tests/test_parser.py` (requer Tkinter). |

Observações:

- Os scripts `test_scanner_*.sh` recebem `[scanner] [pasta-de-testes]` e geram um `output.jsonl` temporário na pasta atual.
- **50 casos do parser:** os casos 01–25 devem ser aceitos com a AST esperada e os casos 26–50 devem ser rejeitados. O runner retorna `0` quando todos passam, `1` quando há falhas e `2` se a pasta de casos não for encontrada. Sem argumento, ele procura em `~/Downloads/testes-parser-50/...` e em `../testes-parser-50/...`, por isso informe o caminho como nos exemplos acima.
- **Parser em C:** rejeita os 25 casos inválidos, mas só 3 dos 25 casos válidos batem com a AST esperada, porque a saída em C ainda usa o formato antigo (por exemplo `VarDecl(int x,Lit(42))` em vez do formato do Python). Por isso, `make test-parser`, que compara a saída de Python e C, ainda falha até o formato ser alinhado.

## O que o lexer reconhece

- palavras reservadas, identificadores, números inteiros e reais, operadores e delimitadores;
- strings e caracteres, incluindo casos malformados;
- comentários de linha e de bloco;
- erros léxicos, como símbolos desconhecidos, comentários não terminados, strings/caracteres não terminados, números reais malformados e identificadores iniciados por dígito.

Cada token reconhecido carrega tipo, lexema, atributo (quando aplicável), linha e coluna. A saída pode ser formatada em tabela ou serializada em JSONL, seguindo o mesmo formato nas versões Python e C.

## Análise sintática e AST

O parser consome os `Token` produzidos pelo lexer e constrói uma AST para declarações (globais e locais, inclusive listas separadas por vírgula e vetores), funções e parâmetros, comandos de controle de fluxo, entrada/saída, chamadas, indexação e expressões (com precedência e associatividade). Os nós usados na saída são: `Program`, `Function`, `Block`, `VarDecl`, `If`, `While`, `Return`, `ExprStmt`, `Assign`, `Binary`, `Unary`, `Call`, `Index`, `Id` e `Lit`.

A AST pode ser exibida de duas formas:

- **S-expression** (`parser.py`, `main.py --ast --sexp`): uma linha, no formato usado pelos casos de teste.
- **Árvore indentada** (`main.py --ast`): mais legível para leitura no terminal.

Erros léxicos e sintáticos são reportados com linha e coluna.

## Casos de teste

- `ProjetoMiniC/casos-programas-c/`: programas `.c` válidos (Fibonacci, números primos, média de vetor, menu interativo, controle de temperatura), cada um com o `.expected.jsonl` correspondente.
- `ProjetoMiniC/casos-invalidos/`: trechos `.minic` com erros léxicos propositais, cada um com `.expected.jsonl` (tokens esperados) e `.errors.jsonl` (erros esperados).
- `testes-parser-50/testes-parser-50/casos/`: 50 programas do professor para o parser. Cada pasta tem `codigo.c`, `ast.esperada.txt` e `resultado.esperado.txt`. O `manifesto.json` lista título e diretório de cada caso.

## Documentação

- `ProjetoMiniC/docs/README.md`: notas sobre a implementação do lexer em Python.
- `ProjetoMiniC/docs/gramatica.ebnf`: gramática da linguagem MiniC.
- `ProjetoMiniC/docs/especificacao.md` e `ProjetoMiniC/docs/arquitetura.md`: ainda a serem preenchidos.
- `testes-parser-50/testes-parser-50/README.md`: descrição do pacote de 50 casos.

## Tecnologias

- Python 3 + Tkinter (interface gráfica)
- C11 (gcc, make)
- JSONL como formato de intercâmbio de tokens/erros entre as implementações e os casos de teste
