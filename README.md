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

O projeto está organizado em subpastas por linguagem e por módulos do compilador. A parte em Python já contém a estrutura base do lexer e uma interface em Tkinter para testar a análise léxica com diferentes entradas, inclusive análise de um arquivo, vários arquivos ou uma pasta inteira.

A interface atual mantém a saída formatada do lexer e adiciona visualização do JSONL acadêmico em abas separadas, exportação individual e em lote, cópia do JSONL para a área de transferência e navegação lateral entre as análises carregadas.

## Estrutura do repositório

```text
Projeto_MiniC/
├── README.md
├── ProjetoMiniC/
│   ├── Python/
│   │   ├── README.md
│   │   ├── src/
│   │   │   ├── lexer/
│   │   │   │   ├── __main__.py
│   │   │   │   ├── demo.py
│   │   │   │   ├── scanner.py
│   │   │   │   ├── token_types.py
│   │   │   │   ├── tokens.py
│   │   │   │   └── errors.py
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
cd "C:\Users\guilherme.lima\OneDrive - Alpargatas S.A\Documentos\GitHub\Projeto_MiniC\ProjetoMiniC\Python"
```

Se o ambiente ainda não tiver o Python configurado, use o `uv` para instalar uma versão funcional:

```powershell
uv python install 3.12
```

Depois execute o analisador léxico com a interface gráfica:

```powershell
uv run python -m src.lexer
```

## Interface de uso

A entrada principal em `src.lexer` oferece uma interface em Tkinter com estas opções:

1. executar os testes embutidos do lexer;
2. colar um trecho de código na própria interface e analisar;
3. abrir um arquivo `.minic`, `.mc` ou `.c`;
4. abrir vários arquivos de uma vez ou uma pasta inteira com arquivos MiniC;
5. navegar entre as análises carregadas em uma lista lateral;
6. visualizar a saída formatada, o JSONL acadêmico e o JSONL de erros em abas separadas;
7. exportar um JSONL individual ou em lote;
8. copiar o JSONL para a área de transferência.

A saída mostra os tokens reconhecidos e os erros léxicos encontrados, mantendo o fluxo de depuração do compilador.

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
- A interface gráfica facilita os testes de entrada e diagnóstico em um fluxo visual e prático.
- O JSONL acadêmico é gerado por uma camada de serialização separada, preservando o scanner pronto para o parser futuro.

## Tecnologias

- Python
- Tkinter
- uv (gerenciamento de ambiente Python)
- Git / GitHub para versionamento
