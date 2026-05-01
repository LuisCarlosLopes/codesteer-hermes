# Business Rules

## Escopo consolidado
- regras operacionais do módulo

## Evidências consolidadas
- request:POST /api/reports/export
- src/modules/reports/export-job.ts:10-35

## Conteúdo reconciliado
- `BR-010`: exportações acima de 10 mil linhas devem ser assíncronas
- `BR-011`: apenas usuários com papel `manager` podem baixar o arquivo final

## Itens pendentes de validação
- Nenhum

## Conflitos e gaps relacionados
- Nenhum
