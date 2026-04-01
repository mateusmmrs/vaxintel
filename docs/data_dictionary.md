# Dicionário de dados

## Dataset processado

Arquivo: `data/processed/vaxintel_bovinos_uf.parquet`

| Campo | Definição | Fonte principal | Ano-base |
|---|---|---|---:|
| `uf` | Sigla da unidade da federação | IBGE Geociências | 2024 |
| `reference_year` | Ano-base harmonizado do recorte | Derivado do pipeline | 2024 |
| `bovine_herd` | Efetivo bovino por UF | IBGE SIDRA tabela 3939 | 2024 |
| `uf_area_km2` | Área territorial da UF | IBGE Geociências `BR_UF_2024.zip` | 2024 |
| `bovine_density` | Efetivo bovino dividido pela área da UF | Derivado | 2024 |
| `bovine_slaughter` | Total anual de bovinos abatidos por UF | IBGE SIDRA tabela 1092 | 2024 |
| `carcass_weight_kg` | Peso total anual de carcaças bovinas por UF | IBGE SIDRA tabela 1092 | 2024 |
| `milk_production_liters` | Total anual de leite adquirido por UF | IBGE SIDRA tabela 1086 | 2024 |
| `milk_price_brl_per_liter` | Preço médio do leite por litro | IBGE SIDRA tabela 1086 | 2024 |
| `estimated_milk_value_brl` | Valor anual estimado da captação leiteira por UF | IBGE SIDRA tabela 1086 + cálculo do pipeline | 2024 |
| `slaughter_intensity` | Relação entre abate anual e rebanho bovino | Derivado | 2024 |
| `milk_intensity` | Relação entre leite anual e rebanho bovino | Derivado | 2024 |
| `animal_exposure_score` | Score 0-100 de exposição animal | Derivado | 2024 |
| `sanitary_pressure_score` | Score 0-100 de pressão sanitária indireta | Derivado | 2024 |
| `beef_economic_score` | Score 0-100 de exposição econômica do corte | Derivado | 2024 |
| `dairy_economic_score` | Score 0-100 de exposição econômica do leite | Derivado | 2024 |
| `economic_exposure_score_combined` | Média dos scores econômicos de corte e leite | Derivado | 2024 |
| `beef_opportunity_score` | Score final do modo corte | Derivado | 2024 |
| `dairy_opportunity_score` | Score final do modo leite | Derivado | 2024 |
| `combined_vaccination_opportunity_index` | Índice final combinado | Derivado | 2024 |
| `territory_profile` | Classificação territorial: corte, leite ou misto | Derivado | 2024 |
| `combined_band` | Faixa executiva do índice combinado | Derivado | 2024 |
| `final_methodological_note` | Nota padrão de interpretação metodológica | Derivado | 2024 |

## Dataset trimestral

Arquivo: `data/processed/bovines_quarterly_uf.parquet`

| Campo | Definição |
|---|---|
| `uf` | Sigla da UF |
| `reference_year` | Ano da observação |
| `quarter` | Trimestre de 1 a 4 |
| `bovine_slaughter` | Bovinos abatidos no trimestre |
| `carcass_weight_kg` | Peso total de carcaças no trimestre |
| `milk_production_thousand_liters` | Leite adquirido no trimestre em mil litros |
| `milk_production_liters` | Leite adquirido no trimestre em litros |
| `milk_price_brl_per_liter` | Preço médio do leite no trimestre |
| `estimated_milk_value_brl` | Volume trimestral multiplicado pelo preço médio trimestral |
