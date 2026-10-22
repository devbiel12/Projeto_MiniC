# Projeto MiniC

Projeto acadêmico de desenvolvimento de um compilador para a linguagem **MiniC**, um subconjunto da linguagem C. O repositório contém uma implementação em Python e uma implementação em C voltada à análise léxica.

## Objetivo

Desenvolver um compilador por etapas, estudando como um código-fonte é processado. O projeto prevê etapas como:

- Análise léxica: identificação de tokens no código-fonte.
- Análise sintática: verificação da estrutura do programa.
- Análise semântica: verificação do significado e das regras semânticas.
- Geração de código intermediário, otimização e geração de código final.

**Importante:** nem todas essas etapas estão implementadas. Consulte a tabela abaixo para ver o estado descrito neste repositório.

## Estado do projeto

| Etapa | Python | C |
|---|---|---|
| Análise léxica | Implementada | Implementada |
| Análise sintática | Em desenvolvimento | Não indicada como implementada |
| Análise semântica | Em desenvolvimento | Não indicada como implementada |
| AST (árvore sintática abstrata) | Estrutura criada | — |
| Código intermediário, otimização e geração de código | Estruturas criadas | — |

## Tecnologias utilizadas

- **Python 3.10 ou superior**
- **Tkinter**, para a interface gráfica da versão Python
- **C11**
- **GCC** e **Make**, para compilar a versão em C
- **JSONL**, para representar tokens e erros em formato estruturado

## Estrutura do repositório

```text
Projeto_MiniC/
├── main.py
├── scanner.py
├── Makefile
├── C/
│   ├── main.c
│   ├── scanner.c
│   ├── scanner.h
│   ├── token.c
│   ├── token.h
│   ├── token_types.c
│   ├── token_types.h
│   ├── errors.c
│   ├── errors.h
│   ├── util.c
│   └── util.h
└── ProjetoMiniC/
    ├── docs/
    ├── casos-programas-c/
    ├── casos-invalidos/
    └── src/
        ├── lexer/
        ├── parser/
        ├── semantic/
        ├── ast/
        ├── codegen/
        ├── ir/
        └── optimizer/
```

## Como executar a versão em Python

### 1. Pré-requisitos

Instale o Python 3.10 ou superior. Para abrir a interface gráfica, também é necessário ter o Tkinter disponível na instalação do Python.

### 2. Baixe o projeto

```bash
git clone https://github.com/devbiel12/Projeto_MiniC.git
cd Projeto_MiniC
```

### 3. Abra a interface gráfica

Na pasta principal do repositório, execute:

```bash
python main.py
```

### 4. Analise um arquivo pelo terminal

Passe o caminho do arquivo que deseja analisar:

```bash
python main.py caminho/para/arquivo.minic
```

Opções disponíveis:

```bash
python main.py caminho/para/arquivo.minic --tokens
python main.py caminho/para/arquivo.minic --errors
python main.py caminho/para/arquivo.minic --jsonl
```

- `--tokens`: exibe somente a tabela de tokens.
- `--errors`: exibe somente os erros léxicos.
- `--jsonl`: apresenta tokens e erros no formato JSONL.

### Executar o lexer diretamente

Também é possível executar o módulo a partir da pasta `ProjetoMiniC`:

```bash
cd ProjetoMiniC
python -m src.lexer
```

Para analisar um arquivo usando essa forma de execução, ajuste o caminho do arquivo conforme a pasta atual.

## Como executar a versão em C

É necessário ter um compilador C compatível com C11 e o Make instalados.

Na raiz do repositório, entre na pasta `C` e compile o projeto:

```bash
cd C
make -f ../Makefile
```

Depois da compilação, execute o analisador léxico:

```bash
./minic_scanner arquivo.c
```

Para obter a saída no formato JSONL:

```bash
./minic_scanner arquivo.c --jsonl
```

### Executar os testes da versão em C

Os comandos abaixo também devem ser executados dentro da pasta `C`:

```bash
make -f ../Makefile test-valid
make -f ../Makefile test-invalid
make -f ../Makefile test
```

Para remover os binários e arquivos gerados:

```bash
make -f ../Makefile clean
```

> No Windows, os comandos de execução do binário podem precisar ser adaptados ao ambiente utilizado, como MSYS2, MinGW ou WSL.

## O que a análise léxica reconhece

O lexer identifica elementos como:

- Palavras reservadas e identificadores.
- Números inteiros e reais.
- Operadores e delimitadores.
- Strings e caracteres.
- Comentários de linha e de bloco.

Ele também identifica erros léxicos, como símbolos desconhecidos, comentários ou strings não terminados, números reais malformados e identificadores iniciados por dígitos.

Cada token contém informações como tipo, lexema, atributo (quando aplicável), linha e coluna.

## Casos de teste

Os casos de teste estão organizados em pastas dentro de `ProjetoMiniC/`:

- `casos-programas-c/`: programas válidos usados para verificar a análise léxica.
- `casos-invalidos/`: arquivos com erros léxicos intencionais.

Os arquivos esperados ajudam a comparar os resultados produzidos pelo analisador com os resultados de referência.

## Documentação

A documentação complementar fica na pasta `ProjetoMiniC/docs/`. Ela inclui informações sobre a implementação Python e a gramática da linguagem MiniC.

## Observação

Este é um projeto em desenvolvimento. A presença de uma pasta ou estrutura para uma etapa do compilador não significa, por si só, que essa etapa esteja pronta ou funcionando completamente. Consulte o código e os testes correspondentes antes de considerar uma funcionalidade concluída.
