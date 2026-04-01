# LinkedIn Post

Nas ultimas semanas, construí o `VaxIntel Brasil`, um projeto de portfolio em animal health voltado a inteligencia territorial para estrategias de vacinacao.

A ideia central foi simples de formular e dificil de executar bem: como priorizar territorios onde programas preventivos e vacinais podem ter maior relevancia estrategica quando combinamos escala animal, intensidade produtiva, proxies de pressao sanitaria e exposicao economica?

Para o MVP, optei por um recorte conservador:

- especie inicial: bovinos
- granularidade: UF
- fontes: apenas dados reais e primarios oficiais
- stack: Python, pandas, geopandas, plotly e Streamlit

O projeto integra bases do IBGE para:

- efetivo bovino por UF
- abate bovino trimestral
- captacao de leite
- preco medio do leite
- geometrias oficiais das UFs

Com isso, estruturei tres camadas analiticas:

- `Sanitary Pressure Score`
- `Economic Exposure Score`
- `Vaccination Opportunity Index`

Importante: o projeto nao estima cobertura vacinal real, nao mede eficacia de vacina e nao faz afirmacoes causais. Ele foi desenhado como ferramenta de priorizacao estrategica, com metodologia transparente e limites explicitamente documentados.

O que mais me interessou nesse trabalho foi a interseccao entre data engineering, analytics, geospatial intelligence e product thinking aplicado ao agro e a saude animal.

Proximos passos:

- expandir para aves, suinos e aquacultura
- enriquecer a camada economica com precos setoriais adicionais
- incorporar proxies sanitarias oficiais mais amplas
- explorar cortes territoriais mais finos onde a qualidade do dado permitir

Se voce atua em animal health, inteligencia comercial, vacinas veterinarias ou analytics aplicado ao agro, faz sentido conversar.

