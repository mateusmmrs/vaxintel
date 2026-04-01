# Data Sources

## Principios

O projeto usa apenas dados reais. Nenhuma metrica final deve entrar no dataset processado sem fonte, ano de referencia, URL e data de extracao.

## Fontes priorizadas no MVP

| Fonte | Uso no MVP | Ano base | URL operacional | Data de extracao | Status |
|---|---|---:|---|---|---|
| IBGE SIDRA / PPM tabela 3939 | Efetivo bovino por UF | 2024 | https://apisidra.ibge.gov.br/values/t/3939/n3/all/v/105/p/2024/c79/2670/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Abate tabela 1092 | Bovinos abatidos por UF, agregado anual | 2024 | https://apisidra.ibge.gov.br/values/t/1092/n3/all/v/284/p/202401,202402,202403,202404/c12716/115236/c18/992/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Abate tabela 1092 | Peso total das carcacas por UF, agregado anual | 2024 | https://apisidra.ibge.gov.br/values/t/1092/n3/all/v/285/p/202401,202402,202403,202404/c12716/115236/c18/992/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Leite tabela 1086 | Leite adquirido por UF, agregado anual | 2024 | https://apisidra.ibge.gov.br/values/t/1086/n3/all/v/282/p/202401,202402,202403,202404/c12716/115236/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Leite tabela 1086 | Preco medio do leite por UF | 2024 | https://apisidra.ibge.gov.br/values/t/1086/n3/all/v/2522/p/202401,202402,202403,202404/c12716/115236/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Geociencias - BR_UF_2024.zip | Geometrias oficiais e area das UFs | 2024 | https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/Brasil/BR_UF_2024.zip | 2026-04-01 | usada |
| MAPA / gov.br | Contexto de vigilancia e relevancia sanitaria | vigente | https://www.gov.br/agricultura/pt-br/assuntos/saude-animal-e-bem-estar-animal | 2026-04-01 | contextual |

## Rastreabilidade operacional

O pipeline salva um manifesto tabular com as seguintes colunas:

- `variable`
- `description`
- `source_name`
- `source_url`
- `reference_year`
- `extraction_date`
- `file_path`
- `notes`

## Observacoes

- o recorte 2024 foi escolhido para harmonizar as tres fontes quantitativas principais em um ano fechado e conservador
- o valor monetario do bloco economico no MVP e uma estimativa parcial baseada em volume de leite e preco medio do leite
- quando houver divergencia temporal entre bases, o pipeline deve registrar a escolha metodologica no manifesto
- fontes secundarias so entram se explicitamente rotuladas como secundarias
- indicadores adicionais de MAPA e CEPEA permanecem em backlog metodologico ate entrarem com rastreabilidade equivalente
