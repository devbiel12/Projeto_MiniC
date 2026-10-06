# Análise semântica do MiniC

A etapa semântica recebe uma AST válida produzida pelo parser e verifica propriedades que não podem ser decididas somente pela gramática.

## Responsabilidades

- tabela de símbolos e escopos léxicos;
- resolução de identificadores e sombreamento;
- detecção de declarações duplicadas;
- verificação de tipos `int`, `float`, `bool`, `char` e `void`;
- promoção implícita `int -> float` e `char -> int`;
- verificação de operadores e atribuições;
- vetores e índices inteiros, incluindo limites quando o índice é constante;
- chamadas de função, aridade e tipos dos argumentos;
- retornos compatíveis com a função;
- `break` e `continue` somente dentro de laços;
- análise simples de fluxo para exigir retorno em funções não `void`;
- diagnóstico de uso de função `void` como valor;
- divisão por zero quando o divisor é uma constante conhecida.

A etapa não gera código de três endereços, IR, temporários ou assembly. Esses recursos pertencem às etapas posteriores do projeto.

## Códigos de diagnóstico

| Código | Regra |
|---|---|
| SEM001 | identificador não declarado |
| SEM002 | declaração duplicada |
| SEM003 | atribuição incompatível ou destino não atribuível |
| SEM004 | operandos incompatíveis / operador inválido |
| SEM005 | condição não `bool` |
| SEM006 | índice/tamanho de vetor inválido |
| SEM007 | chamada com aridade incorreta ou não-função |
| SEM008 | argumento com tipo incompatível |
| SEM009 | retorno incompatível |
| SEM010 | `break`/`continue` fora de laço |
| SEM011 | função não `void` sem retorno garantido |
| SEM012 | função sem valor usada como expressão |

## Execução

Análise semântica pelo programa principal:

```bash
python main.py arquivo.minic --check
```

`--semantic` é um alias de `--check`.

Para visualizar também os símbolos globais:

```bash
python main.py arquivo.minic --check --symbols
```

Ou diretamente pelo módulo:

```bash
python -m ProjetoMiniC.src.semantic arquivo.minic
```

## Códigos de saída

- `0`: programa semanticamente válido;
- `1`: uso incorreto/arquivo não encontrado;
- `2`: erro léxico;
- `3`: erro sintático;
- `4`: erro semântico.

## Testes

A suíte específica da etapa semântica fica em `tests/test_semantic.py` e cobre nomes, escopos, shadowing, atribuições, conversões, operadores, vetores, chamadas, retornos, fluxo de controle e cascatas básicas.
