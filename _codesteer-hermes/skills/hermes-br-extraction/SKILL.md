---
name: hermes-br-extraction
description: >
  HERMES / Business-Rules Analyst: heurísticas para extrair regras de negócio a partir de UI, DB, API,
  navegação e estrutura de código, com EARS-notation adaptada, classificação de certeza e perguntas abertas
  derivadas de evidência fraca. Use quando precisar transformar sinais dispersos em BRs rastreáveis.
---

# hermes-br-extraction

## Quando Carregar Esta Skill

Carregue esta skill quando:

- o agente ativo for o `Business-Rules Analyst`
- houver necessidade de transformar validações, constraints e fluxos em regras de negócio
- você precisar diferenciar regra confirmada de hipótese operacional

Não carregue esta skill quando:

- o trabalho for apenas UI visual, estado ou segurança sem foco em regra de domínio

## Hierarquia de Evidência

Use esta ordem de força:

1. constraint formal ou mensagem observada diretamente
2. endpoint ou contrato com precondição explícita
3. branch de navegação observável
4. repetição convergente em duas ou mais fontes
5. nomenclatura ou placeholder isolado

Se a regra vier apenas do item 5, a certeza não pode passar de `Baixa`.

## Fontes Típicas e o Que Extrair

### UI

Sinais fortes:

- mensagem de erro explícita
- estado disabled ligado a condição objetiva
- validação de campo observada

Perguntas que isso responde:

- o que é obrigatório
- quais formatos são aceitos
- quais estados impedem progressão

### Banco de Dados

Sinais fortes:

- `NOT NULL`
- `UNIQUE`
- `CHECK`
- chave estrangeira obrigatória
- enum formal

Perguntas que isso responde:

- quais combinações são proibidas
- quais campos são mandatórios
- quais estados de domínio existem

### API

Sinais fortes:

- status code de erro específico
- body com validação explícita
- auth requerida
- precondição declarada

Perguntas que isso responde:

- quem pode executar a operação
- o que precisa existir antes da chamada
- quais respostas de erro representam regra de negócio

### Navegação

Sinais fortes:

- branch de fluxo
- tela de confirmação
- stepper ou wizard

Perguntas que isso responde:

- sequência obrigatória
- condições de avanço
- resultados esperados

## Formato EARS Adaptado

Use este molde:

`BR-001: [Domínio] [Condição] -> [Ação/Restrição]`

Exemplos bons:

- `BR-014: [Checkout] Quando o endereço de entrega estiver incompleto -> o usuário não pode avançar para pagamento`
- `BR-021: [Conta] Se o e-mail já existir -> o cadastro deve falhar com erro de duplicidade`

Exemplos ruins:

- `O sistema provavelmente valida CEP`
- `Tem alguma regra de desconto`

## Heurística de Certeza

- `Alta`: uma fonte forte ou duas fontes formais convergentes
- `Média`: duas fontes médias convergentes
- `Baixa`: um único sinal parcial ou nomenclatura sugestiva

## Como Gerar Perguntas Abertas

Toda regra `Baixa` deve virar pergunta objetiva. Prefira:

- "O campo X é obrigatório em todos os casos ou apenas para perfil Y?"
- "O status Z bloqueia o fluxo ou apenas exibe aviso?"
- "A duplicidade de CPF impede criação ou solicita revisão manual?"

Evite perguntas vagas como:

- "Pode explicar melhor a regra?"

## Anti-padrões

- copiar validação técnica de formato sem conectar ao domínio
- transformar nome de botão em regra de negócio
- consolidar comentário antigo como regra atual
- unir duas regras diferentes em uma frase genérica demais
