# Projeto MiniC

Compilador educacional para a linguagem **MiniC**, um subconjunto de C. O projeto reúne implementações em Python e C para análise léxica, análise sintática e análise semântica, além de interfaces gráficas, ferramentas de linha de comando e testes automatizados.

O objetivo é construir gradualmente um pipeline de compilação: leitura do código-fonte, análise léxica, análise sintática, construção da AST, análise semântica, geração de representação intermediária (IR), otimização e geração de código.

## Estado atual do projeto

| Etapa | Python | C |
|---|---|---|
| Análise léxica e geração de tokens | Implementada | Implementada |
| Análise sintática | Implementada | Implementada |
| Construção e serialização da AST | Implementada | Implementada |
| Análise semântica | Implementada | Implementada |
| Representação intermediária (IR/3AC) | Pendente | Pendente |
| Otimização | Pendente | Pendente |
| Geração de código executável | Pendente | Pendente |

> **Importante:** o projeto analisa e representa programas MiniC, mas ainda não executa esses programas nem gera um executável final. Os módulos de IR, otimização e geração de código ainda não possuem implementação funcional.

## Principais funcionalidades

### Análise léxica

O lexer reconhece palavras reservadas, identificadores, números inteiros e reais, operadores, delimitadores, strings, caracteres e comentários. Também identifica erros como símbolos desconhecidos, comentários ou strings não terminados, números reais malformados e identificadores iniciados por dígitos.

Cada token contém tipo, lexema, atributo quando aplicável, linha e coluna. A saída pode ser exibida em tabela ou serializada em JSONL. Na implementação C, os tokens JSONL são enviados para `stdout` e os erros JSONL para `stderr`.

### Análise sintática e AST

O parser consome os tokens do lexer e constrói uma árvore sintática abstrata (AST). São contempladas declarações globais e locais, funções e parâmetros, vetores, comandos de controle de fluxo, entrada e saída, chamadas, indexação e expressões com precedência e associatividade.

A AST pode ser apresentada como S-expression, usada nos testes oficiais, ou como árvore indentada para facilitar a leitura. Erros léxicos e sintáticos são reportados com linha e coluna.

### Análise semântica

A análise semântica é implementada em **Python e C** e verifica restrições estáticas do programa após a construção da AST. Ela não substitui o lexer ou o parser: as etapas anteriores são executadas primeiro e, caso encontrem erros, a análise semântica não prossegue.

As funcionalidades incluem:

- **Tabela de símbolos e escopos léxicos:** registra identificadores, tipos, categorias, escopos e posições. Permite sombreamento em escopos internos e rejeita declarações duplicadas no mesmo escopo.
- **Declarações e identificadores:** detecta identificadores não declarados e usos incompatíveis com a categoria do símbolo.
- **Verificação de tipos:** verifica expressões aritméticas e lógicas, comparações, atribuições, condições e retornos. Permite promoção numérica de `int` para `float`, mas não aceita estreitamento implícito de `float` para `int`.
- **Funções:** registra assinaturas, permite recursão e chamadas a funções definidas posteriormente e valida a existência da função, a quantidade e os tipos dos argumentos.
- **Vetores:** verifica o uso de vetores, a compatibilidade de tipos e se os índices são inteiros.
- **Retornos e fluxo de controle:** valida o tipo de retorno, a cobertura de retorno em funções e o uso de `break` e `continue` dentro de laços.
- **Valores `void` e atribuições:** impede o uso de funções `void` como expressões e exige que destinos de atribuição sejam variáveis ou elementos de vetor atribuíveis.
- **AST anotada:** associa informações semânticas aos nós, como tipo inferido, símbolo resolvido e coerções numéricas.
- **Diagnósticos:** informa erros semânticos com código, mensagem e posição no código-fonte.

Os diagnósticos oficiais incluem códigos `SEM001` a `SEM013`. Alguns casos adicionais utilizam códigos específicos, como `E_OPERATOR`, `E_CALL` e `E_ARRAY`.

#### Executar a análise semântica

Execute os comandos a partir da raiz do repositório.

**Python — analisar um arquivo:**

```bash
python3 minic.py "arquivo.c"
```

**Python — opção semântica do ponto de entrada principal:**

```bash
python main.py "arquivo.c" --semantic
```

**Abrir a interface gráfica semântica:**

```bash
python -m ProjetoMiniC.src.semantic
```

**Abrir a interface gráfica com um arquivo carregado:**

```bash
python -m ProjetoMiniC.src.semantic "arquivo.c"
```

A interface semântica permite digitar ou abrir um arquivo, executar a análise e consultar as abas **Diagnóstico Semântico**, **AST Anotada** e **Tokens**. Também oferece exemplos válidos e inválidos e a opção de limpar os resultados.

O wrapper `minic.py` é indicado para execução automatizada. Seus códigos de saída são:

| Código | Significado |
|---:|---|
| `0` | Programa aceito pela análise semântica |
| `1` | Uso incorreto, arquivo inexistente ou erro de leitura |
| `2` | Erro léxico |
| `3` | Erro sintático |
| `4` | Erro semântico |

Quando o programa é aceito, a saída termina com:

```text
Análise semântica concluída: 0 erros; programa aceito.
```

Quando existem erros semânticos, os diagnósticos são apresentados seguidos de um resumo informando a quantidade de erros e a rejeição do programa.

#### Testes semânticos oficiais

O conjunto oficial contém **20 casos**: 10 programas aceitos e 10 rejeitados. Os scripts comparam a saída com os arquivos `.gabarito`, preservando a verificação exata das mensagens esperadas.

**Testes em C:**

```bash
./testes_semanticos_c.sh minic.c minic-testes-semanticos
```

**Testes em Python:**

```bash
./testes_semanticos_py.sh minic.py minic-testes-semanticos
```

Os scripts exibem o resultado de cada caso, sua classificação como `ACEITO` ou `REJEITADO` e um resumo final. O resultado esperado é:

```text
Resumo Semântico: 10 aceitos | 10 rejeitados (Total: 20 casos)
```

A documentação técnica também registra testes adicionais de semântica, incluindo casos válidos e inválidos, posições dos diagnósticos, símbolos e paridade entre as implementações Python e C.

Consulte [`ProjetoMiniC/docs/semantica.md`](ProjetoMiniC/docs/semantica.md) para detalhes das regras, dos diagnósticos e dos resultados de validação.

## Executando a versão em Python

Todos os comandos abaixo devem ser executados a partir da raiz do repositório.

### Interface gráfica principal

```bash
python main.py
```

O painel principal possui atalhos para as etapas do compilador. As interfaces de análise léxica e sintática são abertas separadamente. A interface semântica também existe e pode ser iniciada com `python -m ProjetoMiniC.src.semantic`; entretanto, o botão de análise semântica do painel principal ainda exibe uma mensagem antiga de funcionalidade em desenvolvimento. IR, otimização e geração de código permanecem pendentes.

### Linha de comando

```bash
python main.py arquivo.minic                # análise léxica
python main.py arquivo.minic --tokens       # apenas a tabela de tokens
python main.py arquivo.minic --errors       # apenas erros léxicos
python main.py arquivo.minic --jsonl        # tokens em JSONL
python main.py arquivo.minic --parse        # análise sintática
python main.py arquivo.minic --ast          # AST em árvore indentada
python main.py arquivo.minic --ast --sexp   # AST em S-expression
python main.py "arquivo.c" --semantic       # análise semântica
```

Atalhos por etapa:

```bash
python scanner.py arquivo.minic --jsonl
python parser.py arquivo.c
python -m ProjetoMiniC.src.lexer
python -m ProjetoMiniC.src.lexer arquivo.minic --jsonl
python -m ProjetoMiniC.src.parser
python -m ProjetoMiniC.src.semantic
```

## Executando a versão em C

O `Makefile` usa caminhos relativos à raiz do repositório.

```bash
make
./C/minic_scanner arquivo.c
./C/minic_scanner arquivo.c --jsonl

make parser
./parser arquivo.c
```

Para compilar o scanner em um único passo:

```bash
gcc -std=c11 scanner.c -o scanner
./scanner arquivo.c
```

A análise semântica em C pode ser executada pelo wrapper e pelos scripts de teste documentados na seção de análise semântica. Para executar os testes oficiais, use `testes_semanticos_c.sh`, que realiza a compilação necessária.

## Testes do projeto

### Testes oficiais do parser

O pacote `testes-parser-50` contém 50 casos: os casos 01 a 25 devem ser aceitos e produzir a AST esperada; os casos 26 a 50 devem ser rejeitados com erro sintático.

```bash
bash testar_parser.sh ./testes-parser-50
bash testar_parser_python.sh ./testes-parser-50 ./parser.py
bash testar_parser_c.sh ./testes-parser-50 ./parser.c
```

O resultado esperado para o conjunto oficial é `50/50 casos passaram`.

### Testes de regressão

```bash
python -m unittest discover -s tests -v
```

Com Make, quando disponível:

```bash
make test-parser
```

### Testes do lexer

```bash
bash test_scanner_python.sh ./scanner.py ./ProjetoMiniC
bash test_scanner_c.sh ./scanner.c ./ProjetoMiniC
```

Com Make:

```bash
make test-valid
make test-invalid
make test
```

Os fixtures JSONL validam a sequência de tokens e, quando disponível, os diagnósticos léxicos esperados.

## Organização e documentação técnica

Arquivos e diretórios relevantes:

- `C/scanner.c` e `C/scanner.h`: scanner em C.
- `C/token.c` e `C/token.h`: estrutura de tokens.
- `C/token_types.c` e `C/token_types.h`: tipos de tokens e palavras reservadas.
- `C/errors.c` e `C/errors.h`: erros léxicos.
- `C/util.c` e `C/util.h`: utilitários de memória, strings e leitura de arquivos.
- `C/parser.c` e `C/parser_main.c`: parser em C e sua entrada de linha de comando.
- `C/ast.c` e `C/ast.h`: nós e serialização da AST.
- `ProjetoMiniC/src/lexer/`: implementação e interface do lexer em Python.
- `ProjetoMiniC/src/parser/`: parser, AST e interface sintática em Python.
- `ProjetoMiniC/src/semantic/`: analisador semântico e interface gráfica.
- `ProjetoMiniC/docs/semantica.md`: documentação detalhada da análise semântica.
- `ProjetoMiniC/docs/especificacao.md`: especificação léxica, regras de tokens, recuperação e JSONL.
- `testes-parser-50/`: pacote externo de testes sintáticos.
- `minic-testes-semanticos/`: casos oficiais de teste semântico.

## Tecnologias

- Python 3.10+
- Tkinter
- C11
- GCC
- Make
- Bash
- JSONL para intercâmbio de tokens e diagnósticos do lexer

## Limitações conhecidas

- A análise semântica está implementada em Python e C; IR, otimização e geração de código ainda estão pendentes.
- O botão de análise semântica no painel principal não foi conectado à interface semântica independente.
- O compilador ainda não executa os programas MiniC nem gera um executável final.
- Os testes do lexer, parser e semântica validam análise e diagnósticos, não a execução dos programas.

## Limpeza

Para remover objetos, executáveis e arquivos gerados pelo Make:

```bash
make clean
```

Os scripts de teste semântico usam diretórios temporários para executáveis C e os removem ao terminar.
