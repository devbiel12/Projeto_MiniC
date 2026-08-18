# Analisador Léxico MiniC (C)

Conversão para C de um analisador léxico (scanner) da linguagem **MiniC**,
originalmente implementado em Python. Percorre o código-fonte
caractere a caractere (autômato manual, sem expressões regulares),
gera a lista de tokens e reporta erros léxicos sem interromper a
análise (recuperação local: ignora o trecho inválido e continua).

Utiliza **apenas bibliotecas nativas da linguagem C**: `stdio.h`,
`stdlib.h`, `string.h`, `ctype.h` e `stddef.h`. Nenhuma dependência
externa.

## Estrutura do projeto

| Arquivo | Responsabilidade |
|---|---|
| `token_types.h` / `.c` | Enum `TokenType` e tabela de palavras reservadas |
| `token.h` / `.c` | Struct `Token` (tipo, lexema, linha, coluna, atributo) |
| `errors.h` / `.c` | Erros léxicos (símbolo inválido, string/comentário/char não terminados, etc.) |
| `scanner.h` / `.c` | Motor da análise léxica (o *scanner* propriamente dito) |
| `util.h` / `.c` | Alocação segura (`xmalloc`/`xrealloc`/`xstrdup`) e string dinâmica (`DynStr`) |
| `main.c` | Programa principal: lê um arquivo `.mc` (ou a entrada padrão) e roda o scanner |
| `Makefile` | Compila o projeto |

## Como compilar

Com `make`:

```bash
make
```

Ou direto com `gcc`:

```bash
gcc -std=c11 -Wall -Wextra -pedantic -O2 -o minic_scanner main.c scanner.c token.c token_types.c errors.c util.c
```

## Como executar

Passando um arquivo-fonte MiniC:

```bash
./minic_scanner arquivo.mc
```

Ou lendo da entrada padrão (digite o código e finalize com `Ctrl+D`
no Linux/Mac ou `Ctrl+Z` + Enter no Windows):

```bash
./minic_scanner
```

A saída mostra:

1. Uma tabela com todos os tokens reconhecidos (tipo, lexema, linha,
   coluna e atributo).
2. Um relatório com os erros léxicos encontrados (ou a confirmação
   de que nenhum foi encontrado).

O programa retorna código de saída `0` se não houver erros léxicos,
e `1` caso contrário.

## Tokens reconhecidos

- **Palavras reservadas:** `bool`, `int`, `float`, `char`, `double`,
  `void`, `true`, `false`, `if`, `else`, `while`, `for`, `return`,
  `break`, `continue`, `print`, `read`
- **Identificadores** e **literais** (inteiro, real, string, char)
- **Operadores** aritméticos, relacionais, lógicos (`&&`, `||`, `!`)
  e de atribuição
- **Delimitadores** (`(` `)` `{` `}` `[` `]` `;` `,` `.`)
- **Comentários** de linha (`//`) e de bloco (`/* ... */`), ignorados
  pelo scanner

## Erros léxicos detectados

- Símbolo inválido (caractere fora do alfabeto da linguagem)
- Identificador inválido (começando com dígito)
- Literal real mal formado (ponto sem parte fracionária, ex.: `3.`)
- Cadeia de caracteres (`"..."`) não terminada
- Comentário de bloco (`/* ... */`) não terminado
- Literal de caractere (`'...'`) mal formado

## Origem

Conversão fiel de um analisador léxico em Python (pacote
`minic_scanner`, módulos `token_types.py`, `tokens.py`, `errors.py`
e `scanner.py`), adaptado para C respeitando as particularidades da
linguagem (sem exceções, sem tipos union nativos, `EOF`/`ERROR`
renomeados para `TOK_EOF`/`TOK_ERROR` por colidirem com macros da
biblioteca padrão).
