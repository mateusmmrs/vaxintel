# Fontes de dados

## Princípios

O projeto usa apenas dados reais. Nenhuma métrica final deve entrar no dataset processado sem fonte, ano de referência, URL operacional e data de extração.

## Fontes priorizadas na v2

| Fonte | Uso na v2 | Ano-base | URL operacional | Data de extração | Status |
|---|---|---:|---|---|---|
| IBGE SIDRA / PPM tabela 3939 | Efetivo bovino por UF | 2024 | https://apisidra.ibge.gov.br/values/t/3939/n3/all/v/105/p/2024/c79/2670/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Abate tabela 1092 | Bovinos abatidos por UF, agregado anual | 2024 | https://apisidra.ibge.gov.br/values/t/1092/n3/all/v/284/p/202401,202402,202403,202404/c12716/115236/c18/992/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Abate tabela 1092 | Peso total das carcaças por UF, agregado anual | 2024 | https://apisidra.ibge.gov.br/values/t/1092/n3/all/v/285/p/202401,202402,202403,202404/c12716/115236/c18/992/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Leite tabela 1086 | Leite adquirido por UF, agregado anual | 2024 | https://apisidra.ibge.gov.br/values/t/1086/n3/all/v/282/p/202401,202402,202403,202404/c12716/115236/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Pesquisa Trimestral do Leite tabela 1086 | Preço médio do leite por UF | 2024 | https://apisidra.ibge.gov.br/values/t/1086/n3/all/v/2522/p/202401,202402,202403,202404/c12716/115236/c12529/118225/f/n | 2026-04-01 | usada |
| IBGE Geociências `BR_UF_2024.zip` | Geometrias oficiais e área das UFs | 2024 | https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/Brasil/BR_UF_2024.zip | 2026-04-01 | usada |
| MAPA / gov.br | Contexto sanitário, programas oficiais e enquadramento técnico | vigente | https://www.gov.br/agricultura/pt-br/assuntos/saude-animal-e-bem-estar-animal | 2026-04-01 | contextual |

## Relação com os blocos analíticos

- `Animal Exposure Score`: rebanho bovino e densidade territorial.
- `Sanitary Pressure Score`: densidade bovina, intensidade de abate e intensidade leiteira.
- `Beef Economic Score`: bovinos abatidos e peso total de carcaças.
- `Dairy Economic Score`: leite adquirido, preço médio do leite e valor estimado da captação leiteira.

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

## Observações

- O recorte 2024 foi escolhido para harmonizar rebanho, abate e leite em um ano fechado e metodologicamente conservador.
- O bloco econômico do leite já conta com uma proxy monetária observável.
- O bloco econômico do corte ainda é mais forte em proxies físicas de escala do que em valor monetário direto por UF.
- Quando houver divergência temporal entre bases, o pipeline deve registrar a escolha metodológica no manifesto.
- Fontes secundárias só entram se explicitamente rotuladas como secundárias.
- Indicadores adicionais de MAPA e CEPEA seguem em backlog metodológico até entrarem com rastreabilidade equivalente.
