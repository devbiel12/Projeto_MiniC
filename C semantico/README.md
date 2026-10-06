# Suíte de testes semânticos MINIC

Contém 20 fontes `.c`: 10 casos de aceitação e 10 de rejeição semântica, além do gabarito completo em `GABARITO.md`.

## Uso

Execute os casos com o analisador semântico C pelo comando `make semantic` seguido de `./semantic "C semantico/01_promocao_numerica.c"`. O executável retorna 0 para programas aceitos e 4 para programas rejeitados semanticamente. A implementação fica em `C/semantic.c` e `C/semantic.h`; `GABARITO.md` permanece como referência dos resultados canônicos.

## Premissas

As regras semânticas seguem a apostila da Aula 15: escopo léxico com sombreamento, compatibilidade exata exceto promoção `int` para `float`, verificação de vetores, chamadas, retornos, condições booleanas e destinos atribuíveis. As fontes evitam comentários e tokens não reconhecidos pelo lexer fornecido.

## Execução da suíte C

Na raiz do projeto:

```bash
make semantic
for f in "C semantico"/*.c; do ./semantic "$f"; done
```

Os 20 casos oficiais devem resultar em 10 aceitações (código 0) e 10 rejeições semânticas (código 4).
