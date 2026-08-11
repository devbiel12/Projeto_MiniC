# Projeto MiniC

Este repositório reúne uma implementação do compilador MiniC em duas linguagens:

- Python
- C

O objetivo do projeto é desenvolver uma ferramenta para análise de código em linguagem C, cobrindo etapas fundamentais de compilação, como:

- identificação de tokens
- análise léxica
- análise sintática
- análise semântica

## Visão geral

O projeto está organizado em subpastas por linguagem e por módulos do compilador. A parte em Python já contém a estrutura base do lexer, com a definição de tokens, erros léxicos e rotinas para leitura do código-fonte.

## Estrutura do repositório

```text
Projeto_MiniC/
├── README.md
├── ProjetoMiniC/
│   ├── Python/
│   │   ├── README.md
│   │   ├── src/
│   │   │   ├── lexer/
│   │   │   ├── parser/
│   │   │   ├── semantic/
│   │   │   ├── ast/
│   │   │   ├── codegen/
│   │   │   ├── ir/
│   │   │   └── optimizer/
│   │   └── docs/
│   └── C/
```

## Executando a versão em Python

Acesse a pasta do projeto Python:

```powershell
EXEMPLO:
cd "C:\Users\guilherme\Documentos\GitHub\Projeto_MiniC\ProjetoMiniC\Python"
```

Se o ambiente ainda não tiver o Python configurado, use o `uv` para instalar uma versão funcional:

```powershell
uv python install 3.12
```

Depois execute o analisador léxico:

```powershell
uv run python -m src.lexer
```

## O que o lexer faz

O módulo de lexer está responsável por:

- percorrer o código-fonte caractere por caractere
- reconhecer palavras reservadas, identificadores, números e operadores
- identificar strings, caracteres e comentários
- registrar erros léxicos como símbolos inválidos, strings não fechadas e comentários sem fechamento
- produzir a lista de tokens para etapas posteriores do compilador

## Observações

- O projeto ainda está em evolução e os módulos posteriores (parser, semântica e geração de código) continuam sendo estruturados.
- A parte em Python é a base mais avançada no momento e funciona como referência para os demais módulos.

## Tecnologias

- Python
- uv (gerenciamento de ambiente Python)
- Git / GitHub para versionamento
