# Projeto MiniC

Compilador para a linguagem **MiniC** (um subconjunto didático e estrito da linguagem C), desenvolvido com duas implementações complementares:

- **Python** — implementação principal completa de todo o frontend em [`ProjetoMiniC/src`](file:///c:/Users/guilherme.lima/OneDrive%20-%20Alpargatas%20S.A/Documentos/Projeto_MiniC/ProjetoMiniC/src), incluindo analisador léxico, sintático (com árvore AST), semântico e interfaces visuais (Tkinter).
- **C** — implementação em C11 do analisador léxico em [`C/`](file:///c:/Users/guilherme.lima/OneDrive%20-%20Alpargatas%20S.A/Documentos/Projeto_MiniC/C) e executor canônico de testes semânticos em [`minic.c`](file:///c:/Users/guilherme.lima/OneDrive%20-%20Alpargatas%20S.A/Documentos/Projeto_MiniC/minic.c).

O objetivo do projeto é construir o pipeline completo de compilação: análise léxica, sintática, semântica, geração de código intermediário (IR), otimização e geração de código final.

---

## Estado Atual do Compilador

| Etapa | Python | C | Status / Detalhes |
|---|:---:|:---:|---|
| **Análise Léxica (Scanner)** | ✅ 100% Funcional | ✅ 100% Funcional | Tabela de tokens, atributos, diagnósticos com linha/coluna exatos e exportação JSONL. Suporta GUI e CLI. |
| **Análise Sintática (Parser)** | ✅ 100% Funcional | — | Descida recursiva cobrindo a gramática EBNF de MiniC, recuperação em modo pânico e construção de AST completa. |
| **Árvore Sintática (AST)** | ✅ 100% Funcional | — | Hierarquia de classes de nós (`NoAST`), visualizador em árvore indentada e representação S-Expression (`--sexp`). |
| **Análise Semântica (Aula 15)** | ✅ 100% Funcional | ✅ 100% Funcional | Tabela de símbolos hierárquica, escopos aninhados, tipagem estática, aridade, fluxo de controle e diagnósticos canônicos (`SEM001`–`SEM013`). **20/20 testes aprovados**. |
| **Interface Visual (GUI)** | ✅ 100% Funcional | — | Painel Launcher central (`main.py`) e telas dedicadas com editor e visualizador para Léxico, Sintático e Semântico. |
| **IR / Otimização / Codegen** | 🚧 Estrutura base | — | Estruturas e módulos preparados em `src/ir`, `src/optimizer` e `src/codegen` para as próximas fases. |

---

## Estrutura do Repositório

```text
Projeto_MiniC/
├── main.py                      # Launcher unificado (GUI Tkinter) e ponto de entrada CLI
├── minic.py                     # Driver CLI da Análise Semântica em Python (compatível com testes oficiais)
├── minic.c                      # Driver da Análise Semântica em C (compilação GCC / testes oficiais)
├── scanner.py                   # Ponto de entrada de conveniência do Scanner léxico
├── testes_semanticos_py.sh      # Script Bash de validação da Análise Semântica (Python)
├── testes_semanticos_c.sh       # Script Bash de validação da Análise Semântica (C)
├── Makefile                     # Build do scanner em C
├── C/                           # Implementação do scanner léxico em C
│   ├── main.c
│   ├── scanner.c / scanner.h
│   ├── token.c / token.h
│   ├── token_types.c / token_types.h
│   ├── errors.c / errors.h
│   └── util.c / util.h
└── ProjetoMiniC/                # Implementação completa do frontend em Python
    ├── docs/                    # Especificação, gramática EBNF e notas da disciplina
    ├── casos-programas-c/       # Casos de teste válidos para análise léxica
    ├── casos-invalidos/         # Casos de teste com erros léxicos
    └── src/
        ├── lexer/               # Scanner, tokens, categorias léxicas e GUI (`__main__.py`)
        ├── parser/              # Parser descendente recursivo e GUI (`__main__.py`)
        ├── ast/                 # Nós da AST (`nodes.py`) e formatadores (`printer.py`)
        ├── semantic/            # Analisador Semântico (`analyzer.py`) e GUI (`__main__.py`)
        ├── ir/                  # Representação intermediária (em desenvolvimento)
        ├── optimizer/           # Otimizador de código intermediário (em desenvolvimento)
        └── codegen/             # Gerador de código-alvo (em desenvolvimento)
```

---

## Análise Semântica (Aula 15)

O analisador semântico valida todas as restrições de contexto estático da linguagem MiniC após a geração da AST.

### Diagnósticos Canônicos Suportados

| Código | Descrição da Regra Semântica | Exemplo de Ocorrência |
|---|---|---|
| **SEM001** | Identificador não declarado no escopo visível | Uso de variável ou função sem declaração prévia |
| **SEM002** | Redeclaração de identificador no mesmo escopo | Declarar `int x;` duas vezes no mesmo bloco |
| **SEM003** | Incompatibilidade de tipos ou estreitamento implícito | Atribuir `float` a `int` (estreitamento proibido) |
| **SEM005** | Condição de controle de fluxo não booleana | Expressão em `if`, `while` ou `for` que não resulta em `bool` |
| **SEM006** | Índice de vetor não inteiro | Acessar `v[2.5]` ou com expressão de tipo não-`int` |
| **SEM007** | Aridade incorreta em chamada de função | Chamar função com mais ou menos argumentos que o esperado |
| **SEM008** | Incompatibilidade de tipo em argumento de função | Passar `float` para parâmetro `int` em função |
| **SEM009** | Tipo de retorno incompatível com a assinatura | Retornar `float` em função com retorno `int` |
| **SEM010** | Comando `break` ou `continue` fora de laço | Uso solto dentro de funções ou apenas dentro de `if` |
| **SEM011** | Caminho de execução sem `return` em função não-void | Função não-`void` cujos fluxos não garantem retorno |
| **SEM012** | Uso de função `void` como expressão de valor | Atribuir `n = funcao_void();` |
| **SEM013** | Destino de atribuição não atribuível (violação de L-Value) | Atribuição inválida como `3 = n;` ou literais à esquerda |

### Validação dos Testes Oficiais (100% de Aprovação)

A suíte oficial do professor é composta por **20 casos de teste**:
- **10 Casos Aceitos (Válidos):** `01` a `10` (testando promoção implícita `int` → `float`, sombreamento léxico de variáveis locais/globais, curto-circuito lógico, vetores e parâmetros array, recursão mútua, comandos `void`, múltiplos ramos com `return`, etc.).
- **10 Casos Rejeitados (Inválidos):** `11` a `20` (testando emissão precisa dos erros semânticos canônicos `SEM001` a `SEM013`).

#### Execução dos Testes em Python

```bash
# Executar a bateria oficial de testes semânticos:
./testes_semanticos_py.sh minic.py "/caminho/para/pasta_testes"

# Resultado obtido:
# [OK] 01_promocao_numerica.c
# ...
# [OK] 20_destino_nao_atribuivel.c
# Resultado: 20/20 aprovados; 0 reprovados.
```

Execução pontual de um arquivo:
```bash
python minic.py programa.c
```

#### Execução dos Testes em C

```bash
# Executar a bateria oficial compilando o runner em C com GCC:
./testes_semanticos_c.sh minic.c "/caminho/para/pasta_testes"

# Resultado obtido:
# Compilando o analisador com gcc...
# [OK] 01_promocao_numerica.c
# ...
# [OK] 20_destino_nao_atribuivel.c
# Resultado: 20/20 aprovados; 0 reprovados.
```

---

## Interfaces Gráficas (UI / Tkinter)

O projeto conta com interfaces visuais completas e interativas para inspeção pedagógica de cada fase:

### 1. Painel Principal (Launcher)
```bash
python main.py
```
Abre o painel integrado que permite navegar e acionar com um clique:
- **Análise Léxica** (`ProjetoMiniC.src.lexer`)
- **Análise Sintática** (`ProjetoMiniC.src.parser`)
- **Análise Semântica** (`ProjetoMiniC.src.semantic`)
- Botões de prévia para as etapas subsequentes (IR, Otimizador, Codegen)

### 2. Telas Dedicadas de Cada Módulo
Cada módulo pode ser executado diretamente em modo gráfico isolado:

- **Interface da Análise Léxica:**
  ```bash
  python -m ProjetoMiniC.src.lexer
  ```
  Permite carregar arquivos `.minic`/`.c`, visualizar tokens em tabela categorizada, inspecionar lexemas, posições e erros léxicos.

- **Interface da Análise Sintática:**
  ```bash
  python -m ProjetoMiniC.src.parser
  ```
  Permite editar código, executar o parser descendente recursivo, visualizar a Árvore Sintática Abstrata (AST) formatada e inspecionar diagnósticos sintáticos.

- **Interface da Análise Semântica:**
  ```bash
  python -m ProjetoMiniC.src.semantic
  ```
  Permite carregar exemplos válidos e com erros semânticos, executar a análise estática e inspecionar diagnósticos formatados com linha, coluna, código de erro e detalhes.

---

## Executando as Etapas via Linha de Comando (CLI)

### 1. Análise Sintática e AST
```bash
# Validar apenas sintaxe (retorna 0 se OK, ou exibe erros sintáticos):
python main.py programa.c --parse

# Gerar e imprimir a AST em árvore hierárquica legível:
python main.py programa.c --ast

# Imprimir a AST em formato S-Expression parentetizado:
python main.py programa.c --ast --sexp
```

### 2. Análise Léxica (Scanner em Python)
```bash
python main.py programa.c --tokens   # Exibe tabela formatada de tokens
python main.py programa.c --errors   # Exibe diagnósticos de erros léxicos
python main.py programa.c --jsonl    # Saída estruturada em JSONL (padrão de testes)
```

### 3. Análise Léxica (Scanner em C)
```bash
cd C
make -f ../Makefile                 # Compila o executável minic_scanner
./minic_scanner arquivo.c           # Saída formatada de tokens
./minic_scanner arquivo.c --jsonl   # Saída em formato JSONL
make -f ../Makefile test            # Executa os testes de regressão do scanner em C
```

---

## Tecnologias e Diretrizes de Engenharia

- **Python 3.10+**: Código estritamente tipado (`typing`, `Optional`, `Union`), estruturas com `@dataclass`, padrões de design limpos e compatibilidade multi-plataforma (Windows, Linux, macOS).
- **C11**: Compilação via GCC com flags rigorosas (`-Wall -Wextra`).
- **Compatibilidade Canônica de Saída**: Tratamento rigoroso de quebras de linha (`CRLF` vs `LF`) e codificação UTF-8, garantindo correspondência byte a byte com os gabaritos e diffs dos scripts avaliadores.
