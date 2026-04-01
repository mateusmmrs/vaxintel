# Metodologia

## Objetivo analítico

O VaxIntel Brasil foi desenhado como uma ferramenta de priorização territorial e estratégica para saúde animal. A v2 responde, em nível de UF, onde a combinação entre escala animal, intensidade produtiva e valor econômico exposto torna um território mais relevante para programas de vacinação bovina.

O índice:

- não estima cobertura vacinal real
- não mede eficácia vacinal
- não representa vigilância epidemiológica oficial
- não prediz surtos de forma causal

## Unidade de análise

- Espécie inicial: bovinos.
- Granularidade inicial: UF.
- Horizonte principal: ano-base harmonizado com série trimestral de apoio.
- Modos de leitura: corte, leite e combinado.

## Arquitetura analítica da v2

### 1. Animal Exposure Score

Mede a escala relativa da exposição animal bovina por UF.

Variáveis-base:

- `bovine_herd`
- `bovine_density`

O que mede:

- tamanho relativo do rebanho bovino
- concentração territorial da massa animal

O que não mede:

- cobertura vacinal
- risco biológico observado

### 2. Sanitary Pressure Score

Representa pressão sanitária indireta por meio de proxies transparentes de intensidade territorial. É um score de sensibilidade operacional e produtiva, não um score epidemiológico causal.

Variáveis-base:

- `bovine_density`
- `slaughter_intensity`
- `milk_intensity`

O que mede:

- intensidade potencial da operação bovina no território
- sinais indiretos de maior sensibilidade sanitária e preventiva

O que não mede:

- incidência ou prevalência oficial de doença
- vigilância laboratorial
- evidência causal sobre surtos

### 3. Beef Economic Score

Mede a exposição econômica relativa mais associada à cadeia de corte.

Variáveis-base:

- `bovine_slaughter`
- `carcass_weight_kg`

Lógica:

- o abate anual representa a escala física observada da cadeia de corte
- o peso total de carcaças reforça a massa produtiva efetivamente movimentada

O que mede:

- escala relativa da cadeia de corte
- relevância econômica indireta do corte por volume físico observado

O que não mede:

- preço da arroba por UF
- receita líquida da cadeia
- rentabilidade empresarial específica

### 4. Dairy Economic Score

Mede a exposição econômica relativa mais associada à cadeia de leite.

Variáveis-base:

- `milk_production_liters`
- `milk_price_brl_per_liter`
- `estimated_milk_value_brl`

Lógica:

- volume indica escala produtiva
- preço médio ajuda a diferenciar exposição econômica relativa
- valor estimado combina quantidade e preço em uma proxy monetária auditável

O que mede:

- escala e relevância econômica observável da cadeia leiteira

O que não mede:

- margem do produtor
- custo logístico
- rentabilidade industrial

## Fórmulas

### Score de corte

```text
Beef Opportunity Score
= w_animal_beef * Animal Exposure Score
+ w_sanitary_beef * Sanitary Pressure Score
+ w_beef_economic * Beef Economic Score
```

Pesos padrão:

- animal: `0,40`
- sanitário: `0,30`
- econômico: `0,30`

### Score de leite

```text
Dairy Opportunity Score
= w_animal_dairy * Animal Exposure Score
+ w_sanitary_dairy * Sanitary Pressure Score
+ w_dairy_economic * Dairy Economic Score
```

Pesos padrão:

- animal: `0,35`
- sanitário: `0,25`
- econômico: `0,40`

### Índice combinado

```text
Combined Vaccination Opportunity Index
= w_beef * Beef Opportunity Score
+ w_dairy * Dairy Opportunity Score
```

Pesos padrão:

- corte: `0,50`
- leite: `0,50`

## Justificativa dos pesos

Os pesos padrão buscam equilibrar interpretabilidade comercial e conservadorismo metodológico:

- no modo corte, o peso animal permanece alto porque escala do rebanho continua central para vacinação bovina
- no modo leite, o componente econômico recebe peso maior porque há melhor observabilidade monetária
- no modo combinado, o blend inicial é simétrico para evitar impor uma tese prévia de dominância entre corte e leite

Esses pesos não são tratados como verdade causal. Eles representam uma parametrização inicial, transparente e auditável, ajustável por ambiente.

## Normalização

Os componentes são normalizados em escala `0-100` via min-max:

```text
score = 100 * (x - min(x)) / (max(x) - min(x))
```

Quando todos os valores são idênticos, o componente recebe `0,0` para evitar inferência artificial.

## Por que o ranking não é apenas rebanho

O ranking final não replica a ordem do rebanho bovino. Uma UF pode ter grande massa animal e ainda não liderar porque:

- perde em intensidade produtiva relativa
- perde em exposição econômica observável
- aparece forte apenas em corte ou apenas em leite
- perde no equilíbrio entre os motores quando o modo combinado é usado

Isso é intencional. O produto foi desenhado para responder onde a oportunidade territorial é mais forte, e não apenas onde há mais bovinos.

## Escolha do ano-base

A v2 adota **2024** como ano-base harmonizado para o primeiro recorte bovino por UF.

Justificativa:

- a tabela 3939 da PPM já disponibiliza rebanho bovino fechado para 2024
- as tabelas 1092 e 1086 permitem consolidar os quatro trimestres de 2024 por UF
- como referência de produto em **1º de abril de 2026**, 2024 é um corte anual fechado e metodologicamente mais conservador do que misturar anos ou usar dados mais sujeitos a revisão

## Governança metodológica

Cada variável usada no pipeline deve registrar:

- nome da variável
- definição
- fonte
- ano de referência
- URL operacional
- data de extração
- transformações aplicadas

Esses metadados são salvos em `data/processed/source_manifest.csv`.

## Limitações analíticas

- o bloco sanitário usa proxies indiretas, não dados oficiais de vigilância causal
- o índice não mede cobertura vacinal observada
- o índice não mede eficácia de produto específico
- o bloco econômico do corte ainda é mais forte em proxies físicas do que em valor monetário direto por UF
- diferenças temporais entre bases exigem harmonização conservadora
- o índice deve ser lido como ferramenta de priorização estratégica, não como estimador causal de retorno vacinal
