# Projeto MiniC

Compilador educacional para a linguagem **MiniC**, um subconjunto de C. O projeto possui implementacoes equivalentes em Python e C para o analisador lexico e o analisador sintatico, uma interface grafica em Tkinter, ferramentas de linha de comando e suites de testes para as duas implementacoes.

O objetivo do projeto e construir gradualmente um pipeline de compilacao: leitura do codigo-fonte, analise lexica, analise sintatica, construcao da AST, analise semantica, geracao de representacao intermediaria, otimizacao e geracao de codigo.

## Estado atual

| Etapa | Python | C |
|---|---|---|
| Analise lexica | Implementada | Implementada |

O scanner C escreve tokens JSONL em `stdout` e erros JSONL em `stderr`. Os modulos C principais sao:

- `C/scanner.c` e `C/scanner.h`: varredura do texto-fonte.
- `C/token.c` e `C/token.h`: estrutura dos tokens.
- `C/token_types.c` e `C/token_types.h`: tipos e palavras reservadas.
- `C/errors.c` e `C/errors.h`: erros lexicos.
- `C/util.c` e `C/util.h`: memoria, strings dinamicas e leitura de arquivos.
- `C/main.c`: CLI e serializacao JSONL do scanner.
- `C/parser.c`, `C/parser_main.c`: parser e entrada CLI do parser.
- `C/ast.c` e `C/ast.h`: nos e serializacao da AST.

O `Makefile` tambem compila os modulos C separadamente. A unidade `scanner.c` da raiz e destinada aos scripts que compilam um unico arquivo; a pasta `C/` preserva a organizacao modular usada pelo Makefile.

## Testes oficiais do professor

O pacote `testes-parser-50` possui 50 casos:

- casos 01 a 25: devem ser aceitos e produzir a AST esperada;
- casos 26 a 50: devem ser rejeitados com erro sintatico.

Cada caso possui um `codigo.c` e, nos casos validos, um `ast.esperada.txt`. O runner tambem usa `manifesto.json` para mostrar titulo e diretorio na tabela.

### Comando combinado

Executa os parsers Python e C. A tabela e exibida uma vez usando os resultados do Python; o resultado C tambem e validado e qualquer falha faz o comando terminar com codigo diferente de zero.

```bash
bash testar_parser.sh ./testes-parser-50
```

### Parser Python

```bash
bash testar_parser_python.sh ./testes-parser-50 ./parser.py
```

### Parser C

```bash
bash testar_parser_c.sh ./testes-parser-50 ./parser.c
```

Os tres comandos procuram automaticamente `casos` tanto em:

```text
testes-parser-50/casos
```

quanto na estrutura aninhada distribuida:

```text
testes-parser-50/testes-parser-50/casos
```

### Saida esperada

Os runners exibem a tabela oficial neste formato:

```text
ID | STATUS | TÍTULO | DIRETÓRIO
01 | ACEITO | Declaração inteira simples | casos/01_declara_o_inteira_simples
02 | ACEITO | Inicialização inteira | casos/02_inicializa_o_inteira
03 | ACEITO | Expressão aritmética e precedência | casos/03_express_o_aritm_tica_e_preced_ncia
04 | ACEITO | Várias declarações globais | casos/04_v_rias_declara_es_globais
05 | ACEITO | Função sem parâmetros | casos/05_fun_o_sem_par_metros
06 | ACEITO | Função com parâmetros | casos/06_fun_o_com_par_metros
07 | ACEITO | Atribuição simples | casos/07_atribui_o_simples
08 | ACEITO | If sem else | casos/08_if_sem_else
09 | ACEITO | If com else | casos/09_if_com_else
10 | ACEITO | While | casos/10_while
11 | ACEITO | Bloco aninhado | casos/11_bloco_aninhado
12 | ACEITO | Operadores relacionais | casos/12_operadores_relacionais
13 | ACEITO | Operador unário | casos/13_operador_un_rio
14 | ACEITO | Chamada sem argumentos | casos/14_chamada_sem_argumentos
15 | ACEITO | Chamada com argumentos | casos/15_chamada_com_argumentos
16 | ACEITO | Vetor com tamanho | casos/16_vetor_com_tamanho
17 | ACEITO | Indexação de vetor | casos/17_indexa_o_de_vetor
18 | ACEITO | Expressão com parênteses | casos/18_express_o_com_par_nteses
19 | ACEITO | Float e comparação | casos/19_float_e_compara_o
20 | ACEITO | Retorno vazio | casos/20_retorno_vazio
21 | ACEITO | Função com vários comandos | casos/21_fun_o_com_v_rios_comandos
22 | ACEITO | Atribuição associativa | casos/22_atribui_o_associativa
23 | ACEITO | Condicionais aninhados | casos/23_condicionais_aninhados
24 | ACEITO | Laço com expressão complexa | casos/24_la_o_com_express_o_complexa
25 | ACEITO | Programa integrado | casos/25_programa_integrado
26 | REJEITADO | Ponto e vírgula ausente em declaração | casos/26_ponto_e_v_rgula_ausente_em_declara_o
27 | REJEITADO | Ponto e vírgula ausente após expressão | casos/27_ponto_e_v_rgula_ausente_ap_s_express_o
28 | REJEITADO | Parêntese de condição ausente | casos/28_par_ntese_de_condi_o_ausente
29 | REJEITADO | Chave de bloco ausente | casos/29_chave_de_bloco_ausente
30 | REJEITADO | Chave final ausente | casos/30_chave_final_ausente
31 | REJEITADO | Parêntese final de função ausente | casos/31_par_ntese_final_de_fun_o_ausente
32 | REJEITADO | Parâmetro sem tipo | casos/32_par_metro_sem_tipo
33 | REJEITADO | Parâmetro sem identificador | casos/33_par_metro_sem_identificador
34 | REJEITADO | Vírgula extra nos parâmetros | casos/34_v_rgula_extra_nos_par_metros
35 | REJEITADO | Inicializador sem expressão | casos/35_inicializador_sem_express_o
36 | REJEITADO | Operador sem operando | casos/36_operador_sem_operando
37 | REJEITADO | Dois operadores consecutivos | casos/37_dois_operadores_consecutivos
38 | REJEITADO | Atribuição sem destino | casos/38_atribui_o_sem_destino
39 | REJEITADO | Chamada sem fechar parêntese | casos/39_chamada_sem_fechar_par_ntese
40 | REJEITADO | Vírgula sem argumento | casos/40_v_rgula_sem_argumento
41 | REJEITADO | Índice sem fechar colchete | casos/41_ndice_sem_fechar_colchete
42 | REJEITADO | Índice sem expressão | casos/42_ndice_sem_express_o
43 | REJEITADO | While sem corpo | casos/43_while_sem_corpo
44 | REJEITADO | Else sem if | casos/44_else_sem_if
45 | REJEITADO | Return sem ponto e vírgula | casos/45_return_sem_ponto_e_v_rgula
46 | REJEITADO | Tipo sem nome | casos/46_tipo_sem_nome
47 | REJEITADO | Declaração local inválida | casos/47_declara_o_local_inv_lida
48 | REJEITADO | Função sem corpo | casos/48_fun_o_sem_corpo
49 | REJEITADO | Fechamento extra | casos/49_fechamento_extra
50 | REJEITADO | Condição vazia | casos/50_condi_o_vazia

Resumo: 50/50 casos passaram.
```

O codigo de saida esperado e `0`:

```bash
echo $?
```

### Comandos usados pelo professor

Na raiz do projeto, os comandos automatizados sao exatamente:

```bash
bash testar_parser.sh ./testes-parser-50
bash testar_parser_python.sh ./testes-parser-50 ./parser.py
bash testar_parser_c.sh ./testes-parser-50 ./parser.c
```

Cada runner individual imprime o cabecalho, as 50 linhas de resultado e o resumo. O runner combinado executa Python e C, mas imprime uma unica tabela para evitar duplicacao da saida.

Qualquer AST divergente, caso valido rejeitado, caso invalido aceito, falta de ferramenta ou quantidade diferente de 50 casos retorna codigo diferente de zero.

### Runner Python direto

Tambem e possivel executar o runner diretamente:

```bash
python test_parser_50.py "C:\caminho\testes-parser-50\testes-parser-50\casos"
```

Para executar um binario C com a mesma tabela:

```bash
python test_parser_50.py "C:\caminho\testes-parser-50\testes-parser-50\casos" --native .\parser.exe
```

## Testes de regressao do projeto

Com Python:

```bash
python -m unittest discover -s tests -v
```

Com Make, quando `make` estiver disponivel:

```bash
make test-parser
```

Os testes verificam gramatica, precedencia, associatividade, declaracoes, vetores, funcoes, parametros, controle de fluxo, entrada e saida, chamadas, indexacao, erros lexicos, erros sintaticos e paridade da AST entre Python e C.

## Testes do lexer

O scanner Python pode produzir tokens e erros em JSONL:

```bash
python main.py caminho/para/arquivo.minic --jsonl
```

O scanner C pode ser compilado e executado com:

```bash
make
./C/minic_scanner caminho/para/arquivo.c --jsonl
```

Casos internos do lexer ficam em:

- `ProjetoMiniC/casos-programas-c/`: programas validos;
- `ProjetoMiniC/casos-invalidos/`: entradas com erros lexicos intencionais.

Com Make:

```bash
make test-valid
make test-invalid
make test
```

### Testes por fixtures JSONL

Os scripts `test_scanner_python.sh` e `test_scanner_c.sh` percorrem arquivos `.expected.jsonl`, executam o scanner correspondente e comparam a sequencia de tokens gerada com os fixtures. Os casos lexicos ficam principalmente em `ProjetoMiniC/casos-invalidos/` e os programas validos ficam em `ProjetoMiniC/casos-programas-c/`.

Exemplos de uso a partir da raiz:

```bash
bash test_scanner_python.sh ./scanner.py ./ProjetoMiniC
bash test_scanner_c.sh ./scanner.c ./ProjetoMiniC
```

O scanner C e compilado para um executavel temporario ou local chamado `scanner`. Os fixtures verificam tokens em JSONL; quando existe um arquivo `.errors.jsonl`, tambem verificam os diagnosticos lexicos esperados.

## Codigos de saida

| Codigo | Significado |
|---:|---|
| 0 | Analise concluida com sucesso |
| 1 | Uso incorreto ou erro de leitura |
| 2 | Erro lexico |
| 3 | Erro sintatico |

Os parsers Python e C seguem esse contrato para a CLI. A interface grafica apresenta os mesmos resultados em suas abas de AST, arvore, diagnosticos e tokens.

## Documentacao tecnica

- `ProjetoMiniC/docs/README.md`: detalhes da implementacao Python.
- `ProjetoMiniC/docs/gramatica.ebnf`: arquivo reservado para a gramatica EBNF completa; a gramatica usada pelo parser esta implementada em `src/parser/parser.py` e em `C/parser.c`.
- `ProjetoMiniC/docs/especificacao.md`: especificacao lexica executavel, regras de tokens, recuperacao e formato JSONL.
- `ProjetoMiniC/docs/arquitetura.md`: documento reservado para a arquitetura geral do compilador.
- `testes-parser-50/README.md`: formato e regras do pacote externo.
- `testes-parser-50/EXECUCAO.txt`: comandos minimos por caso.

## Limitacoes atuais

- A analise semantica ainda nao esta implementada.
- Os pacotes de IR, otimizacao e geracao de codigo ainda sao estruturas de organizacao.
- A interface grafica oferece atalhos para essas etapas, mas informa que estao em desenvolvimento.
- O projeto analisa e representa programas MiniC; ele ainda nao executa os programas nem gera um executavel final.
- O pacote de testes externos valida a AST e a rejeicao sintatica, nao a execucao do programa.

## Limpeza

Para remover objetos, executaveis e arquivos de saida gerados pelo Make:

```bash
make clean
```

Os scripts de teste usam diretorios temporarios para o executavel C e os removem ao terminar.

## Tecnologias

- Python 3.10+.
- Tkinter.
- C11.
- GCC.
- Make.
- Bash.
- JSONL para a troca de tokens e diagnosticos do lexer.
## Executando a versão em Python

Requer Python 3.10+ (o projeto usa `from __future__ import annotations`) e Tkinter instalado para a interface gráfica.

A partir da raiz do repositório:

```bash
python main.py
```

- Sem argumentos: abre o painel gráfico (Tkinter), com atalhos para cada etapa do compilador (as etapas ainda não implementadas exibem um aviso).
- Com um arquivo como argumento: roda a análise léxica em modo terminal.

```bash
python main.py caminho/para/arquivo.minic
python main.py caminho/para/arquivo.minic --tokens   # imprime só a tabela de tokens
python main.py caminho/para/arquivo.minic --errors   # imprime só os erros léxicos
python main.py caminho/para/arquivo.minic --jsonl    # imprime tokens/erros em JSONL
```

Alternativamente, é possível rodar o pacote do lexer diretamente, a partir da pasta `ProjetoMiniC`:

```bash
cd ProjetoMiniC
python -m src.lexer                                   # abre a interface gráfica do lexer
python -m src.lexer ../ProjetoMiniC/casos-invalidos/i01_simbolo_desconhecido.minic --jsonl
```

### Interface gráfica do lexer

A interface em Tkinter (`AplicacaoLexer`, em `src/lexer/__main__.py`) permite:

1. executar os testes embutidos do lexer (`demo.py`);
2. colar um trecho de código diretamente na interface e analisá-lo;
3. abrir um arquivo `.minic`, `.mc`, `.c` ou `.txt` e analisá-lo;
4. visualizar a saída formatada, os tokens em JSONL e os erros em JSONL em abas separadas, além de copiar o JSONL de tokens para a área de transferência.

## Executando a versão em C

A versão em C implementa o mesmo analisador léxico. O `Makefile`, na raiz do repositório, foi escrito para ser executado com o diretório de trabalho dentro de `C/`:

```bash
cd C
make -f ../Makefile          # compila o binário minic_scanner
./minic_scanner arquivo.c              # saída legível (tabela de tokens + diagnóstico)
./minic_scanner arquivo.c --jsonl      # saída apenas em JSONL (tokens no stdout, erros no stderr)
```

Alvos adicionais do Makefile (executados também a partir de `C/`):

```bash
make -f ../Makefile test-valid    # roda o scanner sobre os programas em casos-programas-c/
make -f ../Makefile test-invalid  # roda o scanner sobre os casos em casos-invalidos/
make -f ../Makefile test          # roda os dois conjuntos de teste
make -f ../Makefile clean         # remove binários e arquivos de saída gerados
```

## O que o lexer reconhece

- palavras reservadas, identificadores, números inteiros e reais, operadores e delimitadores;
- strings e caracteres, incluindo casos malformados;
- comentários de linha e de bloco;
- erros léxicos, como símbolos desconhecidos, comentários não terminados, strings/caracteres não terminados, números reais malformados e identificadores iniciados por dígito.

Cada token reconhecido carrega tipo, lexema, atributo (quando aplicável), linha e coluna. A saída pode ser formatada em tabela ou serializada em JSONL, seguindo o mesmo formato entre as versões Python e C.

## Casos de teste

- `ProjetoMiniC/casos-programas-c/`: programas `.c` válidos (Fibonacci, números primos, média de vetor, menu interativo, controle de temperatura), cada um com o `.expected.jsonl` correspondente.
- `ProjetoMiniC/casos-invalidos/`: trechos `.minic` com erros léxicos propositais, cada um com `.expected.jsonl` (tokens esperados) e `.errors.jsonl` (erros esperados).

## Documentação

- `ProjetoMiniC/docs/README.md`: detalhes específicos da implementação em Python.
- `ProjetoMiniC/docs/gramatica.ebnf`: gramática da linguagem MiniC.
- `ProjetoMiniC/docs/especificacao.md` e `docs/arquitetura.md`: ainda a serem preenchidos.

## Análise sintática — Etapa 2

O parser consome diretamente os `Token` produzidos pelo lexer e constrói uma
AST tipada para declarações, funções, comandos e expressões. A saída de linha
de comando é uma S-expression, por exemplo
`Program(Function(int main() Block(Return(Lit(0)))))`.

```bash
# Python (somente biblioteca padrão)
python3 parser.py codigo.c

# C (compila o parser sem substituir o scanner da Etapa 1)
make parser
./parser codigo.c

# Regressão do parser (executa as mesmas entradas em Python e C)
make test-parser
```

Para executar os 50 casos externos, informe a pasta `casos` do pacote de testes:

```powershell
python test_parser_50.py "C:\caminho\testes-parser-50\testes-parser-50\casos"
```

O runner valida a AST exata dos casos 01–25 e confirma a rejeição dos casos
26–50. Ele retorna código `0` quando todos passam e `1` quando há falhas.

Na interface principal (`python3 main.py`), o botão **Análise Sintática** abre
uma tela própria para digitar ou carregar um arquivo, executar o parser e
consultar a AST, os diagnósticos com linha/coluna e os tokens reconhecidos.

Os códigos de saída são: `0` para sucesso, `1` para uso/leitura inválidos,
`2` para erro léxico e `3` para erro sintático. A versão C usa apenas a
biblioteca padrão de C e a versão Python usa apenas a biblioteca padrão; o
`tkinter` é usado somente pelas interfaces gráficas dos analisadores léxico e
sintático.

Os testes de regressão cobrem declarações globais e locais (inclusive listas
separadas por vírgula), vetores, funções, parâmetros, controle de fluxo,
entrada/saída, chamadas, indexação, precedência e associatividade. Além de
aceitar ou rejeitar cada caso, eles verificam que as duas implementações
produzem exatamente a mesma representação textual da AST.

## Tecnologias

- Python 3 + Tkinter (interface gráfica)
- C11 (gcc, make)
- JSONL como formato de intercâmbio de tokens/erros entre as implementações e os casos de teste
