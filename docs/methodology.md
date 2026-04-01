# Methodology

## Objetivo analitico

O `Vaccination Opportunity Index` foi desenhado para priorizacao territorial e estrategica. Ele indica onde a combinacao entre escala do rebanho, intensidade produtiva e exposicao economica sugere maior relevancia para estrategias preventivas. O indice nao estima cobertura vacinal, nao mede eficacia vacinal e nao deve ser interpretado como medida causal de risco de doenca.

## Unidade de analise

- especie inicial: bovinos
- granularidade inicial: UF
- horizonte inicial: corte anual mais recente com variaveis harmonizaveis

## Blocos analiticos

### 1. Animal Exposure Score

Mede o tamanho relativo da exposicao animal por UF a partir do efetivo bovino e, quando disponivel, de metricas territoriais derivadas, como densidade de rebanho.

O que mede:

- escala do rebanho bovino
- concentracao relativa do rebanho no territorio

O que nao mede:

- cobertura vacinal
- risco biologico observado

### 2. Sanitary Pressure Score

Representa pressao sanitaria indireta por meio de proxies transparentes. No MVP inicial, o score deve privilegiar variaveis com sustentacao metodologica e disponibilidade publica nacional. Exemplos:

- densidade bovina territorial
- intensidade de abate em relacao ao rebanho
- intensidade leiteira em relacao ao rebanho

O que mede:

- intensidade potencial da atividade pecuaria
- sinais indiretos de maior sensibilidade operacional e sanitaria

O que nao mede:

- incidencia ou prevalencia oficial de doenca
- evidencias causais sobre surtos

### 3. Economic Exposure Score

Representa valor economico potencialmente exposto na cadeia bovina estadual.

O que mede:

- escala produtiva
- relevancia economica observavel da cadeia bovina estadual
- valor estimado da captacao leiteira por UF
- massa fisica de abate como proxy complementar de escala economica

O que nao mede:

- rentabilidade empresarial especifica
- impacto economico causal de vacinacao
- valor total da cadeia de corte em reais no MVP base

## Normalizacao

Os componentes sao normalizados em escala `0-100` via min-max:

```text
score = 100 * (x - min(x)) / (max(x) - min(x))
```

Quando todos os valores sao identicos, o componente recebe `0.0` para evitar inferencia artificial.

## Formula do indice

```text
VOI = w_animal * animal_exposure_score
    + w_sanitary * sanitary_pressure_score
    + w_economic * economic_exposure_score
```

Pesos default do MVP:

- animal: `0.40`
- sanitary: `0.30`
- economic: `0.30`

## Governanca metodologica

Cada variavel deve registrar:

- nome da variavel
- definicao
- fonte
- ano de referencia
- URL
- data de extracao
- transformacoes aplicadas

Esses metadados sao salvos em `source_manifest.csv`.

## Limitacoes

- proxies sanitarias podem ser mais fracas que o ideal quando dados oficiais comparaveis sao limitados
- anos de referencia podem divergir entre bases e exigem harmonizacao conservadora
- variaveis economicas setoriais podem refletir producao e nao necessariamente valor agregado completo da cadeia
- no MVP bovinos, a componente monetaria observada concentra-se em leite; a cadeia de corte entra principalmente por proxies fisicas de escala

## Escolha do ano-base

O MVP adota 2024 como ano-base harmonizado para o primeiro corte bovino por UF.

Justificativa:

- a tabela 3939 da PPM disponibiliza rebanho bovino ate 2024
- as tabelas 1092 e 1086 permitem consolidacao dos quatro trimestres de 2024 por UF
- como ponto de entrega em 1 de abril de 2026, 2024 oferece um corte anual fechado e metodologicamente mais conservador para o MVP
