# Data Dictionary

## Processed dataset

Arquivo: `data/processed/vaxintel_bovinos_uf.parquet`

| Campo | Definicao | Fonte principal | Ano base |
|---|---|---|---:|
| `uf` | Sigla da unidade da federacao | IBGE Geociencias | 2024 |
| `reference_year` | Ano-base harmonizado do recorte | Derivado do pipeline | 2024 |
| `bovine_herd` | Efetivo bovino por UF | IBGE SIDRA tabela 3939 | 2024 |
| `uf_area_km2` | Area territorial da UF | IBGE Geociencias `BR_UF_2024.zip` | 2024 |
| `bovine_density` | Efetivo bovino dividido pela area da UF | Derivado | 2024 |
| `bovine_slaughter` | Total anual de bovinos abatidos por UF | IBGE SIDRA tabela 1092 | 2024 |
| `carcass_weight_kg` | Peso total anual de carcacas bovinas por UF | IBGE SIDRA tabela 1092 | 2024 |
| `milk_production_liters` | Total anual de leite adquirido por UF | IBGE SIDRA tabela 1086 | 2024 |
| `estimated_milk_value_brl` | Valor anual estimado da captacao leiteira por UF | IBGE SIDRA tabela 1086 + calculo do pipeline | 2024 |
| `slaughter_intensity` | Relacao entre abate anual e rebanho bovino | Derivado | 2024 |
| `milk_intensity` | Relacao entre leite anual e rebanho bovino | Derivado | 2024 |
| `animal_exposure_score` | Score 0-100 da exposicao animal | Derivado | 2024 |
| `sanitary_pressure_score` | Score 0-100 de pressao sanitaria indireta | Derivado | 2024 |
| `economic_exposure_score` | Score 0-100 de exposicao economica | Derivado | 2024 |
| `vaccination_opportunity_index` | Indice composto final | Derivado | 2024 |

## Quarterly dataset

Arquivo: `data/processed/bovines_quarterly_uf.parquet`

| Campo | Definicao |
|---|---|
| `uf` | Sigla da UF |
| `reference_year` | Ano da observacao |
| `quarter` | Trimestre de 1 a 4 |
| `bovine_slaughter` | Bovinos abatidos no trimestre |
| `carcass_weight_kg` | Peso total de carcacas no trimestre |
| `milk_production_thousand_liters` | Leite adquirido no trimestre em mil litros |
| `milk_production_liters` | Leite adquirido no trimestre em litros |
| `milk_price_brl_per_liter` | Preco medio do leite no trimestre |
| `estimated_milk_value_brl` | Volume trimestral x preco medio trimestral |

