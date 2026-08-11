# MiniC em Python

Este diretório contém a implementação do compilador MiniC em Python, focada inicialmente na etapa de análise léxica.

## Objetivo

O projeto identifica e classifica os elementos do código-fonte em tokens, além de detectar erros léxicos, como:

- símbolos inválidos
- strings não fechadas
- comentários de bloco sem fechamento
- literais mal formados

## Estrutura principal

```text
src/
├── lexer/
│   ├── __init__.py
│   ├── __main__.py
│   ├── scanner.py
│   ├── token_types.py
│   ├── tokens.py
│   ├── errors.py
│   └── demo.py
├── parser/
├── semantic/
├── ast/
├── codegen/
├── ir/
├── optimizer/
└── __init__.py
```

## Como executar

No diretório do projeto Python:

```powershell
cd "C:\Users\guilherme.lima\OneDrive - Alpargatas S.A\Documentos\GitHub\Projeto_MiniC\ProjetoMiniC\Python"
uv python install 3.12
uv run python -m src.lexer
```

## O que a execução mostra

Ao rodar o módulo, o programa executa uma série de testes de validação do lexer, incluindo:

1. código válido
2. código com símbolos inválidos e string não fechada
3. código com operadores lógicos e comentário de bloco sem fechar

A saída exibirá os tokens reconhecidos e os erros léxicos encontrados.

## Módulos do lexer

- `token_types.py`: define os tipos de token da linguagem
- `tokens.py`: estrutura os objetos Token
- `errors.py`: define as exceções e mensagens de erro léxico
- `scanner.py`: percorre o código-fonte e identifica cada token
- `demo.py`: contém os testes de demonstração
- `__main__.py`: ponto de entrada para execução do módulo

## Próximos passos

- implementar o parser
- construir a árvore sintática
- validar regras semânticas
- gerar código intermediário ou final
